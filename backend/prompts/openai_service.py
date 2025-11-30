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
Your task is to optimize advertising image prompts for image-to-image generation with product reference.

CRITICAL RULES for FLUX.2 with Image Reference:
1. The product image is PROVIDED as reference - focus on SCENE COMPOSITION and BACKGROUND
2. Describe how to integrate the product into trending lifestyle scenes
3. Keep prompts 50-100 words (concise but descriptive)
4. Use professional product photography terminology
5. Use ONLY ONE SPECIFIC lifestyle element - keep it minimal and focused (e.g., "laptop with code editor" OR "running shoes" OR "vegan cookbook" - NOT multiple items)
6. Be SPECIFIC - use the actual interest name provided (e.g., "Machine Learning textbook" not "tech books")
7. Format: Scene Setup → ONE Specific Element → Lighting → Mood → Composition
8. Avoid describing the product itself - it's already in the reference image
9. IMPORTANT: Keep background CLEAN and MINIMAL - only ONE lifestyle prop to avoid cluttered images

Example structure: "Professional studio product photography with [product] as hero product, [ONE specific item: e.g., MacBook with Python code OR running medal OR coffee beans] subtly placed in soft focus, [lighting style], [mood], [composition]"

The reference image contains the product. Your prompt should describe a CLEAN SCENE with ONE SPECIFIC lifestyle element."""

            user_message = f"""Optimize this advertising image prompt for FLUX.2 with product image reference:

CONTEXT:
- Product: {product_description}
- Target Audience: {user_age} year old {user_occupation}
- Primary Interest: {top_interests[0] if top_interests else 'lifestyle'}
- Note: Product image is provided as reference

BASE PROMPT STRUCTURE:
{json.dumps(base_structured_prompt, indent=2)}

Create an optimized FLUX.2 prompt that:
1. Focuses on SCENE COMPOSITION around the product (already in reference image)
2. Integrates ONLY ONE lifestyle element related to the primary interest - keep it MINIMAL
3. Uses professional product photography terminology
4. Describes lighting, mood, and composition
5. Keeps background CLEAN and NOT OVERLOADED

REMEMBER: 
- Don't describe the product itself - describe the SCENE, BACKGROUND, LIGHTING, and MOOD
- Use ONLY ONE lifestyle prop in background - avoid cluttered compositions
- Keep it SIMPLE and FOCUSED on the product

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
