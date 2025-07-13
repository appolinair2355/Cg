
import logging
import json
import os
from datetime import datetime
from bot.connection import active_connections
from bot.database import save_data, load_data

logger = logging.getLogger(__name__)

class SessionSaver:
    """Gestionnaire de sauvegarde des sessions actives"""
    
    @staticmethod
    async def save_current_sessions():
        """Sauvegarder toutes les sessions actives dans user_data.json"""
        try:
            logger.info("💾 Démarrage de la sauvegarde des sessions...")
            
            # Charger les données existantes
            data = load_data()
            
            # Initialiser la section sessions si nécessaire
            if 'sessions' not in data:
                data['sessions'] = {}
            
            # Compteur de sessions sauvegardées
            session_count = 0
            
            # Parcourir toutes les connexions actives
            for user_id, connection_info in active_connections.items():
                if connection_info.get('connected', False):
                    phone = connection_info.get('phone', '')
                    session_file = connection_info.get('session_name', '')
                    
                    # Stocker les informations de session
                    data['sessions'][str(user_id)] = {
                        'phone': phone,
                        'session_file': session_file,
                        'active': True,
                        'last_saved': datetime.now().isoformat(),
                        'connection_status': 'connected'
                    }
                    
                    session_count += 1
                    logger.info(f"✅ Session sauvée: utilisateur {user_id}, téléphone {phone}")
            
            # Sauvegarder dans le fichier JSON
            save_data(data)
            
            logger.info(f"✅ Sauvegarde terminée: {session_count} sessions actives sauvegardées")
            return session_count
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des sessions: {e}")
            return 0
    
    @staticmethod
    def backup_session_files():
        """Créer une copie de sauvegarde des fichiers de session"""
        try:
            backup_count = 0
            
            # Parcourir tous les fichiers .session
            for file in os.listdir('.'):
                if file.endswith('.session') or file.endswith('.session-journal'):
                    try:
                        # Créer une copie de sauvegarde
                        backup_name = f"backup_{file}"
                        if not os.path.exists(backup_name):
                            with open(file, 'rb') as src, open(backup_name, 'wb') as dst:
                                dst.write(src.read())
                            backup_count += 1
                            logger.info(f"📄 Sauvegarde créée: {backup_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Impossible de sauvegarder {file}: {e}")
            
            logger.info(f"✅ {backup_count} fichiers de session sauvegardés")
            return backup_count
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des fichiers: {e}")
            return 0
