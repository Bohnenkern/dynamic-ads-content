from GoogleTrendsScraper import GoogleTrendsScraper
from TwitterTrendsScraper import TwitterTrendsScraper

def main():
    # Scraper initialisieren
    scraper = GoogleTrendsScraper(json_file="google_trends.json")
    
    # Länderliste definieren
    countries = ["DE", "US", "FR", "GB", "IT", "ES", "JP", "BR", "CA", "AU"]
    
    print("🌍 Google Trends Multi-Country Scraper")
    print("=" * 50)
    
    # 1. Für alle Länder scrapen
    all_trends = scraper.scrape_multiple_countries(countries)
    
    # 3. Statistiken anzeigen
    stats = scraper.get_country_stats()
    print(f"\n📊 ZUSAMMENFASSUNG:")
    for country, data in stats.items():
        print(f"{country}: {data['total_trends']} Trends")
        if data['top_trends']:
            print(f"   Top: {', '.join(data['top_trends'])}")

if __name__ == "__main__":
    main()