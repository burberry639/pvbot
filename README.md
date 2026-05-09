# Bot Discord de Bienvenue

Bot Discord qui accueille les nouveaux membres avec un message personnalisé et les informe des permissions d'images après avoir boosté le serveur.

## Fonctionnalités

- **Message de bienvenue** automatique pour les nouveaux membres
- **Antilink robuste** : détecte et supprime les liens (http, https, www, discord.gg, discordapp.com, etc.)
- **Timeout automatique** : 1 heure pour les utilisateurs qui envoient des liens
- **Commande +embed** : crée des embeds noirs avec support markdown
- **Système de confession** : bouton pour envoyer des confessions anonymes sous forme d'image
- **Suppression sélective** : supprime instantanément les messages texte dans un channel spécifique (pas les fichiers)
- **Mode lent automatique** : active le slow mode en cas de spam intensif (5 messages en 5 secondes)

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Créer un fichier `.env` à partir de `.env.example` :
```bash
copy .env.example .env
```

3. Ajouter votre token Discord dans le fichier `.env` :
```
DISCORD_TOKEN=votre_token_ici
```

## Obtenir le Token Discord

1. Allez sur le [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez une nouvelle application
3. Allez dans l'onglet "Bot" et créez un bot
4. Copiez le token du bot
5. Activez les intents suivants :
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

## Inviter le Bot sur votre Serveur

1. Dans le Discord Developer Portal, allez dans l'onglet "OAuth2" -> "URL Generator"
2. Sélectionnez les scopes :
   - bot
3. Sélectionnez les permissions :
   - Read Messages/View Channels
   - Send Messages
4. Copiez l'URL générée et ouvrez-la dans votre navigateur
5. Sélectionnez votre serveur et autorisez le bot

## Lancer le Bot

```bash
python bot.py
```

## Configuration

Pour changer le channel de bienvenue, modifiez la variable `welcome_channel_id` dans `bot.py` :

```python
welcome_channel_id = VOTRE_CHANNEL_ID
```

Pour changer le channel où les messages texte sont supprimés, modifiez la variable dans `bot.py` :

```python
if message.channel.id == VOTRE_CHANNEL_ID:
```

## Déploiement sur Render

1. **Créer un compte Render** : allez sur [render.com](https://render.com)

2. **Créer un nouveau service** :
   - Cliquez sur "New +"
   - Sélectionnez "Web Service"

3. **Connecter votre repository** :
   - Connectez votre compte GitHub
   - Sélectionnez votre repository

4. **Configurer le service** :
   - Name : discord-bot (ou le nom de votre choix)
   - Region : choisissez une région proche de vous
   - Branch : main (ou votre branche principale)
   - Runtime : Python
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `python bot.py`

5. **Configurer les variables d'environnement** :
   - Allez dans la section "Environment"
   - Ajoutez `DISCORD_TOKEN` avec votre token Discord
   - Cliquez sur "Save"

6. **Déployer** :
   - Cliquez sur "Create Web Service"
   - Render détectera automatiquement le render.yaml
   - Le bot sera lancé automatiquement

7. **Surveiller le bot** :
   - Allez dans l'onglet "Logs"
   - Vous pouvez voir les logs en temps réel

**Note** : Render offre un plan gratuit pour les services web, suffisant pour un bot Discord.
"# pvbot" 
