import json
import feedparser
import openai
import os
from typing import List, Dict


class GoogleTrendsScraper:
    def __init__(self, country: str = "US", json_file: str | None = None):
        """
        country: ISO Code oder Google Trends Geo-Code (DE, US, ...)
        """
        self.country = country.upper()
        # Default JSON file path: backend/google_trends.json relative to repo root
        if json_file:
            self.json_file = json_file
        else:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.json_file = os.path.join(repo_root, 'backend', 'google_trends.json')
        self.trends = {}

        # RSS Feed URL
        self.rss_url = f"https://trends.google.de/trending/rss?geo={self.country}"

    def scrape_trends(self):
        """Scrape aktuelle Google Trends über RSS Feed"""
        feed = feedparser.parse(self.rss_url)
        if not feed.entries:
            print("Keine Google Trends gefunden.")
            return

        self.trends = {str(i+1): entry.title for i, entry in enumerate(feed.entries)}

        # In JSON speichern
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.trends, f, ensure_ascii=False, indent=4)

        print(f"{len(self.trends)} Google Trends erfolgreich gespeichert!")
        # Return the trends dict so callers can use it directly (e.g., for filtering)
        return self.trends

    def print_trends(self):
        if not self.trends:
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    self.trends = json.load(f)
            except FileNotFoundError:
                print("Keine Trends gefunden. scrape_trends() zuerst ausführen.")
                return

        print(f"Aktuelle Google Trends für {self.country}:")
        for rank, trend in self.trends.items():
            print(f"{rank}. {trend}")

    def filter_trends_with_gpt(self, api_key: str, prompt: str):
        """Schickt die Trends an GPT für Marketing-Relevanz"""
        if not self.trends:
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    self.trends = json.load(f)
            except FileNotFoundError:
                print("Keine Trends gefunden. scrape_trends() zuerst ausführen.")
                return

        openai.api_key = api_key
        trends_list = "\n".join(f"{rank}. {trend}" for rank, trend in self.trends.items())
        full_prompt = f"{prompt}\nHier sind die Trends:\n{trends_list}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Marketing-Experte."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=300
        )

        return response["choices"][0]["message"]["content"]
    
    def scrape_multiple_countries(self, countries: List[str]):
        """
        Iteriert über eine Liste von Ländern und speichert ALLE Trends in EINER JSON-Datei
        
        Args:
            countries: Liste von ISO Ländercodes (z.B. ["DE", "US", "FR", "GB"])
        """
        all_country_trends = {}
        
        print(f"Starte Scraping für {len(countries)} Länder...")
        print("=" * 50)
        
        for country in countries:
            country = country.upper()
            print(f"\nScraping Trends für {country}...")
            
            # Temporärer Scraper für dieses Land
            country_scraper = GoogleTrendsScraper(country=country)
            
            # Trends scrapen (aber nicht in separate Datei speichern)
            try:
                feed = feedparser.parse(country_scraper.rss_url)
                if feed.entries:
                    country_trends = {str(i+1): entry.title for i, entry in enumerate(feed.entries)}
                    all_country_trends[country] = country_trends
                    print(f"✅ {country}: {len(country_trends)} Trends")
                else:
                    print(f"❌ {country}: Keine Trends gefunden")
                    all_country_trends[country] = {}
                    
            except Exception as e:
                
                all_country_trends[country] = {}
        
        # ALLE Trends in EINER Datei speichern (der Haupt-JSON-Datei)
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(all_country_trends, f, ensure_ascii=False, indent=4)
        
        print(f"\n" + "=" * 50)
        print(f"Scraping abgeschlossen!")
        print(f"ALLE Trends in '{self.json_file}' gespeichert")
        print(f"Gesamt: {len(all_country_trends)} Länder")
        
        # Trends auch in der Instanz speichern
        self.trends = all_country_trends
        return all_country_trends

    def get_country_stats(self, trends_data: Dict = None) -> Dict:
        """
        Gibt Statistiken zu den gescrapten Länder-Trends zurück
        
        Args:
            trends_data: Optional - Falls nicht angegeben, werden die internen Trends verwendet
        """
        if trends_data is None:
            trends_data = self.trends
        
        stats = {}
        for country, trends in trends_data.items():
            stats[country] = {
                "total_trends": len(trends),
                "top_trends": list(trends.values())[:3] if trends else []
            }
        return stats
