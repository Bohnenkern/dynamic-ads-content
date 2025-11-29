from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from services.user_data import user_service
from services.trend_matcher import trend_matcher
from services.trend_analysis import trend_service
from prompts.openai_service import openai_service
from prompts.trend_filter import trend_filter_service
from prompts.image_prompt_builder import image_prompt_builder
from prompts.image_generation import image_service

router = APIRouter()


class CampaignRequest(BaseModel):
    """Request model for campaign generation"""
    product_description: str
    campaign_theme: Optional[str] = "general marketing campaign"
    company_values: Optional[List[str]] = None


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
async def generate_campaign(request: CampaignRequest):
    """
    Complete workflow for personalized ad campaign generation:
    1. Filter trends for campaign suitability
    2. Match filtered trends with user interests
    3. Generate text prompts with OpenAI
    4. Build structured image prompts
    5. Generate images with Black Forest Labs

    Args:
        product_description: Description of the product to advertise
        campaign_theme: Theme of the marketing campaign
        company_values: List of company values to uphold
    """

    # Step 1: Get and filter trends
    trends_data = trend_service.get_cached_trends()
    if "message" in trends_data or "error" in trends_data:
        raise HTTPException(status_code=404, detail="No trend data available")

    trends = trends_data.get("trends", [])
    if not trends:
        raise HTTPException(status_code=404, detail="No trends found")

    # Filter trends for campaign suitability
    filtered_trends = await trend_filter_service.filter_trends_for_campaign(
        trends=trends,
        campaign_theme=request.campaign_theme,
        company_values=request.company_values
    )

    if not filtered_trends:
        raise HTTPException(
            status_code=400,
            detail="No suitable trends found after filtering for campaign safety"
        )

    # Step 2: Match filtered trends with users
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
        raise HTTPException(
            status_code=404, detail="No users found for matching")

    # Step 3: Build base structured prompts (rule-based, fast)
    structured_prompts = {}
    user_matches = {}

    for match_result in match_results:
        if match_result.get("matched_interests"):
            user_id = match_result["user_id"]
            user_data = user_service.get_user_by_id(user_id)

            if user_data:
                # Build structured base prompt
                structured_prompt = image_prompt_builder.build_structured_prompt(
                    product_description=request.product_description,
                    user_data=user_data,
                    matched_interests=match_result["matched_interests"]
                )
                structured_prompts[user_id] = structured_prompt
                user_matches[user_id] = match_result

    # Step 4: Optimize prompts with OpenAI (LLM refinement)
    optimized_prompts = await openai_service.optimize_prompts_for_all_users(
        product_description=request.product_description,
        structured_prompts=structured_prompts,
        user_matches=user_matches
    )

    # Step 5: Generate images with Black Forest Labs using optimized prompts
    generated_images = await image_service.generate_images_for_users(
        structured_prompts=optimized_prompts,  # Now using optimized text prompts
        product_name=request.product_description.split()[0]
    )

    # Combine all results
    campaign_results = []
    for match_result in match_results:
        user_id = match_result["user_id"]

        result = {
            "user_id": user_id,
            "user_name": match_result["user_name"],
            "matched_interests": match_result["matched_interests"],
            "match_count": match_result["match_count"],
            "base_prompt_structure": structured_prompts.get(user_id, {}),
            "optimized_image_prompt": optimized_prompts.get(user_id, "No prompt generated"),
            "generated_image": generated_images.get(user_id, {"status": "not generated"})
        }
        campaign_results.append(result)

    return {
        "campaign_theme": request.campaign_theme,
        "product_description": request.product_description,
        "total_trends_analyzed": len(trends),
        "filtered_trends_count": len(filtered_trends),
        "users_targeted": len(campaign_results),
        "images_generated": len(generated_images),
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
