import json
import feedparser
import openai

class GoogleTrendsScraper:
    def __init__(self, country: str = "DE", json_file: str = "google_trends.json"):
        """
        country: ISO Code oder Google Trends Geo-Code (DE, US, ...)
        """
        self.country = country.upper()
        self.json_file = json_file
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
