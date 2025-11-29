import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure repo root is on sys.path so imports (TrendWebScraping.*) succeed when running this file directly from backend/
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from TrendWebScraping.GoogleTrendsScraper import GoogleTrendsScraper
#from TrendWebScraping.TwitterTrendsScraper import TwitterTrendsScraper
from filter_trends import filter_data_with_openai



def main():
    # ---------------- Google Trends ----------------

    scraper = GoogleTrendsScraper(json_file="google_trends.json")
    
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
            "Return them in the same form, just delete the unsuitable ones."
        )
        try:
            print("Calling filter_data_with_openai with current trends and OPENAI_API_KEY...")
            filtered = filter_data_with_openai(trends, instruction=instruction, api_key=api_key, api_output='filtered_trends.json')
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



app = FastAPI(title="Dynamic Ads Content API")

# CORS-Konfiguration für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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