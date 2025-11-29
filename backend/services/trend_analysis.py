from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Service für Trendanalyse und Abfrage von Nutzerinteressen"""
    
    def __init__(self):
        self.trends_data: Dict[str, Any] = {}
        self.last_update: datetime | None = None
    
    async def fetch_user_interests(self) -> Dict[str, Any]:
        """
        Holt aktuelle Interessen und Hobbies von Personen über externe API.
        TODO: Externe API-Integration implementieren
        """
        try:
            # PLATZHALTER: Hier wird später die externe API aufgerufen
            # response = await external_api_client.get_user_interests()
            
            # Temporäre Mock-Daten für Entwicklung
            mock_data = {
                "trends": [
                    {
                        "category": "Sports",
                        "interests": ["Football", "Basketball", "Running"],
                        "popularity_score": 85
                    },
                    {
                        "category": "Technology",
                        "interests": ["AI", "Smartphones", "Gaming"],
                        "popularity_score": 92
                    },
                    {
                        "category": "Travel",
                        "interests": ["Beach Holidays", "City Trips", "Adventure"],
                        "popularity_score": 78
                    },
                    {
                        "category": "Food",
                        "interests": ["Healthy Eating", "Fine Dining", "Cooking"],
                        "popularity_score": 88
                    },
                    {
                        "category": "Entertainment",
                        "interests": ["Movies", "Music", "Concerts"],
                        "popularity_score": 81
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "total_users_analyzed": 10000
            }
            
            self.trends_data = mock_data
            self.last_update = datetime.now()
            
            logger.info(f"Trendanalyse erfolgreich aktualisiert: {len(mock_data['trends'])} Kategorien")
            return mock_data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Trendanalyse: {str(e)}")
            return {"error": str(e)}
    
    def get_cached_trends(self) -> Dict[str, Any]:
        """Gibt die zuletzt abgerufenen Trends zurück"""
        if not self.trends_data:
            return {"message": "Keine Trenddaten verfügbar. Bitte initialisieren."}
        
        return {
            **self.trends_data,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }
    
    def get_trends_by_category(self, category: str) -> Dict[str, Any]:
        """Gibt Trends für eine spezifische Kategorie zurück"""
        if not self.trends_data or "trends" not in self.trends_data:
            return {"error": "Keine Trenddaten verfügbar"}
        
        for trend in self.trends_data["trends"]:
            if trend["category"].lower() == category.lower():
                return trend
        
        return {"error": f"Kategorie '{category}' nicht gefunden"}
    
    def get_top_interests(self, limit: int = 5) -> List[str]:
        """Gibt die top N Interessen über alle Kategorien zurück"""
        if not self.trends_data or "trends" not in self.trends_data:
            return []
        
        all_interests = []
        for trend in self.trends_data["trends"]:
            for interest in trend["interests"]:
                all_interests.append({
                    "interest": interest,
                    "category": trend["category"],
                    "score": trend["popularity_score"]
                })
        
        # Sortiere nach Popularity Score
        sorted_interests = sorted(all_interests, key=lambda x: x["score"], reverse=True)
        return sorted_interests[:limit]


# Singleton-Instanz
trend_service = TrendAnalysisService()
