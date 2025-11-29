from dotenv import load_dotenv
load_dotenv()

from services.trend_analysis import trend_service
from services.user_data import user_service
from routers import trends, users
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging


# CRITICAL: Load .env FIRST before ANY other imports
# Services create singleton instances on import and need API keys immediately

# Now safe to import everything else


# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle-Handler für Startup und Shutdown"""
    # Startup
    logger.info("Starte Dynamic Ads Content API...")

    # Lade User-Daten
    logger.info("Lade User-Daten...")
    user_service.load_users()

    # Initialisiere Trendanalyse
    logger.info("Initialisiere Trendanalyse...")
    await trend_service.fetch_user_interests()
    logger.info("Trendanalyse erfolgreich initialisiert")

    yield

    # Shutdown
    logger.info("Beende Dynamic Ads Content API...")


app = FastAPI(
    title="Dynamic Ads Content API",
    lifespan=lifespan
)

# CORS-Konfiguration für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(trends.router, prefix="/api/v1", tags=["trends"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])


@app.get("/")
async def root():
    return {"message": "Welcome to Dynamic Ads Content API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
