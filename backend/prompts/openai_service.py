from typing import Dict, Any, List, Optional
import logging
import os
import json
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for optimizing image generation prompts using LLM intelligence"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.optimized_prompts: Dict[int, str] = {}

        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI Image Prompt Optimizer initialized")
        else:
            logger.warning(
                "OPENAI_API_KEY not set - Falling back to rule-based prompts")

    async def optimize_image_prompt(
        self,
        product_description: str,
        user_data: Dict[str, Any],
        matched_interests: List[Dict[str, Any]],
        base_structured_prompt: Dict[str, Any]
    ) -> str:
        """
        Uses OpenAI to refine and optimize the image generation prompt
        for Black Forest Labs FLUX.2, considering user psychology and trends

        Args:
            product_description: Description of the product being advertised
            user_data: User demographic and interest data
            matched_interests: List of matched trending interests
            base_structured_prompt: Structured prompt from image_prompt_builder

        Returns:
            Optimized text prompt for FLUX.2 image generation
        """
        if not self.client:
            # Fallback: Use rule-based conversion
            return self._generate_fallback_prompt(base_structured_prompt)

        try:
            # Extract key information
            user_age = user_data.get('age', 30)
            user_occupation = user_data['demographics'].get(
                'occupation', 'Professional')
            top_interests = [m['interest']
                             for m in matched_interests[:3]] if matched_interests else []

            system_message = """You are an expert in crafting prompts for FLUX.2 image generation by Black Forest Labs.
Your task is to optimize advertising image prompts following the structure: Subject + Action + Style + Context.

CRITICAL RULES for FLUX.2:
1. Word order matters - most important elements FIRST
2. Keep prompts 50-100 words (concise but descriptive)
3. Use commercial photography terminology
4. Integrate trending interests SUBTLY in background/mood/setting
5. Focus on product as hero, trends enhance atmosphere
6. Avoid overloading - quality over quantity

Format: Subject (product), Action (display), Style (photography type), Context (setting, lighting, mood)"""

            user_message = f"""Optimize this advertising image prompt for FLUX.2:

PRODUCT: {product_description}
TARGET AUDIENCE: {user_age} year old {user_occupation}
TRENDING INTERESTS: {', '.join(top_interests)}

BASE PROMPT STRUCTURE:
{json.dumps(base_structured_prompt, indent=2)}

Create an optimized FLUX.2 prompt that:
1. Showcases the product prominently (hero element)
2. Subtly integrates trending interests in background/atmosphere
3. Appeals to target demographic emotionally
4. Uses professional photography language
5. Follows Subject → Action → Style → Context structure
6. IMPORTANT: If the base prompt mentions using an input image, you MUST include "Use the product from the provided input image" in your output.
7. IMPORTANT: If the base prompt contains a language instruction for text, you MUST include it in your output.

OUTPUT: Only the final optimized prompt text (50-100 words), no explanations or markdown."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Better for creative optimization
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=250,
                temperature=0.8  # Higher for creativity
            )

            optimized_prompt = response.choices[0].message.content.strip()

            # Remove markdown formatting if present
            optimized_prompt = optimized_prompt.replace('```', '').strip()

            # Cache the optimized prompt
            self.optimized_prompts[user_data['id']] = optimized_prompt

            logger.info(
                f"Optimized image prompt for User {user_data.get('name')} (ID: {user_data['id']})")
            logger.info(f"Prompt: {optimized_prompt[:100]}...")

            return optimized_prompt

        except Exception as e:
            logger.error(f"Error in OpenAI prompt optimization: {str(e)}")
            logger.warning("Falling back to rule-based prompt generation")
            return self._generate_fallback_prompt(base_structured_prompt)

    def _generate_fallback_prompt(self, structured_prompt: Dict[str, Any]) -> str:
        """
        Generates fallback prompt without OpenAI (rule-based conversion)
        Following: Subject + Action + Style + Context
        """
        # Extract main subject
        subjects = structured_prompt.get('subjects', [])
        if subjects:
            subject = subjects[0]['description']
            action = subjects[0].get('pose', 'displayed prominently')
        else:
            subject = "product"
            action = "displayed prominently"

        # Extract style and context
        style = structured_prompt.get('style', 'professional photography')
        scene = structured_prompt.get('scene', 'studio setup')
        background = structured_prompt.get('background', 'clean backdrop')
        lighting = structured_prompt.get('lighting', 'professional lighting')
        mood = structured_prompt.get('mood', 'clean and professional')

        # Get color palette
        colors = structured_prompt.get('color_palette', [])
        color_text = f"with {', '.join(colors[:3])} color palette" if colors else ""

        # Build prompt following FLUX.2 guidelines
        # Priority: Subject → Action → Style → Context
        prompt_parts = [
            f"{subject}, {action}",
            f"{style}",
            f"{scene}, {background}",
            f"{lighting}, {mood}",
            color_text
        ]

        # Join and clean up
        final_prompt = ", ".join([p for p in prompt_parts if p and p.strip()])

        return final_prompt

    async def optimize_prompts_for_all_users(
        self,
        product_description: str,
        structured_prompts: Dict[int, Dict[str, Any]],
        user_matches: Dict[int, Dict[str, Any]]
    ) -> Dict[int, str]:
        """
        Optimizes image prompts for multiple users

        Args:
            product_description: Product being advertised
            structured_prompts: Dict of user_id -> structured_prompt
            user_matches: Dict of user_id -> match_result with user_data and interests

        Returns:
            Dict of user_id -> optimized_prompt_text
        """
        from services.user_data import user_service

        results = {}

        for user_id, structured_prompt in structured_prompts.items():
            match_data = user_matches.get(user_id)
            if not match_data:
                continue

            user_data = user_service.get_user_by_id(user_id)
            if not user_data:
                continue

            matched_interests = match_data.get("matched_interests", [])

            optimized_prompt = await self.optimize_image_prompt(
                product_description=product_description,
                user_data=user_data,
                matched_interests=matched_interests,
                base_structured_prompt=structured_prompt
            )

            results[user_id] = optimized_prompt

        logger.info(f"Optimized image prompts for {len(results)} users")
        return results

    def get_cached_prompt(self, user_id: int) -> Optional[str]:
        """Returns cached optimized prompt"""
        return self.optimized_prompts.get(user_id)

    def get_all_cached_prompts(self) -> Dict[int, str]:
        """Returns all cached optimized prompts"""
        return self.optimized_prompts


# Singleton instance
openai_service = OpenAIService()
