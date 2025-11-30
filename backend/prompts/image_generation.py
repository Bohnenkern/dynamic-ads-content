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

            # Real Black Forest Labs API Integration
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.bfl.ml/v1/flux-pro-1.1",
                    headers={
                        "X-Key": self.black_forest_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt_str,
                        "width": width,
                        "height": height,
                        "prompt_upsampling": False,
                        "safety_tolerance": 2
                    },
                    timeout=60.0
                )
                result = response.json()
                logger.info(
                    f"Black Forest Response for user {user_id}: {result}")

                # Parse response
                if "result" in result and result["result"]:
                    # Immediate result
                    image_url = result["result"].get("sample")
                elif "id" in result:
                    # Async generation - need to poll
                    task_id = result["id"]
                    polling_url = result.get(
                        "polling_url", f"https://api.bfl.ai/v1/get_result?id={task_id}")
                    logger.info(
                        f"Polling task {task_id} for user {user_id} (max 60s)...")
                    import asyncio
                    for attempt in range(60):  # 60 seconds max
                        await asyncio.sleep(1)
                        status_resp = await client.get(
                            polling_url,
                            headers={"X-Key": self.black_forest_api_key}
                        )
                        status = status_resp.json()

                        # DEBUG: Log full status on first attempt and every 20 seconds
                        if attempt == 0 or (attempt + 1) % 20 == 0:
                            logger.info(
                                f"User {user_id}: Polling status at {attempt + 1}s: {status}")

                        # Check status (case-insensitive)
                        current_status = str(status.get("status", "")).lower()

                        if current_status == "ready":
                            image_url = status.get("result", {}).get("sample")
                            logger.info(
                                f"User {user_id}: Image ready after {attempt + 1} seconds")
                            break
                        elif current_status in ["error", "failed", "request_moderated"]:
                            logger.error(
                                f"User {user_id}: Generation failed with status '{current_status}' - {status}")
                            break
                        elif "not found" in str(status).lower():
                            logger.error(
                                f"User {user_id}: Task not found - API returned: {status}")
                            break
                        # Log progress every 20 seconds
                        elif (attempt + 1) % 20 == 0:
                            logger.info(
                                f"User {user_id}: Still processing (status: {current_status})... ({attempt + 1}s elapsed)")
                    else:
                        logger.warning(
                            f"User {user_id}: Polling timeout after 60 seconds - Last status: {status.get('status', 'unknown')}")
                        image_url = None
                else:
                    image_url = None

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

    async def generate_image_for_trend(
        self,
        prompt: Union[str, Dict[str, Any]],
        trend_category: str,
        product_name: str = "product",
        width: int = 1024,
        height: int = 768,
        reference_image_url: Optional[str] = None,
        image_prompt_strength: float = 0.3
    ) -> Optional[Dict[str, Any]]:
        """
        Generates an image for a specific trend category with optional product image reference

        Args:
            prompt: Optimized prompt for image generation
            trend_category: The trend category this image represents
            product_name: Name of the product being advertised
            width: Image width
            height: Image height
            reference_image_url: URL or base64 of reference product image
            image_prompt_strength: Strength of image reference influence (0.0-1.0)
                                  Lower = more freedom, Higher = closer to reference

        Returns:
            Dictionary with image_url and metadata including trend_category
        """
        if not self.black_forest_api_key:
            logger.warning(
                "Black Forest API Key missing - Image generation skipped")
            return None

        try:
            # Convert structured prompt to string if needed
            if isinstance(prompt, dict):
                prompt_str = self._format_structured_prompt(prompt)
            else:
                prompt_str = prompt

            logger.info(
                f"Generating image for trend category: {trend_category}")
            logger.info(f"Prompt preview: {prompt_str[:150]}...")
            if reference_image_url:
                # Show only first 50 chars of base64 to avoid log spam
                img_preview = reference_image_url[:50] + "..." if len(
                    reference_image_url) > 50 else reference_image_url
                logger.info(
                    f"Using reference image ({len(reference_image_url)} chars) with strength: {image_prompt_strength}")

            # Build request payload
            request_payload = {
                "prompt": prompt_str,
                "width": width,
                "height": height,
                "safety_tolerance": 2,
                "output_format": "jpeg"
            }

            # Add image reference if provided (for image editing endpoint)
            # FLUX.2 accepts both URLs and raw base64 (without data: prefix)
            if reference_image_url:
                # Remove data URI prefix if present, API expects raw base64 or URL
                if reference_image_url.startswith('data:'):
                    # Extract raw base64: "data:image/jpeg;base64,ABC123..." -> "ABC123..."
                    base64_data = reference_image_url.split(
                        ',', 1)[1] if ',' in reference_image_url else reference_image_url
                    request_payload["input_image"] = base64_data
                else:
                    request_payload["input_image"] = reference_image_url
                # Note: image_prompt_strength not supported in FLUX.2, use prompt engineering instead

            # Real Black Forest Labs API Integration
            # Use flux-2-pro for image editing (with input_image), flux-pro-1.1 for text-to-image
            endpoint = "https://api.bfl.ai/v1/flux-2-pro" if reference_image_url else "https://api.bfl.ml/v1/flux-pro-1.1"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    headers={
                        "X-Key": self.black_forest_api_key,
                        "Content-Type": "application/json"
                    },
                    json=request_payload,
                    timeout=60.0
                )
                result = response.json()
                # Log only status, not full response with base64 data
                if response.status_code != 200:
                    logger.error(
                        f"Black Forest API Error for {trend_category}: Status {response.status_code}")
                    if "detail" in result:
                        logger.error(f"Error details: {result['detail']}")
                else:
                    logger.info(
                        f"Black Forest Response for {trend_category}: Status {response.status_code} - Success")

                # Parse response correctly
                if "result" in result and result["result"]:
                    # Immediate result (rare for FLUX.2)
                    image_url = result["result"].get("sample")
                elif "id" in result:
                    # Async generation - need to poll
                    task_id = result["id"]
                    # Use polling_url from response or construct with correct domain
                    polling_url = result.get(
                        "polling_url", f"https://api.bfl.ai/v1/get_result?id={task_id}")
                    logger.info(
                        f"Polling task {task_id} for {trend_category} (max 60s)...")
                    import asyncio
                    for attempt in range(60):  # 60 seconds max
                        await asyncio.sleep(1)
                        status_resp = await client.get(
                            polling_url,
                            headers={"X-Key": self.black_forest_api_key}
                        )
                        status = status_resp.json()

                        # DEBUG: Log full status on first attempt and every 20 seconds
                        if attempt == 0 or (attempt + 1) % 20 == 0:
                            logger.info(
                                f"{trend_category}: Polling status at {attempt + 1}s: {status}")

                        # Check status (case-insensitive)
                        current_status = str(status.get("status", "")).lower()

                        if current_status == "ready":
                            image_url = status.get("result", {}).get("sample")
                            logger.info(
                                f"{trend_category}: Image ready after {attempt + 1} seconds")
                            break
                        elif current_status in ["error", "failed", "request_moderated"]:
                            logger.error(
                                f"{trend_category}: Generation failed with status '{current_status}' - {status}")
                            break
                        elif "not found" in str(status).lower():
                            logger.error(
                                f"{trend_category}: Task not found - API returned: {status}")
                            break
                        # Log progress every 20 seconds
                        elif (attempt + 1) % 20 == 0:
                            logger.info(
                                f"{trend_category}: Still processing (status: {current_status})... ({attempt + 1}s elapsed)")
                    else:
                        logger.warning(
                            f"{trend_category}: Polling timeout after 60 seconds - Last status: {status.get('status', 'unknown')}")
                        image_url = None
                else:
                    image_url = None

            result_data = {
                "trend_category": trend_category,
                "product_name": product_name,
                "image_url": image_url,
                "prompt_used": prompt_str,
                "dimensions": {"width": width, "height": height},
                "status": "generated"
            }

            logger.info(
                f"Image URL for {trend_category}: {image_url}")
            return result_data

        except Exception as e:
            logger.error(
                f"Error in Black Forest API call for trend {trend_category}: {str(e)}")
            return None

    async def generate_images_for_trends(
        self,
        trend_prompts: Dict[str, str],
        product_name: str = "product",
        reference_image_url: Optional[str] = None,
        image_prompt_strength: float = 0.3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generates images for multiple trend categories with optional product image reference
        PARALLELIZED: All requests run concurrently for faster execution

        Args:
            trend_prompts: Dictionary with trend_category -> prompt mappings
            product_name: Name of the product being advertised
            reference_image_url: URL or base64 of reference product image
            image_prompt_strength: Strength of image reference (0.0-1.0)

        Returns:
            Dictionary with trend_category -> result mappings (containing image_url and metadata)
        """
        import asyncio

        logger.info(
            f"Starting parallel image generation for {len(trend_prompts)} trends...")

        # Create tasks for parallel execution
        tasks = []
        trend_categories = []

        for trend_category, prompt in trend_prompts.items():
            task = self.generate_image_for_trend(
                prompt=prompt,
                trend_category=trend_category,
                product_name=product_name,
                reference_image_url=reference_image_url,
                image_prompt_strength=image_prompt_strength
            )
            tasks.append(task)
            trend_categories.append(trend_category)

        # Execute all tasks in parallel
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dictionary
        results = {}
        for trend_category, result in zip(trend_categories, results_list):
            if isinstance(result, Exception):
                logger.error(
                    f"Error generating image for {trend_category}: {str(result)}")
            elif result:
                results[trend_category] = result

        logger.info(
            f"Parallel generation complete: {len(results)}/{len(trend_prompts)} images generated successfully")
        return results

    async def generate_images_for_users(
        self,
        structured_prompts: Union[Dict[int, Dict[str, Any]], Dict[int, str]],
        product_name: str = "product"
    ) -> Dict[int, Dict[str, Any]]:
        """
        Generates images for multiple users based on prompts
        PARALLELIZED: All requests run concurrently for faster execution

        Args:
            structured_prompts: Dictionary with user_id -> prompt mappings
                               Can be structured dict or optimized text string
            product_name: Name of the product being advertised

        Returns:
            Dictionary with user_id -> result mappings (containing image_url and metadata)
        """
        import asyncio

        logger.info(
            f"Starting parallel image generation for {len(structured_prompts)} users...")

        # Create tasks for parallel execution
        tasks = []
        user_ids = []

        for user_id, prompt in structured_prompts.items():
            task = self.generate_image_with_black_forest(
                prompt=prompt,
                user_id=user_id,
                product_name=product_name
            )
            tasks.append(task)
            user_ids.append(user_id)

        # Execute all tasks in parallel
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dictionary
        results = {}
        for user_id, result in zip(user_ids, results_list):
            if isinstance(result, Exception):
                logger.error(
                    f"Error generating image for user {user_id}: {str(result)}")
            elif result:
                results[user_id] = result

        logger.info(
            f"Parallel generation complete: {len(results)}/{len(structured_prompts)} images generated successfully")
        return results

    def get_cached_image(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Returns cached image result for a user"""
        return self.generated_images.get(user_id)

    def get_all_cached_images(self) -> Dict[int, Dict[str, Any]]:
        """Returns all cached image results"""
        return self.generated_images

    def cache_trend_image(self, trend_category: str, image_data: Dict[str, Any]):
        """Caches an image for a specific trend category"""
        if not hasattr(self, 'trend_images'):
            self.trend_images: Dict[str, Dict[str, Any]] = {}
        self.trend_images[trend_category] = image_data

    def get_trend_image(self, trend_category: str) -> Optional[Dict[str, Any]]:
        """Returns cached image for a trend category"""
        if not hasattr(self, 'trend_images'):
            return None
        return getattr(self, 'trend_images', {}).get(trend_category)

    def get_all_trend_images(self) -> Dict[str, Dict[str, Any]]:
        """Returns all cached trend images"""
        if not hasattr(self, 'trend_images'):
            self.trend_images = {}
        return self.trend_images


# Singleton instance
image_service = ImageGenerationService()
