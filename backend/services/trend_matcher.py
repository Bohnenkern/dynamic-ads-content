from typing import List, Dict, Any
import logging
from services.trend_analysis import trend_service
from services.user_data import user_service

logger = logging.getLogger(__name__)


class TrendMatcher:
    """Service für das Matching von User-Interessen mit Trends"""
    
    def __init__(self):
        self.user_trend_matches: Dict[int, Dict[str, Any]] = {}
    
    def match_user_with_trends(self, user_id: int) -> Dict[str, Any]:
        """
        Vergleicht User-Interessen mit aktuellen Trends
        und findet Übereinstimmungen
        """
        user = user_service.get_user_by_id(user_id)
        if not user:
            return {"error": f"User mit ID {user_id} nicht gefunden"}
        
        # Hole alle User-Interessen (interests + hobbies)
        user_interests = set(user.get("interests", []) + user.get("hobbies", []))
        
        # Hole aktuelle Trends
        trends_data = trend_service.get_cached_trends()
        if "message" in trends_data or "error" in trends_data:
            return {"error": "Keine Trenddaten verfügbar"}
        
        # Sammle alle Trend-Interessen
        trend_interests = set()
        trend_categories = {}
        
        for trend in trends_data.get("trends", []):
            category = trend["category"]
            for interest in trend["interests"]:
                trend_interests.add(interest)
                trend_categories[interest] = {
                    "category": category,
                    "popularity_score": trend["popularity_score"]
                }
        
        # Finde Übereinstimmungen (case-insensitive)
        matches = []
        for user_interest in user_interests:
            for trend_interest in trend_interests:
                if user_interest.lower() == trend_interest.lower():
                    matches.append({
                        "interest": trend_interest,
                        "category": trend_categories[trend_interest]["category"],
                        "popularity_score": trend_categories[trend_interest]["popularity_score"]
                    })
        
        result = {
            "user_id": user_id,
            "user_name": user["name"],
            "total_user_interests": len(user_interests),
            "matched_interests": matches,
            "match_count": len(matches),
            "match_rate": round(len(matches) / len(user_interests) * 100, 2) if user_interests else 0
        }
        
        # Cache das Ergebnis
        self.user_trend_matches[user_id] = result
        
        logger.info(f"User {user['name']} (ID: {user_id}): {len(matches)} Trend-Matches gefunden")
        return result
    
    def match_all_users(self) -> List[Dict[str, Any]]:
        """Führt Trend-Matching für alle User durch"""
        users = user_service.get_all_users()
        results = []
        
        for user in users:
            match_result = self.match_user_with_trends(user["id"])
            results.append(match_result)
        
        logger.info(f"Trend-Matching für {len(users)} User abgeschlossen")
        return results
    
    def get_cached_match(self, user_id: int) -> Dict[str, Any]:
        """Gibt gecachtes Match-Ergebnis zurück"""
        if user_id not in self.user_trend_matches:
            return {"error": "Kein gecachtes Match-Ergebnis vorhanden"}
        return self.user_trend_matches[user_id]
    
    def get_all_cached_matches(self) -> Dict[int, Dict[str, Any]]:
        """Gibt alle gecachten Match-Ergebnisse zurück"""
        return self.user_trend_matches


# Singleton-Instanz
trend_matcher = TrendMatcher()
