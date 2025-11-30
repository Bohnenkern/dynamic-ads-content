from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
import logging
import json
import shutil
import asyncio
import random
from pathlib import Path
from datetime import datetime

from services.user_data import user_service
from services.trend_matcher import trend_matcher
from services.trend_analysis import trend_service
from prompts.openai_service import openai_service
from prompts.trend_filter import trend_filter_service
from prompts.image_prompt_builder import image_prompt_builder
from prompts.image_generation import image_service

router = APIRouter()
logger = logging.getLogger(__name__)

# API Call Limits to prevent overuse
MAX_TRENDS_FOR_OPTIMIZATION = 5  # OpenAI GPT-4o limit
# Generate one image per user interest (3 interests per user)
IMAGES_PER_USER = 3

# boolean for trend filtering step
ENABLE_TREND_FILTERING = False


class CampaignRequest(BaseModel):
    """Request model for campaign generation (deprecated - use FormData)"""
    product_description: str
    campaign_theme: Optional[str] = "general marketing campaign"


async def save_uploaded_image(upload_file: UploadFile) -> str:
    """Saves uploaded product image temporarily"""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = Path(upload_file.filename).suffix
    file_path = upload_dir / f"product_{timestamp}{file_extension}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"Product image saved: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to save image: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to save image: {str(e)}")


@router.get("/users")
async def get_all_users():
    """Gibt alle User zurück"""
    users = user_service.get_all_users()

    if not users:
        raise HTTPException(status_code=404, detail="Keine User gefunden")

    return {
        "count": len(users),
        "users": users
    }


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """Gibt einen spezifischen User zurück"""
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User mit ID {user_id} nicht gefunden")

    return user


@router.post("/match/user/{user_id}")
async def match_user_trends(user_id: int):
    """Führt Trend-Matching für einen User durch"""
    result = trend_matcher.match_user_with_trends(user_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.post("/match/all")
async def match_all_users_trends():
    """Führt Trend-Matching für alle User durch"""
    results = trend_matcher.match_all_users()

    if not results:
        raise HTTPException(
            status_code=404, detail="Keine User zum Matchen gefunden")

    return {
        "count": len(results),
        "results": results
    }


@router.post("/generate-prompts")
async def generate_all_prompts():
    """
    DEPRECATED: Use /campaign/generate instead for full workflow

    Legacy endpoint - generates basic structured prompts without optimization
    """
    # Schritt 1: Trend-Matching
    match_results = trend_matcher.match_all_users()

    if not match_results:
        raise HTTPException(status_code=404, detail="Keine User gefunden")

    # Schritt 2: Generiere Basis-Prompts (regelbasiert)
    structured_prompts = {}
    for match_result in match_results:
        if match_result.get("matched_interests"):
            user_id = match_result["user_id"]
            user_data = user_service.get_user_by_id(user_id)

            if user_data:
                structured_prompt = image_prompt_builder.build_structured_prompt(
                    product_description="generic product",
                    user_data=user_data,
                    matched_interests=match_result["matched_interests"]
                )
                structured_prompts[user_id] = structured_prompt

    # Kombiniere Ergebnisse
    combined_results = []
    for match_result in match_results:
        user_id = match_result["user_id"]
        combined_results.append({
            "user_id": user_id,
            "user_name": match_result["user_name"],
            "matched_interests": match_result["matched_interests"],
            "match_count": match_result["match_count"],
            "structured_prompt": structured_prompts.get(user_id, {})
        })

    return {
        "count": len(combined_results),
        "results": combined_results,
        "note": "This endpoint is deprecated. Use /campaign/generate for optimized prompts."
    }


@router.get("/prompts/{user_id}")
async def get_user_prompt(user_id: int):
    """Returns optimized image prompt for a user"""
    prompt = openai_service.get_cached_prompt(user_id)

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="No optimized prompt found for this user. Please run /campaign/generate first."
        )

    return {
        "user_id": user_id,
        "optimized_prompt": prompt,
        "type": "image_generation"
    }


@router.get("/prompts")
async def get_all_prompts():
    """Returns all optimized image prompts"""
    prompts = openai_service.get_all_cached_prompts()

    if not prompts:
        raise HTTPException(
            status_code=404,
            detail="No optimized prompts found. Please run /campaign/generate first."
        )

    return {
        "count": len(prompts),
        "prompts": prompts,
        "type": "optimized_image_prompts"
    }


@router.post("/campaign/generate")
async def generate_campaign(
    product_image: UploadFile = File(...),
    product_description: str = Form(...),
    campaign_theme: str = Form(default="general marketing campaign"),
    style_preset: str = Form(default="highly_stylized")
):
    """
    Complete workflow for personalized ad campaign generation:
    1. Receive and save product image from frontend
    2. Load hardcoded trends
    3. Filter trends with OpenAI for campaign suitability
    4. Match filtered trends with user interests
    5. Build structured image prompts (rule-based)
    6. Optimize prompts with OpenAI (GPT-4o)
    7. [Next step] Generate images with Black Forest Labs

    Args:
        product_image: Product image file from frontend
        product_description: Description of the product to advertise
        campaign_theme: Theme of the marketing campaign
        style_preset: Visual style preset (realistic, semi_realistic, highly_stylized)
    """

    logger.info("=" * 70)
    logger.info("CAMPAIGN GENERATION STARTED (OPTIMIZED PIPELINE)")
    logger.info("=" * 70)
    logger.info(f"Product: {product_description}")
    logger.info(f"Theme: {campaign_theme}")
    logger.info(f"Style: {style_preset}")
    logger.info(
        f"Image: {product_image.filename} ({product_image.content_type})")
    logger.info("=" * 70)

    # STEP 1: Save uploaded product image and convert to base64 for Black Forest API
    try:
        import base64
        from PIL import Image
        import io

        image_path = await save_uploaded_image(product_image)
        logger.info(f" Step 1 Complete: Image saved to {image_path}")

        # Analyze image with OpenAI Vision
        logger.info(" Analyzing image with OpenAI Vision...")
        image_analysis = await openai_service.analyze_image(image_path)
        logger.info(" Image analysis complete")

        # Convert image to JPEG format (Black Forest API requirement)
        # Open image and convert to RGB (removes alpha channel if present)
        img = Image.open(image_path)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB to avoid transparency issues
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()
                          [-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Save as JPEG to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)

        # Encode to base64
        image_data = base64.b64encode(img_byte_arr.read()).decode('utf-8')
        image_base64_uri = f"data:image/jpeg;base64,{image_data}"

        logger.info(
            f"Step 1b: Image converted to JPEG and base64 ({len(image_data)} chars)")
    except Exception as e:
        logger.error(f"Step 1 Failed: {str(e)}")
        raise

    # STEP 2: Get hardcoded trends
    trends_data = trend_service.get_cached_trends()
    if "message" in trends_data or "error" in trends_data:
        logger.error("Step 2 Failed: No trend data available")
        raise HTTPException(status_code=404, detail="No trend data available")

    trends = trends_data.get("trends", [])
    if not trends:
        logger.error("Step 2 Failed: No trends found")
        raise HTTPException(status_code=404, detail="No trends found")

    logger.info(f"Step 2 Complete: Loaded {len(trends)} hardcoded trends")
    for trend in trends:
        logger.info(
            f"    {trend['category']}: {', '.join(trend['interests'][:3])}...")

    # STEP 3: Filter trends with OpenAI (LLM-based safety check)
    if ENABLE_TREND_FILTERING:
        logger.info(
            f" Step 3: Filtering trends with OpenAI for campaign suitability...")
        filtered_trends = await trend_filter_service.filter_trends_for_campaign(
            trends=trends,
            campaign_theme=campaign_theme,
        )

        if not filtered_trends:
            logger.error(" Step 3 Failed: No suitable trends after filtering")
            raise HTTPException(
                status_code=400,
                detail="No suitable trends found after filtering for campaign safety"
            )

        logger.info(
            f" Step 3 Complete: {len(trends)} → {len(filtered_trends)} suitable trends")
        for trend in filtered_trends:
            logger.info(f"   ✓ Kept: {trend['category']}")
    else:
        logger.info(
            f"⏭  Step 3 Skipped: Trend filtering disabled (ENABLE_TREND_FILTERING=False)")
        filtered_trends = trends

    # STEP 4: Match filtered trends with users
    logger.info(f" Step 4: Matching filtered trends with 5 users...")

    # Temporarily update trend service cache with filtered trends
    original_trends = trends_data.copy()
    trend_service.trends_data = {
        "trends": filtered_trends,
        "timestamp": trends_data.get("timestamp"),
        "total_users_analyzed": trends_data.get("total_users_analyzed")
    }

    match_results = await trend_matcher.match_all_users()

    # Restore original trends
    trend_service.trends_data = original_trends

    if not match_results:
        logger.error(" Step 4 Failed: No users found for matching")
        raise HTTPException(
            status_code=404, detail="No users found for matching")

    logger.info(
        f" Step 4 Complete: Matched trends with {len(match_results)} users")
    for match in match_results:
        logger.info(
            f"   👤 {match['user_name']}: {match['match_count']} matches")

    # STEP 5: Build base structured prompts (rule-based, fast)
    logger.info(f"🏗️  Step 5: Building structured prompts (rule-based)...")
    structured_prompts = {}
    user_matches = {}

    for match_result in match_results:
        if match_result.get("matched_interests"):
            user_id = match_result["user_id"]
            user_data = user_service.get_user_by_id(user_id)

            if user_data:
                structured_prompt = image_prompt_builder.build_structured_prompt(
                    product_description=product_description,
                    user_data=user_data,
                    matched_interests=match_result["matched_interests"]
                )
                structured_prompts[user_id] = structured_prompt
                user_matches[user_id] = match_result

    logger.info(
        f" Step 5 Complete: Built {len(structured_prompts)} structured prompts")

    # Initialize API call counter
    api_calls = {
        "openai_gpt4o_mini": 0,
        "openai_gpt4o": 0,
        "black_forest": 0
    }

    # Count API calls from previous steps
    api_calls["openai_gpt4o_mini"] += 1  # Step 3: Trend filtering
    # Step 4: Interest matching (1 per user)
    api_calls["openai_gpt4o_mini"] += len(match_results)

    # PREPARE STEP 9 (Preview User Selection) - Moved up for parallelization
    random_user_match = None
    user_optimized_prompt_task = None
    random_user_data = None

    if match_results:
        random_user_match = random.choice(match_results)
        random_user_id = random_user_match["user_id"]
        random_user_data = user_service.get_user_by_id(random_user_id)
        user_structured_prompt = structured_prompts.get(random_user_id)

        if user_structured_prompt and random_user_data:
            logger.info(
                f" Preparing preview generation for random user: {random_user_data.get('name')}")
            user_optimized_prompt_task = openai_service.optimize_image_prompt(
                product_description=product_description,
                user_data=random_user_data,
                matched_interests=random_user_match.get(
                    "matched_interests", []),
                base_structured_prompt=user_structured_prompt,
                image_analysis=image_analysis,
                style_preset=style_preset
            )

    # STEP 6: Build prompts for EACH USER'S SPECIFIC INTERESTS (one image per interest)
    # NEW APPROACH: Generate 3 images per user (one per interest) = 15 total images for 5 users
    logger.info(
        f" Step 6: Building prompts for each user's {IMAGES_PER_USER} interests...")
    logger.info(
        f"    Total images to generate: {len(match_results)} users × {IMAGES_PER_USER} interests = {len(match_results) * IMAGES_PER_USER} images")

    # Prepare data for parallel OpenAI prompt optimization
    # Structure: [{user_id, user_data, interest, structured_prompt}, ...]
    user_interest_prompts = []

    for match_result in match_results:
        user_id = match_result["user_id"]
        user_data = user_service.get_user_by_id(user_id)

        if not user_data:
            continue

        # Get user's raw interests (should be exactly 3)
        user_interests = user_data.get("interests", [])

        # Generate one image per interest
        for interest in user_interests[:IMAGES_PER_USER]:
            # Build structured prompt for this specific interest
            structured_prompt = image_prompt_builder.build_prompt_for_trend(
                product_description=product_description,
                trend_category=interest,  # Use interest as category
                trend_interests=[interest]  # Single interest
            )

            user_interest_prompts.append({
                "user_id": user_id,
                "user_name": user_data.get("name"),
                "interest": interest,
                "structured_prompt": structured_prompt
            })

    logger.info(
        f"    Prepared {len(user_interest_prompts)} user-interest combinations for optimization")

    # Parallelize OpenAI prompt optimization for all user interests AND preview user
    logger.info(
        f"    Optimizing {len(user_interest_prompts)} user-interest prompts in parallel with GPT-4o...")

    optimization_tasks = []

    # 1. User-Interest Optimization Tasks
    for data in user_interest_prompts:
        user_data_for_opt = user_service.get_user_by_id(data["user_id"])
        task = openai_service.optimize_image_prompt(
            product_description=product_description,
            user_data=user_data_for_opt,
            matched_interests=[
                {"interest": data["interest"], "category": data["interest"]}],
            base_structured_prompt=data["structured_prompt"],
            style_preset=style_preset
        )
        optimization_tasks.append(task)

    # 2. Preview User Optimization Task (if exists)
    if user_optimized_prompt_task:
        optimization_tasks.append(user_optimized_prompt_task)

    # Execute all optimizations in parallel
    import asyncio
    all_optimized_results = await asyncio.gather(*optimization_tasks, return_exceptions=True)

    # Separate results
    user_optimized_prompt = None
    if user_optimized_prompt_task:
        user_optimized_prompt = all_optimized_results[-1]
        user_interest_optimized_results = all_optimized_results[:-1]

        if isinstance(user_optimized_prompt, Exception):
            logger.error(
                f"Error optimizing preview prompt: {str(user_optimized_prompt)}")
            user_optimized_prompt = None
        else:
            api_calls["openai_gpt4o"] += 1
    else:
        user_interest_optimized_results = all_optimized_results

    # Build user_interest_prompts_optimized list with optimized prompts
    for data, optimized_prompt in zip(user_interest_prompts, user_interest_optimized_results):
        if isinstance(optimized_prompt, Exception):
            logger.error(
                f"Error optimizing prompt for {data['user_name']}'s interest '{data['interest']}': {str(optimized_prompt)}")
            # Fallback to basic prompt conversion
            optimized_prompt = image_prompt_builder.convert_to_simple_prompt(
                data["structured_prompt"])
        data["optimized_prompt"] = optimized_prompt
        api_calls["openai_gpt4o"] += 1  # Count GPT-4o optimization call

    logger.info(
        f"Step 6 Complete: Optimized {len(user_interest_prompts)} user-interest prompts in parallel")
    logger.info(
        f"    API Calls so far - GPT-4o-mini: {api_calls['openai_gpt4o_mini']}, GPT-4o: {api_calls['openai_gpt4o']}")

    # STEP 7 & 9: Generate images for each user's interests AND previews in parallel
    # Generate exactly 3 images per user (one per interest) = 15 images total for 5 users
    logger.info(
        f"Step 7 & 9: Generating {len(user_interest_prompts)} user-interest images + 3 preview images in parallel...")
    logger.info(
        f"    Using FLUX.2 Image Editing with product image as input_image")
    logger.info(
        f"    PARALLEL EXECUTION: All images will be generated simultaneously")

    image_generation_tasks = []

    # Tasks 1-N: User-Interest Images
    for data in user_interest_prompts:
        task = image_service.generate_image_for_trend(
            prompt=data["optimized_prompt"],
            # Unique identifier
            trend_category=f"{data['user_name']}_{data['interest']}",
            product_name=product_description.split()[0],
            reference_image_url=image_base64_uri
        )
        image_generation_tasks.append(task)

    # Tasks N+1 to N+3: Preview Images (if prompt available)
    preview_categories = ["preview_banner",
                          "preview_vertical", "preview_rectangular"]
    preview_dims = [(1280, 320), (512, 1024), (768, 768)]

    if user_optimized_prompt:
        for category, (w, h) in zip(preview_categories, preview_dims):
            task = image_service.generate_image_for_trend(
                prompt=user_optimized_prompt,
                trend_category=category,
                width=w,
                height=h,
                reference_image_url=image_base64_uri
            )
            image_generation_tasks.append(task)

    # Execute ALL image generations in parallel
    all_image_results = await asyncio.gather(*image_generation_tasks, return_exceptions=True)

    # Process User-Interest Images Results
    user_interest_images = {}
    for idx, data in enumerate(user_interest_prompts):
        result = all_image_results[idx]
        if isinstance(result, Exception):
            logger.error(
                f"Error generating image for {data['user_name']}'s interest '{data['interest']}': {str(result)}")
        elif result:
            # Store with composite key: user_id + interest
            key = f"{data['user_id']}_{data['interest']}"
            user_interest_images[key] = {
                **result,
                "user_id": data["user_id"],
                "interest": data["interest"]
            }
            api_calls["black_forest"] += 1

    # Process Preview Images Results
    preview_formats = {}
    if user_optimized_prompt:
        preview_start_idx = len(user_interest_prompts)
        preview_results_list = all_image_results[preview_start_idx:]

        # Map results back to categories
        banner_res = preview_results_list[0] if len(preview_results_list) > 0 and not isinstance(
            preview_results_list[0], Exception) else None
        vertical_res = preview_results_list[1] if len(preview_results_list) > 1 and not isinstance(
            preview_results_list[1], Exception) else None
        rect_res = preview_results_list[2] if len(preview_results_list) > 2 and not isinstance(
            preview_results_list[2], Exception) else None

        if random_user_data:
            preview_formats = {
                "user_id": random_user_data.get("id"),
                "user_name": random_user_data.get("name"),
                "banner": banner_res,
                "vertical": vertical_res,
                "rectangular": rect_res
            }

            # Count preview images
            if banner_res:
                api_calls["black_forest"] += 1
            if vertical_res:
                api_calls["black_forest"] += 1
            if rect_res:
                api_calls["black_forest"] += 1

            logger.info(
                f"Step 9 Complete: Generated preview formats for {random_user_data.get('name')}")

    logger.info(
        f"Step 7 & 9 Complete: Generated all images in parallel (much faster!)")
    logger.info(
        f"    Black Forest API calls: {api_calls['black_forest']}")

    # STEP 8: Map generated images to users based on their interests
    logger.info(f"Step 8: Mapping user-interest images to users...")
    campaign_results = []

    for match_result in match_results:
        user_id = match_result["user_id"]
        user_data = user_service.get_user_by_id(user_id)

        if not user_data:
            continue

        # Get user's raw interests (exactly 3)
        user_interests = user_data.get("interests", [])

        user_images = []
        for interest in user_interests:
            # Look up image by composite key
            key = f"{user_id}_{interest}"
            image_data = user_interest_images.get(key)

            if image_data:
                user_images.append({
                    "interest": interest,
                    "image_url": image_data.get("image_url"),
                    "prompt_used": image_data.get("prompt_used"),
                    "status": "generated"
                })
            else:
                user_images.append({
                    "interest": interest,
                    "image_url": None,
                    "status": "failed",
                    "message": f"Image generation failed for interest: {interest}"
                })

        result = {
            "user_id": user_id,
            "user_name": match_result["user_name"],
            "interests": user_interests,
            "generated_images": user_images,
            "images_count": len([img for img in user_images if img.get("image_url")])
        }
        campaign_results.append(result)

    logger.info(
        f"Step 8 Complete: Mapped {len(user_interest_images)} images to {len(campaign_results)} users")

    logger.info("=" * 70)
    logger.info("CAMPAIGN GENERATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info("API USAGE STATISTICS:")
    logger.info(
        f"   • OpenAI GPT-4o-mini calls: {api_calls['openai_gpt4o_mini']}")
    logger.info(f"   • OpenAI GPT-4o calls: {api_calls['openai_gpt4o']}")
    logger.info(
        f"   • Black Forest image generations: {api_calls['black_forest']} ({IMAGES_PER_USER} per user × {len(campaign_results)} users)")
    logger.info(
        f"   • Total OpenAI API calls: {api_calls['openai_gpt4o_mini'] + api_calls['openai_gpt4o']}")
    logger.info("=" * 70)

    total_images_generated = sum([result["images_count"]
                                 for result in campaign_results])

    return {
        "campaign_theme": campaign_theme,
        "product_description": product_description,
        "product_image_path": image_path,
        "total_trends_analyzed": len(trends),
        "filtered_trends_count": len(filtered_trends),
        "images_per_user": IMAGES_PER_USER,
        "users_targeted": len(campaign_results),
        "total_user_images_generated": total_images_generated,
        "preview_formats": preview_formats,
        "api_usage": {
            "openai_gpt4o_mini_calls": api_calls["openai_gpt4o_mini"],
            "openai_gpt4o_calls": api_calls["openai_gpt4o"],
            "black_forest_calls": api_calls["black_forest"],
            "total_openai_calls": api_calls["openai_gpt4o_mini"] + api_calls["openai_gpt4o"],
            "images_per_user": IMAGES_PER_USER,
            "optimization_limit": MAX_TRENDS_FOR_OPTIMIZATION
        },
        "results": campaign_results
    }


@router.get("/campaign/images")
async def get_generated_images():
    """Returns all generated campaign images"""
    images = image_service.get_all_cached_images()

    if not images:
        raise HTTPException(
            status_code=404,
            detail="No images found. Please generate a campaign first."
        )

    return {
        "count": len(images),
        "images": images
    }


@router.get("/campaign/images/{user_id}")
async def get_user_image(user_id: int):
    """Returns generated image for a specific user"""
    image = image_service.get_cached_image(user_id)

    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"No image found for user {user_id}. Please generate a campaign first."
        )

    return image
