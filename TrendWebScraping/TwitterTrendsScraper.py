import json
import requests
import openai

class TwitterTrendsScraper:
    def __init__(self, woeid: int = 23424829, json_file: str = "twitter_trends.json"):
        """
        woeid: Where On Earth ID (23424829 = Deutschland)
        """
        self.woeid = woeid
        self.json_file = json_file
        self.trends = {}

    def scrape_trends(self, bearer_token: str):
        """Scrape Twitter/X Trending Topics via API"""
        url = f"https://api.twitter.com/1.1/trends/place.json?id={self.woeid}"
        headers = {"Authorization": f"Bearer {bearer_token}"}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Fehler beim Abrufen der Twitter Trends:", response.status_code, response.text)
            return

        data = response.json()
        trends_list = data[0]["trends"]
        self.trends = {str(i+1): t["name"] for i, t in enumerate(trends_list)}

        # In JSON speichern
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.trends, f, ensure_ascii=False, indent=4)

        print(f"{len(self.trends)} Twitter Trends erfolgreich gespeichert!")

    def print_trends(self):
        if not self.trends:
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    self.trends = json.load(f)
            except FileNotFoundError:
                print("Keine Trends gefunden. scrape_trends() zuerst ausführen.")
                return

        print(f"Aktuelle Twitter Trends (WOEID {self.woeid}):")
        for rank, trend in self.trends.items():
            print(f"{rank}. {trend}")

    def filter_trends_with_gpt(self, api_key: str, prompt: str):
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
