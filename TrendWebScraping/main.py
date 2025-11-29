from GoogleTrendsScraper import GoogleTrendsScraper
from TwitterTrendsScraper import TwitterTrendsScraper

def main():
    # ---------------- Google Trends ----------------
    google_scraper = GoogleTrendsScraper(country="DE")
    google_scraper.scrape_trends()
    google_scraper.print_trends()

    # Optional GPT Filter
    # api_key = "DEIN_OPENAI_API_KEY"
    # prompt = "Gib mir die 5 relevantesten Trends für eine Werbekampagne."
    # print(google_scraper.filter_trends_with_gpt(api_key, prompt))

    # ---------------- Twitter Trends ----------------
    #twitter_scraper = TwitterTrendsScraper(woeid=23424829)  # DE WOEID
    #bearer_token = "DEIN_TWITTER_BEARER_TOKEN"
    #twitter_scraper.scrape_trends(bearer_token)
    #twitter_scraper.print_trends()

if __name__ == "__main__":
    main()
