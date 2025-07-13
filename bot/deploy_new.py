import logging
import os
import shutil
from telethon import events
from datetime import datetime
from bot.connection import active_connections
from bot.database import save_data, load_data
from bot.session_saver import SessionSaver

logger = logging.getLogger(__name__)

async def save_active_sessions():
    """Sauvegarder les sessions actives dans user_data.json"""
    try:
        # Utiliser le nouveau gestionnaire de sessions
        session_count = await SessionSaver.save_current_sessions()
        file_count = SessionSaver.backup_session_files()
        
        logger.info(f"✅ Sauvegarde complète: {session_count} sessions + {file_count} fichiers")
        return session_count > 0
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des sessions: {e}")
        return False

async def handle_deploy(event, client):
    """
    Handle deployment command - sends the complete Railway package
    Premium feature for licensed users
    """
    try:
        user_id = event.sender_id

        # Check if user has premium access
        if not await is_premium_user(user_id):
            await event.respond("❌ **Accès premium requis**\n\nCette fonctionnalité est réservée aux utilisateurs premium.\nUtilisez `/valide` pour activer votre licence.")
            return

        await event.respond("📦 **Préparation du package Render complet...**\n\n⏳ Sauvegarde des sessions actives...")

        # Sauvegarder les sessions actives avant création du package
        await save_active_sessions()

        await event.respond("📦 **Sessions sauvegardées avec succès**\n\n⏳ Création du package avec corrections PostgreSQL et Telethon...")

        # Create the Render package
        import subprocess
        result = subprocess.run(['python', 'create_render_package.py'], capture_output=True, text=True, cwd='.')
        zip_path = 'TeleFeed_Render_Complete_Deploy.zip'

        if os.path.exists(zip_path):
            # Get file size for verification
            file_size = os.path.getsize(zip_path)
            size_kb = file_size / 1024

            # Send the ZIP file
            await client.send_file(
                user_id,
                zip_path,
                caption=f"""
🌐 **Package Render.com COMPLET - {size_kb:.1f} KB**

📁 **Contenu du package :**
• Configuration Render complète (render.yaml, main_render.py)
• Corrections erreurs PostgreSQL et Telethon intégrées
• Système de communication automatique Render ↔ Replit ↔ Bot
• Session manager avec fallback JSON
• Variables d'environnement préconfigurées
• Documentation complète avec instructions

🚀 **Prêt pour déploiement Render.com**

📋 **Instructions :**
1. Décompressez le fichier ZIP
2. Uploadez sur GitHub
3. Déployez sur Render.com (Web Service)
4. Configurez les variables d'environnement
5. Recevez automatiquement la notification de succès !

✅ **Erreurs PostgreSQL et Telethon corrigées**
✅ **Communication automatique silencieuse - Pas de messages "réveil toi"**
                """,
                attributes=[],
                force_document=True
            )

            logger.info(f"Complete Render package sent to user {user_id} - Size: {size_kb:.1f} KB")

        else:
            await event.respond("❌ **Package non disponible**\n\nLe package Render n'est pas encore généré. Veuillez réessayer.")

    except Exception as e:
        logger.error(f"Error in deploy handling: {e}")
        await event.respond("❌ Erreur lors du traitement du déploiement. Veuillez réessayer.")

async def is_premium_user(user_id):
    """Check if user has premium access"""
    # For now, allow admin user
    ADMIN_ID = int(os.getenv('ADMIN_ID', '1190237801'))
    return user_id == ADMIN_ID

import shutil
import tempfile
import zipfile
from pathlib import Path

async def create_deployment_package():
    """Créer le package de déploiement complet pour Render"""
    try:
        # Sauvegarder les sessions actives avant le déploiement
        await save_active_sessions()

        # Créer le dossier temporaire
        temp_dir = "temp_deploy"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Copier les fichiers essentiels
        files_to_copy = [
            "main.py",
            "requirements.txt", 
            "runtime.txt",
            "Procfile",
            "render.yaml",
            ".env.example"
        ]

        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, temp_dir)
                logger.info(f"{file} copié")
            else:
                logger.warning(f"{file} non trouvé")

        # Sauvegarder les sessions actives avant copie
        await save_active_sessions()

        # Copier user_data.json s'il existe (maintenant avec sessions sauvegardées)
        if os.path.exists("user_data.json"):
            shutil.copy("user_data.json", temp_dir)
            logger.info("user_data.json copié avec sessions actives")

        # Copier les fichiers de session actifs
        session_files_copied = 0
        for file in os.listdir('.'):
            if file.endswith('.session') or file.endswith('.session-journal'):
                try:
                    shutil.copy(file, temp_dir)
                    session_files_copied += 1
                    logger.info(f"Fichier de session copié: {file}")
                except Exception as e:
                    logger.warning(f"Impossible de copier {file}: {e}")

        logger.info(f"📁 {session_files_copied} fichiers de session copiés")


        # Créer l'archive ZIP
        zip_file = "TeleFeed_Render_Complete_Deploy.zip"
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arc_name)

        logger.info(f"📦 Archive ZIP créée: {zip_file}")

        # Nettoyer le dossier temporaire
        shutil.rmtree(temp_dir)
        logger.info("Dossier temporaire supprimé")

        return zip_file

    except Exception as e:
        logger.error(f"Erreur lors de la création du package de déploiement: {e}")
        return None