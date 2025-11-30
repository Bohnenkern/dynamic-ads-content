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

    async def analyze_image(self, image_path: str) -> str:
        """
        Analyzes the uploaded image using GPT-4o Vision to get a detailed description
        following specific guidelines for text, placement, style, font size, and color.
        """
        if not self.client:
            return "Product image"

        try:
            import base64

            # Determine mime type
            mime_type = "image/jpeg"
            if image_path.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_path.lower().endswith(".webp"):
                mime_type = "image/webp"

            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(
                    image_file.read()).decode('utf-8')

            system_message = """You are an expert in analyzing product images for advertising.
Describe the image following these strict guidelines:
1. Use quotation marks for any visible text: "The text 'OPEN' appears in red neon letters above the door"
2. Specify placement: Where text appears relative to other elements
3. Describe style: "elegant serif typography", "bold industrial lettering", "handwritten script"
4. Font size: "large headline text", "small body copy", "medium subheading"
5. Color: Use hex codes for brand text if possible, or precise color names: "The logo text 'ACME' in color #FF5733"
6. Describe the product's key visual characteristics, perspective, and composition.
"""

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analyze this product image for use in an image generation prompt."},
                        {"type": "image_url", "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"}}
                    ]}
                ],
                max_tokens=300
            )

            analysis = response.choices[0].message.content.strip()
            logger.info(f"Image Analysis Result: {analysis[:100]}...")
            return analysis

        except Exception as e:
            logger.error(f"Error in OpenAI vision analysis: {str(e)}")
            return "Product image"

    async def optimize_image_prompt(
        self,
        product_description: str,
        user_data: Dict[str, Any],
        matched_interests: List[Dict[str, Any]],
        base_structured_prompt: Dict[str, Any],
        image_analysis: Optional[str] = None
    ) -> str:
        """
        Uses OpenAI to refine and optimize the image generation prompt
        for Black Forest Labs FLUX.2, considering user psychology and trends

        Args:
            product_description: Description of the product being advertised
            user_data: User demographic and interest data
            matched_interests: List of matched trending interests
            base_structured_prompt: Structured prompt from image_prompt_builder
            image_analysis: Optional analysis of the input image

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
            user_language = user_data.get('language', 'de')
            top_interests = [m['interest']
                             for m in matched_interests[:3]] if matched_interests else []

            system_message = """You are an expert in crafting prompts for FLUX.2 image generation by Black Forest Labs.
Your task is to optimize advertising image prompts following the structure: Subject + Action + Style + Context.

CRITICAL RULES for FLUX.2 with Image Reference:
1. The product image is PROVIDED as reference - focus on SCENE COMPOSITION and ATMOSPHERIC BACKGROUND
2. Create an immersive lifestyle environment that reflects the user interest theme
3. Keep prompts 75-125 words allowing more creative detail
4. Use professional product photography terminology
5. Translate user interests into ABSTRACT ATMOSPHERE and MOOD rather than literal objects
6. Create fuller backgrounds with depth, texture, and environmental context
7. Format: Scene Setup with Atmosphere → Environmental Details → Lighting → Mood → Composition
8. Avoid describing the product itself - it's already in the reference image
9. IMPORTANT: Create rich, immersive backgrounds that evoke the lifestyle theme without being literal

LEGAL COMPLIANCE - COPYRIGHT & TRADEMARK PROTECTION:
10. NEVER use specific brand names, trademarks, or company names (e.g., "Nike" → "athletic brand", "Apple" → "tech device", "Mercedes" → "luxury car")
11. NEVER use real person names, celebrities, or public figures (e.g., "Cristiano Ronaldo" → "male professional footballer", "Taylor Swift" → "female pop artist")
12. NEVER reference copyrighted characters, franchises, or IP (e.g., "Mario" → "video game character", "Star Wars" → "sci-fi theme")
13. Use GENERIC, DESCRIPTIVE terms instead: "premium sportswear", "high-end smartphone", "professional athlete"
14. For sports: Use role descriptions ("male footballer", "female tennis player") instead of names
15. For brands: Use category descriptions ("luxury watch brand", "sports car manufacturer") instead of names

Example structure: "Professional studio product photography with [product] as hero product, set in [atmospheric description of environment related to interest theme], [environmental textures and depth], [lighting style creating specific mood], [emotional atmosphere], [composition]"

The reference image contains the product. Your prompt should describe an ATMOSPHERIC SCENE that evokes the lifestyle theme through environment and mood rather than specific objects."""

            user_message = f"""Optimize this advertising image prompt for FLUX.2:

CONTEXT:
- Product: {product_description}
- Target Audience: {user_age} year old {user_occupation}
- TARGET LANGUAGE: {user_language}
- Interest Theme: {top_interests[0] if top_interests else 'lifestyle'}
- Note: Product image is provided as reference

BASE PROMPT STRUCTURE:
{json.dumps(base_structured_prompt, indent=2)}

Create an optimized FLUX.2 prompt that:

1. Focuses on creating an ATMOSPHERIC ENVIRONMENT that reflects the interest theme
2. Translates the interest into abstract mood, lighting, and environmental qualities
3. Creates a fuller background with depth, texture, and spatial context
4. Uses professional product photography terminology
5. Describes lighting, atmosphere, and emotional tone
6. Evokes the lifestyle theme through environment rather than literal objects
7. IMPORTANT: If the base prompt mentions using an input image, you MUST include "Use the product from the provided input image" in your output.
8. IMPORTANT: If the base prompt contains a language instruction for text, you MUST include it in your output.
9. CRITICAL: Any text found in the image analysis MUST be preserved exactly (1:1) in the generated image.
10. CRITICAL: If the target audience language ({user_language}) is different from German, translate any text to {user_language}.
11. Automatically decide and describe how the product should be actively used and staged in the scene to make it look interesting and cool for the specific user group, depending on the product.

⚠️ LEGAL COMPLIANCE - GENERALIZE PROTECTED CONTENT:
11. If the Interest Theme contains specific BRAND NAMES → Replace with generic category ("Nike shoes" → "athletic footwear", "iPhone" → "premium smartphone")
12. If the Interest Theme contains PERSON NAMES or CELEBRITIES → Replace with role description ("Cristiano Ronaldo" → "professional male footballer", "Elon Musk" → "tech entrepreneur")
13. If the Interest Theme contains COPYRIGHTED CHARACTERS/FRANCHISES → Replace with generic description ("Batman" → "superhero character", "Pokémon" → "collectible game creatures")
14. ALWAYS use neutral, generic, descriptive terms to avoid trademark and copyright violations
15. Examples: "luxury sports car" (not Ferrari), "gaming console" (not PlayStation), "streaming platform" (not Netflix)

REMEMBER: 
- Don't describe the product itself - describe the ATMOSPHERIC SCENE and ENVIRONMENT
- Create rich backgrounds with depth and texture
- Interpret interests abstractly - focus on mood and atmosphere
- Give the AI creative freedom to interpret the theme
- GENERALIZE any specific brands, persons, or protected content

OUTPUT: Only the final optimized prompt text (75-125 words), no explanations or markdown."""

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
