from dotenv import load_dotenv
load_dotenv()

from services.trend_analysis import trend_service
from services.user_data import user_service
from routers import trends, users
import os
import sys
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
# Ensure repo root is on sys.path so imports (TrendWebScraping.*) succeed when running this file directly from backend/
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from TrendWebScraping.GoogleTrendsScraper import GoogleTrendsScraper
#from TrendWebScraping.TwitterTrendsScraper import TwitterTrendsScraper
from filter_trends import filter_data_with_openai



def main():
    # ---------------- Google Trends ----------------

    scraper = GoogleTrendsScraper()
    
    # Länderliste definieren
    countries = ["DE", "US", "FR", "GB", "IT", "ES", "JP", "BR", "CA", "AU"]
    
    print("🌍 Google Trends Multi-Country Scraper")
    print("=" * 50)
    
    # 1. Für alle Länder scrapen
    trends = scraper.scrape_multiple_countries(countries)
    
    scraper.print_trends()
    

    # Optional GPT Filter — call the reusable function in backend/filter_trends
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        instruction = (
            "From the following trending topics, find those which are suitable to be merged into general marketing campaigns. "
            "The connection may be broad. Hard constraints are for example, but not limited to: topics that are negative, political, religious, racist, sexist, illegal, associated with certain people, drugs or weapons. "
            "Return them in the same form, just delete the unsuitable ones. in that sense, make sure to only return a valid JSON object with the same keys as the input, but only the filtered trends as values."
        )
        try:
            print("Calling filter_data_with_openai with current trends and OPENAI_API_KEY...")
            filtered = filter_data_with_openai(trends, instruction=instruction, api_key=api_key)
            print('Filtered trends (from API):')
            print(filtered)
        except Exception as e:
            print('Error while filtering trends with OpenAI:', e)
    else:
        print('OPENAI_API_KEY not set — skipping GPT-based filter. To enable, set OPENAI_API_KEY in environment or .env and restart.')

    # ---------------- Twitter Trends ----------------
    #twitter_scraper = TwitterTrendsScraper(woeid=23424829)  # DE WOEID
    #bearer_token = "DEIN_TWITTER_BEARER_TOKEN"
    #twitter_scraper.scrape_trends(bearer_token)
    #twitter_scraper.print_trends()




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
        main()