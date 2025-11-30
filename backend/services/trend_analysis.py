from typing import List, Dict, Any
from datetime import datetime
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Service für Trendanalyse und Abfrage von Nutzerinteressen"""

    def __init__(self):
        self.trends_data: Dict[str, Any] = {}
        self.last_update: datetime | None = None
        self.trends_file = Path(__file__).parent.parent / \
            "data" / "trends_short.json"

    def _load_trends_from_file(self) -> Dict[str, Any]:
        """Lädt Trend-Daten aus der trends.json Datei"""
        try:
            with open(self.trends_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                "trends": data.get("trends", []),
                "timestamp": datetime.now().isoformat(),
                "total_categories": data.get("metadata", {}).get("total_categories", 0),
                "total_interests": data.get("metadata", {}).get("total_interests", 0)
            }
        except FileNotFoundError:
            logger.error(f"Trends file not found: {self.trends_file}")
            return {"error": "Trends file not found"}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing trends.json: {str(e)}")
            return {"error": "Invalid JSON format"}

    async def fetch_user_interests(self) -> Dict[str, Any]:
        """
        Lädt Trend-Daten aus der trends.json Datei.
        TODO: Später kann hier auch eine externe API-Integration erfolgen
        """
        try:
            trends_data = self._load_trends_from_file()

            if "error" in trends_data:
                return trends_data

            self.trends_data = trends_data
            self.last_update = datetime.now()

            logger.info(
                f"Trendanalyse erfolgreich aktualisiert: {len(trends_data.get('trends', []))} Kategorien")
            return trends_data

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
        sorted_interests = sorted(
            all_interests, key=lambda x: x["score"], reverse=True)
        return sorted_interests[:limit]


# Singleton-Instanz
trend_service = TrendAnalysisService()
