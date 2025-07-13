"""
Point d'entrée principal pour le déploiement Render.com
Modifie le comportement pour Render.com au lieu de Railway/Replit
Configuration directe avec gestion d'erreur PostgreSQL améliorée
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Charger les variables d'environnement directement
load_dotenv()

# Configuration Render directe (sans config/)
API_ID = int(os.getenv('API_ID', '29177661'))
API_HASH = os.getenv('API_HASH', 'a8639172fa8d35dbfd8ea46286d349ab')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8168829272:AAEdBli_8E0Du_uHVTGLRLCN6KV7Gwox0WQ')
ADMIN_ID = int(os.getenv('ADMIN_ID', '1190237801'))

# Configuration Render
RENDER_PORT = int(os.getenv('PORT', 10000))
REPLIT_URL = os.getenv('REPLIT_URL', 'https://telefeed-bot.kouamappoloak.repl.co')

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_with_render_integration():
    """Démarrage avec intégration Render"""
    try:
        # Import des modules bot sans config/
        from telethon import TelegramClient
        from bot.handlers import start_bot_sync
        from auto_communication import AutoCommunicationSystem
        from render_keep_alive import RenderKeepAliveSystem
        from http_server import start_server_in_background
        
        print("🌐 Démarrage TeleFeed Bot sur Render.com")
        
        # Démarrer le serveur HTTP en arrière-plan pour Render (optionnel)
        try:
            start_server_in_background()
        except Exception as e:
            logger.warning(f"Serveur HTTP non démarré: {e}")
        
        # Créer le client Telegram
        client = TelegramClient('bot', API_ID, API_HASH)
        
        # Connexion avec le token du bot
        await client.start(bot_token=BOT_TOKEN)
        
        print(f"🌐 Bot Render démarré sur le port {RENDER_PORT}")
        print(f"🔗 Communication avec Replit: {REPLIT_URL}")
        
        # Démarrer le système de communication automatique
        auto_comm = AutoCommunicationSystem(client, ADMIN_ID)
        await auto_comm.start_auto_communication()
        
        # Démarrer le système Render keep-alive
        render_keep_alive = RenderKeepAliveSystem(client, ADMIN_ID)
        render_task = asyncio.create_task(render_keep_alive.start_render_keep_alive())
        
        # Notifier le déploiement réussi
        await auto_comm.notify_render_deployment_success()
        
        # Importer et démarrer tous les handlers du bot directement
        from bot.handlers import start_bot
        
        # Démarrer le bot avec tous ses handlers
        await start_bot()
        
        # Exécuter le bot
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Erreur démarrage Render: {e}")
        # En cas d'erreur, essayer de démarrer quand même
        try:
            from bot.handlers import start_bot_sync
            start_bot_sync()
        except Exception as fallback_error:
            logger.error(f"Erreur de fallback: {fallback_error}")

if __name__ == "__main__":
    # Configuration Render
    os.environ['RENDER_DEPLOYMENT'] = 'true'
    os.environ['PORT'] = str(RENDER_PORT)
    
    print("✅ Configuration Render.com activée")
    print(f"🌐 Port Render: {RENDER_PORT}")
    
    # Démarrer avec Render
    asyncio.run(start_with_render_integration())