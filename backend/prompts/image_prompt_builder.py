from typing import Dict, Any, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class ImagePromptBuilder:
    """Service for building structured prompts for Black Forest Labs image generation"""

    def __init__(self):
        self.prompt_cache: Dict[int, Dict[str, Any]] = {}

    def build_prompt_for_trend(
        self,
        product_description: str,
        trend_category: str,
        trend_interests: List[str],
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds a structured prompt for a specific trend category following Black Forest best practices.
        The product image will be provided as reference, so prompts focus on scene composition.

        Args:
            product_description: Description of the product being advertised
            trend_category: The trend category (e.g., "Technology & AI", "Sports & Fitness")
            trend_interests: List of SPECIFIC interests in this trend (e.g., ["Machine Learning", "Deep Learning"] not just category)
            additional_context: Optional additional context

        Returns:
            Structured prompt dictionary following Black Forest guidelines
        """
        mood = self._determine_mood_for_category(trend_category)
        color_palette = self._generate_color_palette_for_category(
            trend_category)
        background = self._generate_background_for_category(
            trend_category, trend_interests)

        # Build lifestyle elements based on SINGLE MOST RELEVANT interest (not multiple)
        lifestyle_elements = self._generate_lifestyle_elements_for_trend(
            trend_category, trend_interests[:1]
        )

        structured_prompt = {
            "scene": f"Professional studio product photography setup with polished surface, {lifestyle_elements}",
            "subjects": [
                {
                    "description": f"{product_description} as hero product",
                    "pose": "Stationary on surface",
                    "position": "Center foreground on polished surface",
                    "color_palette": color_palette[:2]
                }
            ],
            "context": {
                "trend_category": trend_category,
                "primary_interest": trend_interests[0] if trend_interests else trend_category,
                "lifestyle_theme": f"Create atmospheric environment inspired by {trend_interests[0] if trend_interests else trend_category} lifestyle with immersive background depth and thematic mood"
            },
            "style": "Ultra-realistic product photography with commercial quality",
            "color_palette": color_palette,
            "lighting": "Three-point softbox setup creating soft, diffused highlights with no harsh shadows",
            "mood": mood,
            "background": background,
            "composition": "rule of thirds with clear focus on product",
            "camera": {
                "angle": "slightly elevated angle for premium feel",
                "distance": "medium shot emphasizing product",
                "focus": "Sharp focus on product details with subtle depth of field on background",
                "lens-mm": 85,
                "f-number": "f/4.0",
                "ISO": 200
            }
        }

        if additional_context:
            structured_prompt["additional_details"] = additional_context

        logger.info(
            f"Built structured prompt for trend category: {trend_category}")
        return structured_prompt

    def build_structured_prompt(
        self,
        product_description: str,
        user_data: Dict[str, Any],
        matched_interests: List[Dict[str, Any]],
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds a structured JSON prompt for Black Forest Labs API

        Args:
            product_description: Description of the product being advertised
            user_data: User demographic and interest data
            matched_interests: List of matched trending interests
            additional_context: Optional additional context for the scene

        Returns:
            Structured prompt dictionary following Black Forest guidelines
        """
        # Extract key information
        user_name = user_data.get('name', 'User')
        user_age = user_data.get('age', 30)
        user_occupation = user_data['demographics'].get(
            'occupation', 'Professional')
        user_location = user_data.get('location', 'City')
        user_language = user_data.get('language')

        # Get top 3 trending interests
        top_interests = [m['interest']
                         for m in matched_interests[:3]] if matched_interests else []
        trend_categories = list(
            set([m['category'] for m in matched_interests[:3]])) if matched_interests else []

        # Build mood and style based on interests and demographics
        mood = self._determine_mood(matched_interests, user_data)
        style = self._determine_visual_style(user_age, user_occupation)
        color_palette = self._generate_color_palette(matched_interests)

        # Build the structured prompt
        structured_prompt = {
            "scene": f"Professional advertising photography setup with {product_description} as the hero product",
            "subjects": [
                {
                    "description": product_description,
                    "pose": "Prominently displayed with appealing presentation",
                    "position": "Center foreground on clean surface",
                    "color_palette": color_palette[:2]
                }
            ],
            "context": {
                "target_audience": f"{user_age} year old {user_occupation} from {user_location}",
                "trending_interests": top_interests,
                "trend_categories": trend_categories,
                "lifestyle_integration": self._generate_lifestyle_context(matched_interests, user_data),
                "language_instruction": f"If the uploaded image contains any text or should include any, it should be translated/added in {user_language}"
            },
            "style": f"{style}, ultra-realistic advertising photography with commercial quality",
            "color_palette": color_palette,
            "lighting": "Three-point softbox setup creating soft, diffused highlights with no harsh shadows, professional studio lighting",
            "mood": mood,
            "background": self._generate_background(matched_interests, user_data),
            "composition": "rule of thirds with clear focus on product",
            "camera": {
                "angle": "slightly elevated angle for premium feel",
                "distance": "medium shot emphasizing product",
                "focus": "Sharp focus on main product with subtle depth of field",
                "lens-mm": 85,
                "f-number": "f/4.0",
                "ISO": 200
            }
        }

        if additional_context:
            structured_prompt["additional_details"] = additional_context

        # Cache the prompt
        self.prompt_cache[user_data['id']] = structured_prompt

        logger.info(
            f"Built structured image prompt for user {user_name} (ID: {user_data['id']})")

        return structured_prompt

    def _determine_mood(
        self,
        matched_interests: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> str:
        """Determines the mood based on user interests and demographics"""
        if not matched_interests:
            return "Clean, professional, aspirational"

        categories = [m['category'] for m in matched_interests]

        # Map categories to moods
        if 'Technology & Innovation' in categories:
            return "Sleek, modern, innovative, tech-forward"
        elif 'Sports & Fitness' in categories:
            return "Energetic, dynamic, active, motivating"
        elif 'Food & Dining' in categories:
            return "Warm, inviting, appetizing, gourmet"
        elif 'Travel & Adventure' in categories:
            return "Adventurous, exciting, wanderlust, aspirational"
        elif 'Entertainment & Culture' in categories:
            return "Vibrant, engaging, culturally rich, entertaining"
        else:
            return "Clean, professional, lifestyle-oriented, aspirational"

    def _determine_visual_style(self, age: int, occupation: str) -> str:
        """Determines visual style based on demographics"""
        if age < 30:
            return "Contemporary, bold, social media ready"
        elif age < 45:
            return "Modern, sophisticated, professional"
        else:
            return "Classic, refined, premium quality"

    def _generate_color_palette(self, matched_interests: List[Dict[str, Any]]) -> List[str]:
        """Generates color palette based on trending interests"""
        if not matched_interests:
            return ["clean white", "soft gray", "muted blue", "warm beige"]

        categories = [m['category'] for m in matched_interests]

        # Map categories to color palettes
        if 'Technology & Innovation' in categories:
            return ["sleek black", "metallic silver", "electric blue", "pure white"]
        elif 'Sports & Fitness' in categories:
            return ["vibrant red", "energetic orange", "fresh green", "deep blue"]
        elif 'Food & Dining' in categories:
            return ["warm brown", "rich red", "fresh green", "golden yellow"]
        elif 'Travel & Adventure' in categories:
            return ["sky blue", "sunset orange", "earth brown", "ocean teal"]
        elif 'Entertainment & Culture' in categories:
            return ["vibrant purple", "bold red", "golden yellow", "deep blue"]
        else:
            return ["sophisticated navy", "warm beige", "soft white", "accent gold"]

    def _generate_background(
        self,
        matched_interests: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> str:
        """Generates background description based on user context"""
        if not matched_interests:
            return "Clean studio backdrop with neutral gradient"

        categories = [m['category'] for m in matched_interests]
        interests = [m['interest'] for m in matched_interests[:3]]

        # Create contextual background
        if 'Technology & Innovation' in categories or 'AI' in interests:
            return "Modern minimalist space with subtle tech elements, clean lines, futuristic ambiance"
        elif 'Sports & Fitness' in categories or 'Running' in interests:
            return "Active lifestyle setting with subtle athletic elements, energetic atmosphere"
        elif 'Food & Dining' in categories:
            return "Elegant dining atmosphere with subtle gourmet elements, warm ambiance"
        elif 'Travel & Adventure' in categories:
            return "Sophisticated travel-inspired setting with subtle adventure elements"
        else:
            return "Professional lifestyle setting with clean, aspirational atmosphere"

    def _determine_mood_for_category(self, category: str) -> str:
        """Determines mood based on trend category"""
        mood_map = {
            "Technology": "Sleek, modern, innovative, tech-forward",
            "Sports": "Energetic, dynamic, active, motivating",
            "Food": "Warm, inviting, appetizing, gourmet",
            "Travel": "Adventurous, exciting, wanderlust, aspirational",
            "Entertainment": "Vibrant, engaging, culturally rich, entertaining"
        }
        return mood_map.get(category, "Clean, professional, lifestyle-oriented, aspirational")

    def _generate_color_palette_for_category(self, category: str) -> List[str]:
        """Generates color palette based on trend category"""
        palette_map = {
            "Technology": ["sleek black", "metallic silver", "electric blue", "pure white"],
            "Sports": ["vibrant red", "energetic orange", "fresh green", "deep blue"],
            "Food": ["warm brown", "rich red", "fresh green", "golden yellow"],
            "Travel": ["sky blue", "sunset orange", "earth brown", "ocean teal"],
            "Entertainment": ["vibrant purple", "bold red", "golden yellow", "deep blue"]
        }
        return palette_map.get(category, ["sophisticated navy", "warm beige", "soft white", "accent gold"])

    def _generate_background_for_category(self, category: str, interests: List[str]) -> str:
        """Generates background description for trend category"""
        background_map = {
            "Technology": "Modern minimalist space with subtle tech elements, clean lines, futuristic ambiance",
            "Sports": "Active lifestyle setting with subtle athletic elements, energetic atmosphere",
            "Food": "Elegant dining atmosphere with subtle gourmet elements, warm ambiance",
            "Travel": "Sophisticated travel-inspired setting with subtle adventure elements",
            "Entertainment": "Vibrant cultural setting with entertainment-themed accents",
            "Gaming": "Modern gaming setup with subtle gaming peripherals in soft focus background",
            "Music": "Creative studio space with subtle musical instruments as background elements",
            "Fashion": "Minimalist fashion setting with subtle textile elements, elegant atmosphere"
        }
        return background_map.get(category, "Professional lifestyle setting with clean, aspirational atmosphere")

    def _generate_lifestyle_elements_for_trend(self, category: str, interests: List[str]) -> str:
        """Generates atmospheric lifestyle environment based on interest theme - abstract and immersive"""
        # Select the FIRST interest and translate to atmospheric description
        if interests:
            interest = interests[0]
            interest_lower = interest.lower()

            # Map interests to ATMOSPHERIC ENVIRONMENTS rather than single objects
            if "machine learning" in interest_lower or "deep learning" in interest_lower:
                return "modern tech workspace atmosphere with subtle digital elements and clean minimalist aesthetic in background"
            elif "chatgpt" in interest_lower or "ai" in interest_lower:
                return "contemporary digital workspace environment with soft ambient glow and technological aesthetic"
            elif "trail running" in interest_lower:
                return "natural outdoor environment with organic textures and athletic energy in the atmospheric background"
            elif "marathon" in interest_lower or "running" in interest_lower:
                return "active lifestyle setting with dynamic energy and achievement-oriented atmosphere"
            elif "pc gaming" in interest_lower:
                return "immersive gaming setup environment with ambient lighting and entertainment-focused atmosphere"
            elif "mobile gaming" in interest_lower:
                return "casual entertainment space with modern digital lifestyle aesthetic"
            elif "rpg games" in interest_lower or "indie games" in interest_lower:
                return "creative gaming atmosphere with artistic and immersive environmental qualities"
            elif "portrait photography" in interest_lower or "street photography" in interest_lower:
                return "artistic creative workspace with visual storytelling atmosphere and professional aesthetic"
            elif "photo editing" in interest_lower:
                return "digital creative studio environment with focused artistic workflow atmosphere"
            elif "vegan cooking" in interest_lower:
                return "natural wholesome kitchen atmosphere with organic textures and fresh healthy lifestyle aesthetic"
            elif "meal prep" in interest_lower:
                return "organized culinary workspace with efficient lifestyle atmosphere and clean aesthetic"
            elif "cooking" in interest_lower or "international cuisine" in interest_lower:
                return "gourmet kitchen environment with culinary passion and sophisticated food culture atmosphere"
            elif "live music" in interest_lower or "indie music" in interest_lower:
                return "artistic musical atmosphere with creative energy and cultural lifestyle aesthetic"
            elif "guitar" in interest_lower or "playing guitar" in interest_lower:
                return "musical creative space with artistic expression and melodic atmosphere"
            elif "beach holidays" in interest_lower or "island hopping" in interest_lower:
                return "relaxed travel lifestyle atmosphere with wanderlust aesthetic and vacation vibes"
            elif "travel photography" in interest_lower:
                return "adventurous explorer environment with worldly atmosphere and discovery aesthetic"
            elif "wine tasting" in interest_lower or "wine pairing" in interest_lower:
                return "sophisticated sommelier atmosphere with refined taste and elegant lifestyle aesthetic"
            elif "fine dining" in interest_lower or "restaurant reviews" in interest_lower:
                return "upscale culinary setting with gourmet atmosphere and refined dining aesthetic"
            elif "crossfit" in interest_lower:
                return "intense athletic training environment with performance-focused atmosphere and fitness dedication"
            elif "fitness training" in interest_lower:
                return "active wellness lifestyle setting with health-conscious atmosphere and motivational energy"
            elif "netflix binging" in interest_lower or "streaming" in interest_lower:
                return "cozy entertainment space with relaxed viewing atmosphere and comfortable lifestyle aesthetic"
            elif "basketball" in interest_lower:
                return "dynamic sports environment with athletic energy and competitive spirit atmosphere"
            elif "football" in interest_lower or "playing football" in interest_lower:
                return "energetic sports setting with team spirit and athletic lifestyle atmosphere"
            elif "strategy games" in interest_lower:
                return "focused gaming workspace with tactical thinking atmosphere and competitive aesthetic"
            elif "5g technology" in interest_lower or "wearable tech" in interest_lower:
                return "cutting-edge tech lifestyle environment with innovative atmosphere and futuristic aesthetic"
            elif "smart home" in interest_lower:
                return "intelligent connected living space with automated lifestyle atmosphere and modern convenience"
            else:
                # Abstract interpretation of any interest
                # Fallback to category-based
                return f"{interest} inspired lifestyle environment with thematic atmosphere and cultural aesthetic"
        elements_map = {
            "Technology": "laptop and smartphone in soft focus background",
            "Sports": "sports equipment in background",
            "Gaming": "gaming controller in soft focus background",
            "Travel": "map or travel items in background",
            "Food": "fresh ingredients in background",
            "Music": "headphones in background",
            "Fashion": "fabric swatches in background",
            "Health": "wellness items in background",
            "Outdoor": "natural elements in background"
        }
        return elements_map.get(category, "subtle lifestyle props in soft focus background")

    def _generate_lifestyle_context(
        self,
        matched_interests: List[Dict[str, Any]],
        user_data: Dict[str, Any]
    ) -> str:
        """Generates lifestyle integration context"""
        interests = [m['interest']
                     for m in matched_interests[:3]] if matched_interests else []
        occupation = user_data['demographics'].get(
            'occupation', 'professional')

        if interests:
            return f"Product integrated into {occupation} lifestyle with connection to {', '.join(interests)}"
        else:
            return f"Product showcased in aspirational {occupation} lifestyle context"

    def convert_to_simple_prompt(self, structured_prompt: Dict[str, Any]) -> str:
        """
        Converts structured prompt to a simple string format for APIs that prefer text

        Following: Subject + Action + Style + Context
        """
        subject = structured_prompt['subjects'][0]['description']
        action = structured_prompt['subjects'][0]['pose']
        style = structured_prompt['style']
        context = f"{structured_prompt['background']}, {structured_prompt['lighting']}, {structured_prompt['mood']}"

        simple_prompt = f"{subject}, {action}, {style}, {context}"

        return simple_prompt

    def get_cached_prompt(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Returns cached structured prompt for a user"""
        return self.prompt_cache.get(user_id)

    def get_all_cached_prompts(self) -> Dict[int, Dict[str, Any]]:
        """Returns all cached structured prompts"""
        return self.prompt_cache

    def format_for_api(self, structured_prompt: Dict[str, Any], format_type: str = "json") -> str:
        """
        Formats the structured prompt for API submission

        Args:
            structured_prompt: The structured prompt dictionary
            format_type: "json" or "text"

        Returns:
            Formatted prompt string
        """
        if format_type == "text":
            return self.convert_to_simple_prompt(structured_prompt)
        else:
            return json.dumps(structured_prompt, indent=2)


# Singleton instance
image_prompt_builder = ImagePromptBuilder()
