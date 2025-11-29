from typing import List, Dict, Any, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class UserDataService:
    """Service für Verwaltung von User-Daten"""
    
    def __init__(self, data_file: str = "data/users.json"):
        self.data_file = Path(data_file)
        self.users: List[Dict[str, Any]] = []
        self.load_users()
    
    def load_users(self) -> List[Dict[str, Any]]:
        """Lädt User-Daten aus JSON-Datei"""
        try:
            if not self.data_file.exists():
                logger.warning(f"User-Datei nicht gefunden: {self.data_file}")
                return []
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
            
            logger.info(f"{len(self.users)} User erfolgreich geladen")
            return self.users
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der User-Daten: {str(e)}")
            return []
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Gibt alle User zurück"""
        return self.users
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Gibt einen User nach ID zurück"""
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_user_interests(self, user_id: int) -> List[str]:
        """Gibt alle Interessen eines Users zurück"""
        user = self.get_user_by_id(user_id)
        if user:
            return user.get("interests", []) + user.get("hobbies", [])
        return []
    
    def save_users(self) -> bool:
        """Speichert User-Daten in JSON-Datei"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            logger.info("User-Daten erfolgreich gespeichert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der User-Daten: {str(e)}")
            return False


# Singleton-Instanz
user_service = UserDataService()
