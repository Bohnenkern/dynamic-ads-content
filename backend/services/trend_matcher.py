from typing import List, Dict, Any
import logging
import asyncio
from services.trend_analysis import trend_service
from services.user_data import user_service
from prompts.interest_matcher import interest_matcher_service

logger = logging.getLogger(__name__)


class TrendMatcher:
    """Service für das Matching von User-Interessen mit Trends"""

    def __init__(self):
        self.user_trend_matches: Dict[int, Dict[str, Any]] = {}

    async def match_user_with_trends(self, user_id: int) -> Dict[str, Any]:
        """
        Vergleicht User-Interessen mit aktuellen Trends
        und findet intelligente Übereinstimmungen mit LLM
        """
        user = user_service.get_user_by_id(user_id)
        if not user:
            return {"error": f"User mit ID {user_id} nicht gefunden"}

        # Hole alle User-Interessen (interests + hobbies)
        user_interests_list = list(
            set(user.get("interests", []) + user.get("hobbies", [])))

        # Hole aktuelle Trends
        trends_data = trend_service.get_cached_trends()
        if "message" in trends_data or "error" in trends_data:
            return {"error": "Keine Trenddaten verfügbar"}

        # Use LLM to intelligently match interests
        matches = await interest_matcher_service.match_interests_with_llm(
            user_interests=user_interests_list,
            trend_data=trends_data.get("trends", []),
            user_name=user["name"]
        )

        result = {
            "user_id": user_id,
            "user_name": user["name"],
            "total_user_interests": len(user_interests_list),
            "matched_interests": matches,
            "match_count": len(matches),
            "match_rate": round(len(matches) / len(user_interests_list) * 100, 2) if user_interests_list else 0
        }

        # Cache das Ergebnis
        self.user_trend_matches[user_id] = result

        logger.info(
            f"User {user['name']} (ID: {user_id}): {len(matches)} Trend-Matches gefunden")
        return result

    async def match_all_users(self) -> List[Dict[str, Any]]:
        """Führt Trend-Matching für alle User durch"""
        users = user_service.get_all_users()

        # Run async matching for all users in parallel
        tasks = [self.match_user_with_trends(user["id"]) for user in users]
        results = await asyncio.gather(*tasks)

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
