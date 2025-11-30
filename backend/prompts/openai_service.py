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

            user_message = f"""Create a DYNAMIC, ACTION-PACKED advertising scenario for FLUX.2:

🎯 CONTEXT:
- Product: {product_description}
- Target Audience: {user_age} year old {user_occupation}
- TARGET LANGUAGE: {user_language}
- SPECIFIC Interest Niche: {top_interests[0] if top_interests else 'lifestyle'}
- Note: Product image is provided as reference

BASE PROMPT STRUCTURE:
{json.dumps(base_structured_prompt, indent=2)}

🎬 Create a DRAMATIC, SPECIFIC scenario that:

1. Shows the product IN MOTION or IN ACTION (not static!)
2. Matches the EXACT SPECIFIC interest niche (e.g., "Beach Volleyball" → Rio beach volleyball court, "Machine Learning" → high-tech AI research lab)
3. Creates a CONCRETE, DETAILED scenario with specific location/situation
4. Uses DYNAMIC, CINEMATIC language: "racing", "flying", "splashing", "cutting through"
5. Includes UNEXPECTED, CREATIVE scenarios (car in kitchen? smartphone surfing? BE BOLD!)
6. Describes dramatic lighting, motion blur, action details
7. Automatically decide how the product should be ACTIVELY USED in the scene to make it look exciting and cool for this specific user niche
8. IMPORTANT: If the base prompt mentions using an input image, you MUST include "Use the product from the provided input image" in your output.
9. IMPORTANT: If the base prompt contains a language instruction for text, you MUST include it in your output.
10. CRITICAL: Any text found in the image analysis MUST be preserved exactly (1:1) in the generated image.
11. CRITICAL: If the target audience language ({user_language}) is different from German, translate any text to {user_language}.

⚠️ LEGAL COMPLIANCE - GENERALIZE PROTECTED CONTENT:
12. If Interest contains BRAND NAMES → Use specific scenario instead ("Nike" → "Olympic athletics track", "iPhone" → "Silicon Valley tech office")
13. If Interest contains PERSON NAMES → Use their venue/context ("Cristiano Ronaldo" → "Champions League football stadium", "Taylor Swift" → "sold-out arena concert stage")
14. If Interest contains COPYRIGHTED CONTENT → Use setting ("Mario" → "retro 8-bit arcade game room", "Star Wars" → "futuristic space station cockpit")
15. ALWAYS use SPECIFIC, VIVID locations and scenarios to avoid trademark violations
16. Examples: "Formula 1 racing circuit" (not Ferrari), "Tokyo gaming arcade" (not PlayStation), "streaming service watch party" (not Netflix)

🎯 SCENARIO EXAMPLES by Interest:
- "Trail Running" → "Sprinting down a rugged alpine trail in Swiss mountains, mud splashing, pine trees blurring past, sunrise golden light"
- "Beach Volleyball" → "Diving for a spike on Copacabana beach court, sand flying, Rio sunset backdrop, dynamic mid-air action"
- "Machine Learning" → "Racing through a neon-lit AI research lab, holographic code projections, futuristic server racks, electric blue lighting"
- "Fine Dining" → "Flying through a Michelin-star restaurant kitchen mid-service, flames from stove, chefs in motion, dramatic spotlighting"

REMEMBER:
- Product must be IN ACTION, not static
- Match the EXACT specific interest, not generic category
- Be CREATIVE and DRAMATIC - unexpected scenarios are encouraged!
- Use SPECIFIC locations and vivid details
- GENERALIZE any brands/persons but keep scenarios SPECIFIC and EXCITING

OUTPUT: Only the final optimized prompt text (100-150 words), no explanations or markdown."""

            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Better for creative optimization
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,  # Increased for detailed action scenarios
                temperature=0.9  # Higher for maximum creativity and drama
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
