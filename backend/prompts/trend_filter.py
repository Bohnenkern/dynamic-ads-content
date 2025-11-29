from typing import Dict, Any, List, Optional
import logging
import os
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class TrendFilterService:
    """Service for filtering trends using LLM to ensure campaign suitability"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.filtered_trends_cache: Dict[str, List[Dict[str, Any]]] = {}

        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("Trend Filter Client initialized")
        else:
            logger.warning("OPENAI_API_KEY not set - Trend filtering disabled")

    async def filter_trends_for_campaign(
        self,
        trends: List[Dict[str, Any]],
        campaign_theme: str = "general marketing campaign",
        company_values: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filters trends to remove unsuitable content for marketing campaigns

        Args:
            trends: List of trend dictionaries with category, interests, and popularity
            campaign_theme: The theme of the marketing campaign
            company_values: Optional list of company values to consider

        Returns:
            Filtered list of suitable trends
        """
        if not self.client:
            logger.warning("No OpenAI client - returning unfiltered trends")
            return trends

        if company_values is None:
            company_values = ["family-friendly",
                              "positive", "inclusive", "safe"]

        try:
            # Prepare trends for analysis
            trends_text = "\n".join([
                f"- Category: {trend['category']}, Interests: {', '.join(trend['interests'])}, Popularity: {trend['popularity_score']}"
                for trend in trends
            ])

            system_message = """You are an expert content moderator for marketing campaigns. 
            Your task is to filter out ONLY trends that are clearly inappropriate:
            1. Violence, tragedies, disasters, or negative events
            2. Adult content, gambling, or illegal activities
            3. Highly controversial political or religious topics
            
            Be LENIENT - Keep positive and neutral trends related to:
            - Technology, smartphones, AI, gaming
            - Sports, fitness, healthy lifestyle
            - Entertainment, music, movies, concerts
            - Travel, food, dining experiences
            - Photography, art, creative hobbies
            
            Return only the trend categories and interests that are suitable for a safe, positive marketing campaign."""

            user_message = f"""
            Campaign Theme: {campaign_theme}
            Company Values: {', '.join(company_values)}
            
            Please review these trends and identify which ones are suitable for our marketing campaign:
            
            {trends_text}
            
            For each trend, respond with "KEEP" if it's suitable or "REMOVE" with a brief reason if it should be filtered out.
            Format your response as a JSON array with objects containing: category, interests (array), action ("KEEP" or "REMOVE"), reason (optional).
            """

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Filter trends based on LLM response
            filtered_trends = []
            if "trends" in result:
                for trend_decision in result["trends"]:
                    if trend_decision.get("action") == "KEEP":
                        # Find matching original trend
                        for original_trend in trends:
                            if original_trend["category"] == trend_decision["category"]:
                                filtered_trends.append(original_trend)
                                break

            # Fallback: If all trends were filtered out, keep at least safe categories
            if not filtered_trends:
                logger.warning(
                    "All trends were filtered out - applying fallback to keep safe trends")
                safe_categories = ["Technology", "Food", "Sports"]
                filtered_trends = [
                    t for t in trends if t["category"] in safe_categories]

                if not filtered_trends and trends:
                    # Last resort: keep all trends if even safe categories don't exist
                    logger.warning(
                        "No safe categories found - keeping all trends")
                    filtered_trends = trends

            logger.info(
                f"Filtered trends: {len(trends)} -> {len(filtered_trends)} suitable trends")

            # Cache filtered trends
            self.filtered_trends_cache[campaign_theme] = filtered_trends

            return filtered_trends

        except Exception as e:
            logger.error(f"Error filtering trends: {str(e)}")
            logger.warning("Returning original trends due to filtering error")
            return trends

    def get_cached_filtered_trends(self, campaign_theme: str) -> Optional[List[Dict[str, Any]]]:
        """Returns cached filtered trends for a campaign theme"""
        return self.filtered_trends_cache.get(campaign_theme)


# Singleton instance
trend_filter_service = TrendFilterService()
