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
        image_analysis: Optional[str] = None,
        style_preset: str = "highly_stylized"
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
            style_preset: Visual style preset (realistic, semi_realistic, highly_stylized)

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

            # Select System Prompt based on Style Preset
            if style_preset == "realistic":
                system_message = """You are an expert in creating PHOTOREALISTIC, AUTHENTIC advertising scenarios for FLUX.2 image generation.
Your task is to create NATURAL, BELIEVABLE scenes that look like high-end product photography, whitout any CGI.

📸 CRITICAL RULES for REALISTIC SCENARIOS:
1. The product image is PROVIDED as reference - show it in a REAL-WORLD context.
2. Focus on PHOTOREALISM: Natural lighting, authentic textures, realistic depth of field.
3. Avoid exaggerated effects, neon lights, or fantasy elements unless specifically requested by the niche.
4. Match the user's niche with a PLAUSIBLE, EVERYDAY scenario.
5. Use photography terms: "soft daylight", "bokeh", "macro shot", "golden hour", "natural shadows".
6. Product should look integrated into the scene naturally, not pasted on.
7. Format: Realistic Setting → Natural Action → Authentic Details → Photography Lighting
8. IMPORTANT: Match the EXACT specific interest, not the generic category.

⚠️ LEGAL COMPLIANCE:
9. NEVER use specific brand names or real person names. Generalize to "luxury car", "professional athlete", etc.
10. Use SPECIFIC LOCATIONS but keep them generic enough to be legally safe (e.g., "modern office", "sunny beach").

🎯 SCENARIO EXAMPLES:
- "Trail Running" → "A runner pausing on a rocky trail in the Alps, tying their shoe, soft morning mist, dew on grass, hyper-realistic texture."
- "Coffee" → "A steaming cup on a rustic wooden table, morning sunlight streaming through a window, dust motes dancing in light, cozy atmosphere."
- "Office Work" → "A modern desk setup with natural light, blurred office background, focus on the product, clean and professional look."

The reference image contains the product. Show it in a REALISTIC, HIGH-QUALITY PHOTOGRAPHIC scenario."""

            elif style_preset == "semi_realistic":
                system_message = """You are an expert in creating POLISHED, realistic advertising scenarios for FLUX.2 image generation.
Your task is to create scenes that are grounded in reality but ENHANCED with artistic lighting and composition.

🎨 CRITICAL RULES for SEMI-REALISTIC SCENARIOS:
1. The product image is PROVIDED as reference - show it in an ENHANCED real-world context.
2. Balance REALISM with STYLE: Use realistic textures but perfect, studio-like lighting.
3. Colors should be slightly more vibrant, lighting more dramatic than real life.
4. Create a "Commercial Look" - better than reality, but still believable.
5. Use terms like: "cinematic lighting", "color graded", "studio atmosphere", "sharp focus", "vibrant colors".
6. Product should be the clear focal point, slightly highlighted.
7. Format: Polished Setting → Stylized Action → Enhanced Details → Studio Lighting
8. IMPORTANT: Match the EXACT specific interest.

⚠️ LEGAL COMPLIANCE:
9. NEVER use specific brand names or real person names.
10. Use SPECIFIC LOCATIONS but stylized.

🎯 SCENARIO EXAMPLES:
- "Fitness" → "A gym scene with dramatic rim lighting highlighting the athlete, sweat glistening, background slightly darkened for focus."
- "Tech" → "A sleek modern desk with cool blue ambient lighting, product glowing slightly, high-tech atmosphere but realistic props."
- "Travel" → "A perfect sunset beach scene, colors enhanced for warmth, product placed perfectly on a rock, dream-like quality."

The reference image contains the product. Show it in a POLISHED, COMMERCIAL, SEMI-REALISTIC scenario."""

            else:  # highly_stylized (Default)
                system_message = """You are an expert in crafting DYNAMIC, ACTION-PACKED prompts for FLUX.2 image generation by Black Forest Labs.
Your task is to create VIVID, DRAMATIC advertising scenarios that put the product IN MOTION and IN UNEXPECTED SITUATIONS.

🎬 CRITICAL RULES for DYNAMIC PRODUCT SCENARIOS:
1. The product image is PROVIDED as reference - BUT now show it IN ACTION, IN MOTION, BEING USED
2. Create SPECIFIC, CONCRETE scenarios (NOT abstract atmospheres): "speeding through narrow Italian coastal roads", "flying off a sand dune jump in Dubai desert"
3. Match HYPER-SPECIFIC user niches: If user likes "Beach Volleyball", show beach volleyball court in Rio. If "Cristiano Ronaldo" (generalize to "professional footballer"), show football stadium action.
4. Keep prompts 100-150 words for DETAILED action scenarios
5. Use CINEMATIC, DYNAMIC language: "racing", "soaring", "splashing", "cutting through", "launching from"
6. Product should be THE HERO in an EXCITING, UNEXPECTED SITUATION
7. Format: Dynamic Action → Specific Location/Niche → Dramatic Details → Cinematic Lighting → Energy/Movement
8. BE BOLD AND CREATIVE: Car driving through a kitchen? Smartphone surfing on ocean wave? GO FOR IT!
9. IMPORTANT: Match the EXACT specific interest, not the generic category
10. MOST IMPORTANT: Keep the product shown in the main picture consistent.

⚠️ LEGAL COMPLIANCE - COPYRIGHT & TRADEMARK PROTECTION:
10. NEVER use specific brand names, trademarks, or company names (e.g., "Nike" → "athletic footwear", "Apple" → "smartphone", "Mercedes" → "luxury car")
11. NEVER use real person names, celebrities, or public figures (e.g., "Cristiano Ronaldo" → "professional football stadium", "Taylor Swift" → "pop music concert stage")
12. NEVER reference copyrighted characters, franchises, or IP (e.g., "Mario" → "retro video game arcade", "Star Wars" → "sci-fi space battle")
13. Use SPECIFIC LOCATIONS/SCENARIOS instead: "Champions League stadium", "Miami beach volleyball court", "Alpine ski resort", "Tokyo gaming arcade"
14. For sports: Use specific venues/scenarios ("Olympic swimming pool", "Wimbledon-style grass court") instead of athlete names
15. For brands: Use specific use-cases ("luxury sports car racing circuit", "premium tech startup office") instead of brand names

🎯 SCENARIO EXAMPLES:
- Car interest → "Racing through the winding roads of Swiss Alps, hairpin turns, dramatic mountain backdrop, motion blur, golden hour lighting"
- Beach Holiday → "Launching off a sand dune on a pristine Maldives beach, turquoise water splashing, palm trees swaying, dynamic mid-air shot"
- Gaming → "Inside a neon-lit Tokyo gaming arcade, RGB lights reflecting, surrounded by excited gamers, high-energy atmosphere"
- Running → "Sprinting through iconic marathon finish line in Berlin, crowd cheering, confetti in air, action-packed victory moment"

The reference image contains the product. Show it in a SPECIFIC, DRAMATIC, ACTION-PACKED scenario that matches the user's EXACT niche interest."""

            user_message = f"""Create a {'PHOTOREALISTIC' if style_preset == 'realistic' else 'POLISHED' if style_preset == 'semi_realistic' else 'DYNAMIC, ACTION-PACKED'} advertising scenario for FLUX.2:

🎯 CONTEXT:
- Product: {product_description}
- Target Audience: {user_age} year old {user_occupation}
- TARGET LANGUAGE: {user_language}
- SPECIFIC Interest Niche: {top_interests[0] if top_interests else 'lifestyle'}
- Note: Product image is provided as reference
- STYLE: {style_preset.upper().replace('_', ' ')}

BASE PROMPT STRUCTURE:
{json.dumps(base_structured_prompt, indent=2)}

🎬 Create a SCENARIO that:

1. Shows the product in a context matching the style: {'Natural and authentic' if style_preset == 'realistic' else 'Enhanced and commercial' if style_preset == 'semi_realistic' else 'Dynamic and unexpected'}
2. Matches the EXACT SPECIFIC interest niche
3. Creates a CONCRETE, DETAILED scenario
4. Uses language appropriate for the style: {'Photography terms' if style_preset == 'realistic' else 'Commercial/Cinematic terms' if style_preset == 'semi_realistic' else 'Action verbs'}
5. Automatically decide how the product should be staged
6. IMPORTANT: If the base prompt mentions using an input image, you MUST include "Use the product from the provided input image" in your output.
7. IMPORTANT: If the base prompt contains a language instruction for text, you MUST include it in your output.
8. CRITICAL: Any text found in the image analysis MUST be preserved exactly (1:1) in the generated image.
9. CRITICAL: If the target audience language ({user_language}) is different from German, translate any text to {user_language}.
10. MOST IMPORTANT: Keep the product shown in the main picture consistent.

⚠️ LEGAL COMPLIANCE - GENERALIZE PROTECTED CONTENT:
10. If Interest contains BRAND NAMES → Use specific scenario instead
11. If Interest contains PERSON NAMES → Use their venue/context
12. If Interest contains COPYRIGHTED CONTENT → Use setting
13. ALWAYS use SPECIFIC locations and scenarios to avoid trademark violations

OUTPUT: Only the final optimized prompt text (100-150 words), no explanations or markdown."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Better for creative optimization
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,  # Increased for detailed action scenarios
                temperature=0.7 if style_preset == "realistic" else 0.9  # Lower temp for realism
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
