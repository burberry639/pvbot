import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import re
from PIL import Image, ImageDraw, ImageFont
import io
from collections import defaultdict
import asyncio

# Charger les variables d'environnement
load_dotenv()

# Intents requis
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Créer le bot
bot = commands.Bot(command_prefix='+', intents=intents)

# Dictionnaire pour suivre les messages de spam
message_counts = defaultdict(list)
SLOW_MODE_THRESHOLD = 5  # Nombre de messages en 5 secondes pour déclencher le slow mode
SLOW_MODE_DURATION = 60  # Durée du slow mode en secondes

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user.name}')

@bot.event
async def on_member_join(member):
    # Channel de bienvenue (remplacez par l'ID de votre channel de bienvenue)
    welcome_channel_id = 1502691425295405089
    welcome_channel = bot.get_channel(welcome_channel_id)
    
    if welcome_channel:
        # Message de bienvenue avec mention du boost pour les permissions image
        welcome_message = f"""🎉 **Bienvenue {member.mention} !** 🎉

Bienvenu(e) sur le serveur ! 
Pour envoyer des images dans ce salon, **boost le serveur** pour obtenir les permissions nécessaires.

Profite de ton séjour parmi nous ! 🚀"""
        
        await welcome_channel.send(welcome_message)

# Pattern regex pour détecter les liens (http, https, www, discord.gg, discordapp.com, etc.)
LINK_PATTERN = re.compile(
    r'(https?:\/\/[^\s]+|www\.[^\s]+|discord\.gg\/[^\s]+|discord\.com\/invite\/[^\s]+|discordapp\.com\/invite\/[^\s]+|dsc\.gg\/[^\s]+|\.gg\/[^\s]+)',
    re.IGNORECASE
)

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author.bot:
        return
    
    # Ignorer les messages des utilisateurs avec certaines permissions (optionnel)
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return
    
    # Supprimer instantanément les messages texte dans le channel spécifique (pas les fichiers)
    if message.channel.id == 1502715777491664978:
        if message.content and not message.attachments:
            try:
                await message.delete()
            except discord.Forbidden:
                print("Permission insuffisante pour supprimer le message")
            except Exception as e:
                print(f"Erreur lors de la suppression du message: {e}")
            return
    
    # Détection de spam et activation du slow mode automatique
    user_key = (message.author.id, message.channel.id)
    current_time = asyncio.get_event_loop().time()
    
    # Ajouter le timestamp du message actuel
    message_counts[user_key].append(current_time)
    
    # Nettoyer les anciens messages (plus de 5 secondes)
    message_counts[user_key] = [t for t in message_counts[user_key] if current_time - t < 5]
    
    # Vérifier si l'utilisateur spam (5 messages en 5 secondes)
    if len(message_counts[user_key]) >= SLOW_MODE_THRESHOLD:
        try:
            # Activer le slow mode (1 seconde entre les messages)
            await message.channel.edit(slowmode_delay=1)
            
            # Envoyer un message d'avertissement
            warning = await message.channel.send(
                f"🐌 **Slow mode activé** en raison de spam intensif par {message.author.mention} !",
                delete_after=10
            )
            
            # Désactiver le slow mode après 60 secondes
            await asyncio.sleep(SLOW_MODE_DURATION)
            await message.channel.edit(slowmode_delay=0)
            
            # Nettoyer le compteur de messages
            if user_key in message_counts:
                del message_counts[user_key]
                
        except discord.Forbidden:
            print("Permission insuffisante pour modifier le slow mode")
        except Exception as e:
            print(f"Erreur lors de l'activation du slow mode: {e}")
    
    # Vérifier si le message contient un lien
    if LINK_PATTERN.search(message.content):
        try:
            # Supprimer le message
            await message.delete()
            
            # Timeout l'utilisateur pendant 1 heure
            await message.author.timeout(discord.utils.utcnow() + discord.timedelta(hours=1), reason="Envoi de lien interdit")
            
            # Envoyer un message de timeout
            timeout_message = f"🔒 {message.author.mention} a été timeout pendant 1 heure pour envoi de lien !"
            await message.channel.send(timeout_message, delete_after=10)
        except discord.Forbidden:
            print("Permission insuffisante pour supprimer le message ou timeout")
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")
    
    # Traiter les commandes
    await bot.process_commands(message)

@bot.command()
async def embed(ctx, *, content):
    """Crée un embed noir avec markdown"""
    embed = discord.Embed(
        description=content,
        color=0x000000  # Noir
    )
    await ctx.send(embed=embed)

# Modal pour les confessions
class ConfessionModal(discord.ui.Modal, title='Confession Anonyme'):
    confession = discord.ui.TextInput(
        label='Ta confession',
        style=discord.TextStyle.paragraph,
        placeholder='Écris ta confession ici...',
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Générer l'image avec la confession
        image = generate_confession_image(self.confession.value)
        
        # Envoyer l'image anonymement
        file = discord.File(image, filename='confession.png')
        await interaction.response.send_message(file=file)

# Vue avec le bouton de confession
class ConfessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='📝 Faire une confession', style=discord.ButtonStyle.blurple)
    async def confession_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConfessionModal())

@bot.command()
async def confession(ctx):
    """Envoie un bouton pour faire une confession anonyme"""
    view = ConfessionView()
    await ctx.send('Clique sur le bouton pour faire une confession anonyme !', view=view)

def generate_confession_image(text):
    """Génère une image avec le texte de la confession"""
    # Créer une image noire
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Essayer d'utiliser une police, sinon utiliser la police par défaut
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Ajouter le texte (avec wrap pour les longs textes)
    margin = 50
    max_width = width - 2 * margin
    
    # Diviser le texte en lignes
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        line_text = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), line_text, font=font)
        line_width = bbox[2] - bbox[0]
        
        if line_width > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Dessiner les lignes
    y_position = margin
    for line in lines:
        draw.text((margin, y_position), line, fill=(255, 255, 255), font=font)
        y_position += 40
    
    # Sauvegarder dans un buffer
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

# Lancer le bot
bot.run(os.getenv('DISCORD_TOKEN'))
