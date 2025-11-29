import json
from pytrends.request import TrendReq
import openai

class TrendScraper:
    def __init__(self, country: str, json_file: str = "trends.json"):
        """
        country: ISO-Ländercode, z.B. 'DE', 'US', 'FR'
        json_file: Name der Datei, in der Trends gespeichert werden
        """
        self.country = country.upper()   # Realtime API nutzt ISO-Codes
        self.json_file = json_file
        self.trends = {}

    def scrape_trends(self):
        """Scrape aktuelle Google Realtime Trends und speichere sie als JSON"""
        pytrends = TrendReq(hl='de', tz=360)

        try:
            # Realtime-Trends abrufen (funktioniert 2024/2025 sicher)
            data = pytrends.realtime_trending_searches(pn=self.country)
        except Exception as e:
            print("Fehler beim Abrufen der Realtime Trends:", e)
            return

        # Trends extrahieren
        trending_raw = data.get("trendingSearches", [])
        if not trending_raw:
            print("Keine Trends gefunden. Prüfe den country-Code.")
            return

        # "title -> query" extrahieren
        self.trends = {
            str(i + 1): item["title"]["query"]
            for i, item in enumerate(trending_raw)
        }

        # In JSON speichern
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.trends, f, ensure_ascii=False, indent=4)

        print(f"{len(self.trends)} Trends erfolgreich gespeichert!")

    def print_trends(self):
        """Gibt die aktuell gespeicherten Trends aus"""
        if not self.trends:
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.trends = json.load(f)
            except FileNotFoundError:
                print("Keine Trends gefunden. Bitte zuerst scrape_trends() ausführen.")
                return
        
        print(f"Aktuelle Trends für {self.country}:")
        for rank, trend in self.trends.items():
            print(f"{rank}. {trend}")

    def filter_trends_with_gpt(self, api_key: str, prompt: str):
        """
        Schickt die Trends an die ChatGPT API und filtert nützliche Trends heraus.
        """
        if not self.trends:
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    self.trends = json.load(f)
            except FileNotFoundError:
                print("Keine Trends gefunden. Bitte zuerst scrape_trends() ausführen.")
                return

        openai.api_key = api_key

        trends_list = "\n".join(f"{rank}. {trend}" for rank, trend in self.trends.items())
        full_prompt = f"{prompt}\nHier ist die Liste der Trends:\n{trends_list}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Marketing-Experte."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=300
        )

        return response['choices'][0]['message']['content']