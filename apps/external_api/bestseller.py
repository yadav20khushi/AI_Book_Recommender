from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache

#User will land here if they select Bestseller
class BestsellerRecommendation(ExternalAPIService):
    def __init__(self, lib_code="127058"): #lib_code by default else pick what user chooses from the interface
        self.lib_code = lib_code
        self.url = f"https://data4library.kr/api/loanItemSrchByLib?authKey={self.auth_key}&libCode={self.lib_code}&pageSize=10&format=json"

    @api_cache(3600)
    def get_bestseller_books(self):
        res = self.get_json(self.url, fallback_data={})
        parsed = []
        for item in res.get("response", {}).get("docs", []):
            book_data = item.get("doc", {})
            parsed.append({
                "title": book_data.get("bookname"),
                "isbn13": book_data.get("isbn13"),
                "author": book_data.get("authors"),
                "cover": book_data.get("bookImageURL") #Display to user
            })
        return parsed #Will be shown to user and the book selected by user will trigger user's_selected_book.py