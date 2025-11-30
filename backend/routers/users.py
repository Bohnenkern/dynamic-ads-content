from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
import logging
import json
import shutil
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
MAX_IMAGES_PER_CAMPAIGN = 5  # Black Forest API limit
MAX_TRENDS_FOR_OPTIMIZATION = 5  # OpenAI GPT-4o limit


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
    campaign_theme: str = Form(default="general marketing campaign")
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
    """

    logger.info("=" * 70)
    logger.info("🚀 CAMPAIGN GENERATION STARTED")
    logger.info("=" * 70)
    logger.info(f"📱 Product: {product_description}")
    logger.info(f"🎯 Theme: {campaign_theme}")
    logger.info(
        f"🖼️  Image: {product_image.filename} ({product_image.content_type})")
    logger.info("=" * 70)

    # STEP 1: Save uploaded product image and convert to base64 for Black Forest API
    try:
        import base64
        from PIL import Image
        import io

        image_path = await save_uploaded_image(product_image)
        logger.info(f"✅ Step 1 Complete: Image saved to {image_path}")

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
            f"✅ Step 1b: Image converted to JPEG and base64 ({len(image_data)} chars)")
    except Exception as e:
        logger.error(f"❌ Step 1 Failed: {str(e)}")
        raise

    # STEP 2: Get hardcoded trends
    trends_data = trend_service.get_cached_trends()
    if "message" in trends_data or "error" in trends_data:
        logger.error("❌ Step 2 Failed: No trend data available")
        raise HTTPException(status_code=404, detail="No trend data available")

    trends = trends_data.get("trends", [])
    if not trends:
        logger.error("❌ Step 2 Failed: No trends found")
        raise HTTPException(status_code=404, detail="No trends found")

    logger.info(f"✅ Step 2 Complete: Loaded {len(trends)} hardcoded trends")
    for trend in trends:
        logger.info(
            f"   📊 {trend['category']}: {', '.join(trend['interests'][:3])}...")

    # STEP 3: Filter trends with OpenAI (LLM-based safety check)
    logger.info(
        f"🔍 Step 3: Filtering trends with OpenAI for campaign suitability...")
    filtered_trends = await trend_filter_service.filter_trends_for_campaign(
        trends=trends,
        campaign_theme=campaign_theme,
    )

    if not filtered_trends:
        logger.error("❌ Step 3 Failed: No suitable trends after filtering")
        raise HTTPException(
            status_code=400,
            detail="No suitable trends found after filtering for campaign safety"
        )

    logger.info(
        f"✅ Step 3 Complete: {len(trends)} → {len(filtered_trends)} suitable trends")
    for trend in filtered_trends:
        logger.info(f"   ✓ Kept: {trend['category']}")

    # STEP 4: Match filtered trends with users
    logger.info(f"🎯 Step 4: Matching filtered trends with 5 users...")

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
        logger.error("❌ Step 4 Failed: No users found for matching")
        raise HTTPException(
            status_code=404, detail="No users found for matching")

    logger.info(
        f"✅ Step 4 Complete: Matched trends with {len(match_results)} users")
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
        f"✅ Step 5 Complete: Built {len(structured_prompts)} structured prompts")

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

    # STEP 6: Build prompts for TOP trend categories (limited to prevent API overuse)
    # Select top trends based on:
    # 1. How many users matched this trend
    # 2. Popularity score
    trend_user_counts = {}
    for match_result in match_results:
        for interest in match_result.get("matched_interests", []):
            category = interest.get("category")
            if category:
                trend_user_counts[category] = trend_user_counts.get(
                    category, 0) + 1

    # Sort filtered trends by user match count + popularity
    filtered_trends_sorted = sorted(
        filtered_trends,
        key=lambda t: (trend_user_counts.get(
            t["category"], 0), t.get("popularity_score", 0)),
        reverse=True
    )

    # Limit to MAX_TRENDS_FOR_OPTIMIZATION (5 trends max)
    selected_trends = filtered_trends_sorted[:MAX_TRENDS_FOR_OPTIMIZATION]

    logger.info(
        f"🏗️  Step 6: Building prompts for TOP {len(selected_trends)} trend categories (limited to {MAX_TRENDS_FOR_OPTIMIZATION})...")
    logger.info("   🎯 Selected trends based on user matches + popularity:")
    for trend in selected_trends:
        user_count = trend_user_counts.get(trend["category"], 0)
        logger.info(f"      • {trend['category']}: {user_count} users matched")

    trend_prompts = {}
    for trend in selected_trends:
        trend_category = trend["category"]
        trend_interests = trend["interests"]

        structured_prompt = image_prompt_builder.build_prompt_for_trend(
            product_description=product_description,
            trend_category=trend_category,
            trend_interests=trend_interests
        )

        optimized_prompt = await openai_service.optimize_image_prompt(
            product_description=product_description,
            user_data={"name": "Campaign", "id": 0, "age": 30,
                       "demographics": {"occupation": "General"}},
            matched_interests=[{"interest": interest, "category": trend_category}
                               for interest in trend_interests[:3]],
            base_structured_prompt=structured_prompt
        )

        trend_prompts[trend_category] = optimized_prompt
        api_calls["openai_gpt4o"] += 1  # Count GPT-4o optimization call

    logger.info(
        f"✅ Step 6 Complete: Built {len(trend_prompts)} trend-specific prompts")
    logger.info(
        f"   📊 API Calls so far - GPT-4o-mini: {api_calls['openai_gpt4o_mini']}, GPT-4o: {api_calls['openai_gpt4o']}")

    # STEP 7: Generate images ONLY for selected trends (MAX 5) with Black Forest API
    # Further limit to MAX_IMAGES_PER_CAMPAIGN to protect API key
    images_to_generate = min(len(trend_prompts), MAX_IMAGES_PER_CAMPAIGN)
    limited_trend_prompts = dict(
        list(trend_prompts.items())[:images_to_generate])

    logger.info(
        f"🎨 Step 7: Generating {images_to_generate} images with Black Forest API (limited to {MAX_IMAGES_PER_CAMPAIGN})...")
    logger.info(
        f"   📸 Using FLUX.2 Image Editing with product image as input_image")
    if len(trend_prompts) > MAX_IMAGES_PER_CAMPAIGN:
        logger.warning(
            f"   ⚠️  Limiting from {len(trend_prompts)} trends to {MAX_IMAGES_PER_CAMPAIGN} images to protect API key")

    # Pass the product image to Black Forest FLUX.2 API (image editing mode)
    trend_images = await image_service.generate_images_for_trends(
        trend_prompts=limited_trend_prompts,
        product_name=product_description.split()[0],
        reference_image_url=image_base64_uri,  # Raw base64 string
        # Note: FLUX.2 doesn't have strength parameter, control via prompt engineering
        image_prompt_strength=0.3  # Ignored, kept for API compatibility
    )

    # Count actual images generated
    api_calls["black_forest"] = len(trend_images)

    for trend_category, image_data in trend_images.items():
        image_service.cache_trend_image(trend_category, image_data)

    logger.info(
        f"✅ Step 7 Complete: Generated {len(trend_images)} trend images")
    logger.info(
        f"   🖼️  Black Forest API calls: {api_calls['black_forest']}/{MAX_IMAGES_PER_CAMPAIGN}")

    # STEP 8: Map generated images to users based on their matched interests
    logger.info(f"🔗 Step 8: Mapping trend images to users...")
    campaign_results = []
    for match_result in match_results:
        user_id = match_result["user_id"]
        user_matched_categories = list(
            set([m["category"] for m in match_result.get("matched_interests", [])]))

        user_images = []
        for category in user_matched_categories:
            trend_image = image_service.get_trend_image(category)
            if trend_image:
                user_images.append({
                    "trend_category": category,
                    "image_url": trend_image.get("image_url"),
                    "prompt_used": trend_image.get("prompt_used"),
                    "status": "generated"
                })

        if not user_images:
            user_images = [{
                "trend_category": "default",
                "image_url": None,
                "status": "no_matching_trends",
                "message": "No images generated for user's matched trends"
            }]

        result = {
            "user_id": user_id,
            "user_name": match_result["user_name"],
            "matched_interests": match_result["matched_interests"],
            "match_count": match_result["match_count"],
            "generated_images": user_images,
            "images_count": len([img for img in user_images if img.get("image_url")])
        }
        campaign_results.append(result)

    logger.info(
        f"✅ Step 8 Complete: Mapped images to {len(campaign_results)} users")
    logger.info("=" * 70)
    logger.info("🎉 CAMPAIGN GENERATION COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info("📊 API USAGE STATISTICS:")
    logger.info(
        f"   • OpenAI GPT-4o-mini calls: {api_calls['openai_gpt4o_mini']}")
    logger.info(f"   • OpenAI GPT-4o calls: {api_calls['openai_gpt4o']}")
    logger.info(
        f"   • Black Forest image generations: {api_calls['black_forest']}/{MAX_IMAGES_PER_CAMPAIGN}")
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
        "selected_trends_count": len(selected_trends),
        "selected_trends": [{"category": t["category"], "interests": t["interests"], "user_matches": trend_user_counts.get(t["category"], 0)} for t in selected_trends],
        "trend_images_generated": len(trend_images),
        "users_targeted": len(campaign_results),
        "total_user_images_mapped": total_images_generated,
        "api_usage": {
            "openai_gpt4o_mini_calls": api_calls["openai_gpt4o_mini"],
            "openai_gpt4o_calls": api_calls["openai_gpt4o"],
            "black_forest_calls": api_calls["black_forest"],
            "total_openai_calls": api_calls["openai_gpt4o_mini"] + api_calls["openai_gpt4o"],
            "image_limit": MAX_IMAGES_PER_CAMPAIGN,
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
