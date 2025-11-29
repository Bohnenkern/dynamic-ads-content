from typing import Dict, Any, Optional, Union
import logging
import os
import httpx
import json

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Service for image generation with Black Forest Labs and other APIs"""

    def __init__(self):
        self.black_forest_api_key = os.getenv("BLACK_FOREST_API_KEY")
        self.generated_images: Dict[int, Dict[str, Any]] = {}

        if self.black_forest_api_key:
            logger.info("Black Forest API Key found")
        else:
            logger.warning(
                "BLACK_FOREST_API_KEY not set - Image Generation disabled")

    async def generate_image_with_black_forest(
        self,
        prompt: Union[str, Dict[str, Any]],
        user_id: int,
        product_name: str = "product",
        width: int = 1024,
        height: int = 768
    ) -> Optional[Dict[str, Any]]:
        """
        Generates an image using Black Forest Labs Flux.2 API

        Args:
            prompt: Structured prompt (dict) or simple text prompt (str)
            user_id: User ID for caching
            product_name: Name of the product being advertised
            width: Image width
            height: Image height

        Returns:
            Dictionary with image_url and metadata
        """
        if not self.black_forest_api_key:
            logger.warning(
                "Black Forest API Key missing - Image generation skipped")
            return None

        try:
            # Convert structured prompt to string if needed
            if isinstance(prompt, dict):
                prompt_str = self._format_structured_prompt(prompt)
                logger.info(f"Using structured prompt for user {user_id}")
            else:
                prompt_str = prompt
                logger.info(f"Using simple text prompt for user {user_id}")

            logger.info(
                f"Generating image with Black Forest for User {user_id}")
            logger.info(f"Prompt preview: {prompt_str[:150]}...")

            # TODO: Real Black Forest Labs API Integration
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         "https://api.bfl.ml/v1/flux-pro-1.1",
            #         headers={
            #             "X-Key": self.black_forest_api_key,
            #             "Content-Type": "application/json"
            #         },
            #         json={
            #             "prompt": prompt_str,
            #             "width": width,
            #             "height": height,
            #             "prompt_upsampling": False,
            #             "safety_tolerance": 2
            #         },
            #         timeout=60.0
            #     )
            #     result = response.json()
            #     image_url = result.get("result", {}).get("sample")

            # Placeholder response
            image_url = f"https://placeholder.com/ads/{user_id}_{product_name}.jpg"

            result = {
                "user_id": user_id,
                "product_name": product_name,
                "image_url": image_url,
                "prompt_used": prompt_str if isinstance(prompt, str) else json.dumps(prompt),
                "dimensions": {"width": width, "height": height},
                "status": "generated"
            }

            self.generated_images[user_id] = result

            logger.info(f"Image generated successfully for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error in Black Forest API call: {str(e)}")
            return None

    def _format_structured_prompt(self, structured_prompt: Dict[str, Any]) -> str:
        """
        Formats structured prompt into optimized text for Black Forest API
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

        # Get camera settings for detail
        camera = structured_prompt.get('camera', {})
        camera_detail = f"{camera.get('angle', 'medium angle')}, {camera.get('focus', 'sharp focus')}"

        # Build optimized prompt following FLUX.2 guidelines
        # Priority: Subject → Action → Style → Context → Details
        prompt_parts = [
            f"{subject}, {action}",
            f"{style}",
            f"{scene}, {background}",
            f"{lighting}, {mood}",
            color_text,
            camera_detail
        ]

        # Join and clean up
        final_prompt = ", ".join([p for p in prompt_parts if p])

        return final_prompt

    async def generate_images_for_users(
        self,
        structured_prompts: Union[Dict[int, Dict[str, Any]], Dict[int, str]],
        product_name: str = "product"
    ) -> Dict[int, Dict[str, Any]]:
        """
        Generates images for multiple users based on prompts

        Args:
            structured_prompts: Dictionary with user_id -> prompt mappings
                               Can be structured dict or optimized text string
            product_name: Name of the product being advertised

        Returns:
            Dictionary with user_id -> result mappings (containing image_url and metadata)
        """
        results = {}

        for user_id, prompt in structured_prompts.items():
            result = await self.generate_image_with_black_forest(
                prompt=prompt,
                user_id=user_id,
                product_name=product_name
            )
            if result:
                results[user_id] = result

        logger.info(f"Generated images for {len(results)} users")
        return results

    def get_cached_image(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Returns cached image result for a user"""
        return self.generated_images.get(user_id)

    def get_all_cached_images(self) -> Dict[int, Dict[str, Any]]:
        """Returns all cached image results"""
        return self.generated_images


# Singleton-Instanz
image_service = ImageGenerationService()
