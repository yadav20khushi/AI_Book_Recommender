"""
    When the user selects keyword on the home_page.html, this api will be triggered and the top 10
    keywords will be shown on keyword_page.html
"""
from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache
from apps.books.models import Book
from django.core.cache import cache

class KeywordRecommendationFlow(ExternalAPIService):
    def __init__(self, auth_key,month=None):
        self.month = month or self.get_current_month()
        self.auth_key = auth_key
    def get_current_month(self):
        from datetime import datetime, timedelta
        first = datetime.today().replace(day=1)
        prev_month = first - timedelta(days=1)
        return prev_month.strftime("%Y-%m")

    @api_cache(3600)  # ⏱ 1 hour cache
    def get_monthly_keywords(self):
        url = f"https://data4library.kr/api/monthlyKeywords?authKey={self.auth_key}&month={self.month}&format=json"
        print("Fetching from URL:", url)
        # Logic to fetch top 10 keywords only
        res = self.get_json(url, fallback_data=[])
        #print("Raw response:", res)
        keywords = []
        words = res.get('response',{}).get('keywords',[])
        #print("Parsed keywords list:", words)
        for item in words[:10]:
            keyword_data = item.get("keyword", {})
            keywords.append(keyword_data.get("word", "N/A"))

        return keywords 

    @api_cache(3600)
    def get_books_by_keyword(self, keyword): #The user's selected keyword
        url = f"https://data4library.kr/api/srchBooks?authKey={self.auth_key}&keyword={keyword}&format=json"
        res = self.get_json(url, fallback_data=[])
        parsed = []
        for item in res.get("response", {}).get("docs", [])[:10]:
            book_data = item.get("doc", {})
            parsed.append({
                "title": book_data.get("bookname"),
                "isbn13": book_data.get("isbn13"),
                "author": book_data.get("authors"),
                "cover": book_data.get("bookImageURL") #Display to user
            })
        return parsed 


