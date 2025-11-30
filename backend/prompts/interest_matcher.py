from typing import Dict, Any, List, Optional
import logging
import os
import json
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class InterestMatcherService:
    """Service for intelligent matching of user interests with trend interests using LLM"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.match_cache: Dict[str, List[Dict[str, Any]]] = {}

        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("Interest Matcher Client initialized")
        else:
            logger.warning(
                "OPENAI_API_KEY not set - Falling back to exact matching")

    async def match_interests_with_llm(
        self,
        user_interests: List[str],
        trend_data: List[Dict[str, Any]],
        user_name: str = "User"
    ) -> List[Dict[str, Any]]:
        """
        Uses LLM to intelligently match user interests with trend interests.
        Returns specific sub-categories (e.g., "Football" instead of "Sports").

        Args:
            user_interests: List of user's interests and hobbies
            trend_data: List of trend categories with their interests
            user_name: Name of the user for logging

        Returns:
            List of matched interests with specific sub-categories
        """
        if not self.client:
            logger.warning("No OpenAI client - falling back to exact matching")
            return self._fallback_exact_matching(user_interests, trend_data)

        try:
            # Build trend information for LLM
            trends_text = ""
            for trend in trend_data:
                category = trend["category"]
                interests = ", ".join(trend["interests"])
                trends_text += f"Category: {category}\nInterests: {interests}\n\n"

            user_interests_text = ", ".join(user_interests)

            system_message = """You are an expert at matching user interests with trending topics.
Your task is to find intelligent matches between user interests and available trend interests.

IMPORTANT RULES:
1. Match semantically similar interests (e.g., "Marathon Training" matches "Running")
2. Match broader interests to specific ones (e.g., "Gaming" matches "Video Gaming", "PC Gaming", etc.)
3. Match related concepts (e.g., "Cooking" matches "Baking", "Meal Prep", "Recipe", etc.)
4. Return the SPECIFIC trend interest, NOT the general category (e.g., "Football", not "Sports")
5. Only include confident matches (relevance > 80%)
6. One user interest can match multiple trend interests if relevant

FORMAT: Return JSON with array of matches, each containing:
- user_interest: original user interest
- matched_trend_interest: specific trend interest name
- category: trend category
- relevance_score: 0-100 (how confident the match is)
- reasoning: brief explanation why they match"""

            user_message = f"""User Profile: {user_name}
User Interests: {user_interests_text}

Available Trends:
{trends_text}

Find all relevant matches between the user's interests and the trend interests.
Return ONLY the JSON object, no additional text."""

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            matches = result.get("matches", [])

            # Build structured match results with popularity scores
            structured_matches = []
            for match in matches:
                # Find the original trend to get popularity score
                matched_category = match.get("category")
                trend_interest = match.get("matched_trend_interest")

                popularity_score = 80  # Default
                for trend in trend_data:
                    if trend["category"] == matched_category:
                        popularity_score = trend["popularity_score"]
                        break

                structured_matches.append({
                    "user_interest": match.get("user_interest"),
                    "interest": trend_interest,
                    "trend": trend_interest,
                    "category": matched_category,
                    "score": match.get("relevance_score", 85),
                    "popularity_score": popularity_score,
                    "reasoning": match.get("reasoning", "")
                })

            logger.info(
                f"LLM matched {len(structured_matches)} interests for {user_name}")

            # Cache results
            cache_key = f"{user_name}_{hash(tuple(user_interests))}"
            self.match_cache[cache_key] = structured_matches

            return structured_matches

        except Exception as e:
            logger.error(f"Error in LLM interest matching: {str(e)}")
            logger.warning("Falling back to exact matching")
            return self._fallback_exact_matching(user_interests, trend_data)

    def _fallback_exact_matching(
        self,
        user_interests: List[str],
        trend_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fallback method for exact case-insensitive matching
        when LLM is not available
        """
        matches = []

        # Build lookup dict for trend interests
        trend_lookup = {}
        for trend in trend_data:
            category = trend["category"]
            popularity = trend["popularity_score"]
            for interest in trend["interests"]:
                trend_lookup[interest.lower()] = {
                    "interest": interest,
                    "category": category,
                    "popularity_score": popularity
                }

        # Find exact matches (case-insensitive)
        for user_interest in user_interests:
            user_lower = user_interest.lower()
            if user_lower in trend_lookup:
                trend_info = trend_lookup[user_lower]
                matches.append({
                    "user_interest": user_interest,
                    "interest": trend_info["interest"],
                    "trend": trend_info["interest"],
                    "category": trend_info["category"],
                    "score": 100,  # Exact match
                    "popularity_score": trend_info["popularity_score"],
                    "reasoning": "Exact match"
                })

        logger.info(f"Fallback exact matching found {len(matches)} matches")
        return matches


# Singleton instance
interest_matcher_service = InterestMatcherService()
