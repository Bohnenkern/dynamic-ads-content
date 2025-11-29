from fastapi import APIRouter, HTTPException
from typing import List
from services.user_data import user_service
from services.trend_matcher import trend_matcher
from services.openai_service import openai_service

router = APIRouter()


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
        raise HTTPException(status_code=404, detail=f"User mit ID {user_id} nicht gefunden")
    
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
        raise HTTPException(status_code=404, detail="Keine User zum Matchen gefunden")
    
    return {
        "count": len(results),
        "results": results
    }


@router.post("/generate-prompts")
async def generate_all_prompts():
    """
    Führt vollständigen Workflow durch:
    1. Trend-Matching für alle User
    2. Prompt-Generierung für alle User mit Matches
    """
    # Schritt 1: Trend-Matching
    match_results = trend_matcher.match_all_users()
    
    if not match_results:
        raise HTTPException(status_code=404, detail="Keine User gefunden")
    
    # Schritt 2: Prompt-Generierung
    prompts = await openai_service.generate_prompts_for_all_users(match_results)
    
    # Kombiniere Ergebnisse
    combined_results = []
    for match_result in match_results:
        user_id = match_result["user_id"]
        combined_results.append({
            "user_id": user_id,
            "user_name": match_result["user_name"],
            "matched_interests": match_result["matched_interests"],
            "match_count": match_result["match_count"],
            "generated_prompt": prompts.get(user_id, "Kein Prompt generiert (keine Matches)")
        })
    
    return {
        "count": len(combined_results),
        "results": combined_results
    }


@router.get("/prompts/{user_id}")
async def get_user_prompt(user_id: int):
    """Gibt generierten Prompt für einen User zurück"""
    prompt = openai_service.get_cached_prompt(user_id)
    
    if not prompt:
        raise HTTPException(
            status_code=404, 
            detail="Kein Prompt für diesen User gefunden. Bitte zuerst generate-prompts aufrufen."
        )
    
    return {
        "user_id": user_id,
        "prompt": prompt
    }


@router.get("/prompts")
async def get_all_prompts():
    """Gibt alle generierten Prompts zurück"""
    prompts = openai_service.get_all_cached_prompts()
    
    if not prompts:
        raise HTTPException(
            status_code=404, 
            detail="Keine Prompts gefunden. Bitte zuerst generate-prompts aufrufen."
        )
    
    return {
        "count": len(prompts),
        "prompts": prompts
    }
