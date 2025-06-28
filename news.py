import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os

load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API')

def extract_full_text_from_url(url):
    """Attempt to extract the full text from an article URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Collect all paragraph text
        paragraphs = soup.find_all("p")
  
        content = " ".join(p.get_text() for p in paragraphs if len(p.get_text()) > 50)
     
        return content.strip()
    except Exception as e:
        return f"[Error fetching article body: {e}]"

def get_latest_headlines_and_summaries():
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params).json()

    if response["status"] == "ok" and response["totalResults"] > 0:
        results = []
        for article in response["articles"]:
            title = article.get("title", "")
            url = article.get("url", "")
            content = extract_full_text_from_url(url)
            results.append([title, content])
        return results

    return []

# Example usage
if __name__ == "__main__":
    articles = get_latest_headlines_and_summaries()
    for i, [title, content] in enumerate(articles, start=1):
        print(f"\nArticle {i}:")
        print("Title:", title)
        print(f"Content:\n{content[:500]}...\n")  # Show first 500 chars
