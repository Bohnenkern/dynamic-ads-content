from fastapi import APIRouter, HTTPException
from typing import Optional
from services.trend_analysis import trend_service

router = APIRouter()


@router.get("/trends")
async def get_trends():
    """
    Gibt alle aktuellen Trenddaten zurück
    """
    trends = trend_service.get_cached_trends()
    
    if "message" in trends:
        raise HTTPException(status_code=404, detail=trends["message"])
    
    return trends


@router.get("/trends/refresh")
async def refresh_trends():
    """
    Aktualisiert die Trenddaten durch erneuten API-Aufruf
    """
    trends = await trend_service.fetch_user_interests()
    
    if "error" in trends:
        raise HTTPException(status_code=500, detail=trends["error"])
    
    return {
        "message": "Trends erfolgreich aktualisiert",
        "data": trends
    }


@router.get("/trends/category/{category}")
async def get_trends_by_category(category: str):
    """
    Gibt Trends für eine spezifische Kategorie zurück
    """
    trends = trend_service.get_trends_by_category(category)
    
    if "error" in trends:
        raise HTTPException(status_code=404, detail=trends["error"])
    
    return trends


@router.get("/trends/top")
async def get_top_interests(limit: Optional[int] = 5):
    """
    Gibt die Top N Interessen zurück
    """
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="Limit muss zwischen 1 und 50 liegen")
    
    top_interests = trend_service.get_top_interests(limit=limit)
    
    if not top_interests:
        raise HTTPException(status_code=404, detail="Keine Trenddaten verfügbar")
    
    return {
        "count": len(top_interests),
        "interests": top_interests
    }
