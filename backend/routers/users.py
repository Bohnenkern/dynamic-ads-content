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


class CampaignRequest(BaseModel):
    """Request model for campaign generation (deprecated - use FormData)"""
    product_description: str
    campaign_theme: Optional[str] = "general marketing campaign"
    company_values: Optional[List[str]] = None


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
    company_values: str = Form(default=None)
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
        company_values: JSON string of company values
    """

    # Parse company_values from JSON string
    try:
        values_list = json.loads(company_values) if company_values else [
            "innovative", "premium"]
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse company_values: {company_values}")
        values_list = ["innovative", "premium"]

    logger.info("=" * 70)
    logger.info("🚀 CAMPAIGN GENERATION STARTED")
    logger.info("=" * 70)
    logger.info(f"📱 Product: {product_description}")
    logger.info(f"🎯 Theme: {campaign_theme}")
    logger.info(f"✨ Values: {values_list}")
    logger.info(
        f"🖼️  Image: {product_image.filename} ({product_image.content_type})")
    logger.info("=" * 70)

    # STEP 1: Save uploaded product image
    try:
        image_path = await save_uploaded_image(product_image)
        logger.info(f"✅ Step 1 Complete: Image saved to {image_path}")
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
        company_values=values_list
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

    match_results = trend_matcher.match_all_users()

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
                    matched_interests=match_result["matched_interests"],
                    has_input_image=(image_path is not None)
                )
                structured_prompts[user_id] = structured_prompt
                user_matches[user_id] = match_result

    logger.info(
        f"✅ Step 5 Complete: Built {len(structured_prompts)} structured prompts")

    # STEP 6: Build prompts for each filtered trend category
    logger.info(
        f"🏗️  Step 6: Building prompts for {len(filtered_trends)} trend categories...")
    trend_prompts = {}
    for trend in filtered_trends:
        trend_category = trend["category"]
        trend_interests = trend["interests"]

        structured_prompt = image_prompt_builder.build_prompt_for_trend(
            product_description=product_description,
            trend_category=trend_category,
            trend_interests=trend_interests,
            has_input_image=(image_path is not None)
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

    logger.info(
        f"✅ Step 6 Complete: Built {len(trend_prompts)} trend-specific prompts")

    # STEP 7: Generate images for each trend with Black Forest API
    logger.info(
        f"🎨 Step 7: Generating images for {len(trend_prompts)} trends with Black Forest API...")
    trend_images = await image_service.generate_images_for_trends(
        trend_prompts=trend_prompts,
        product_name=product_description.split()[0],
        input_image_path=image_path
    )

    for trend_category, image_data in trend_images.items():
        image_service.cache_trend_image(trend_category, image_data)

    logger.info(
        f"✅ Step 7 Complete: Generated {len(trend_images)} trend images")

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

    total_images_generated = sum([result["images_count"]
                                 for result in campaign_results])

    return {
        "campaign_theme": campaign_theme,
        "product_description": product_description,
        "product_image_path": image_path,
        "total_trends_analyzed": len(trends),
        "filtered_trends_count": len(filtered_trends),
        "filtered_trends": [{"category": t["category"], "interests": t["interests"]} for t in filtered_trends],
        "trend_images_generated": len(trend_images),
        "users_targeted": len(campaign_results),
        "total_user_images_mapped": total_images_generated,
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
