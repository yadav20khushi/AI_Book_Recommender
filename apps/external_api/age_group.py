from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache

class AgeGroupRecommendationFlow(ExternalAPIService):
    def __init__(self, auth_key, lib_code="127058"):
        super().__init__()
        self.auth_key = auth_key
        self.lib_code = lib_code
        self.url = f"https://data4library.kr/api/extends/loanItemSrchByLib?authKey={self.auth_key}&libCode={self.lib_code}&format=json"

    @api_cache(3600)
    def get_cached_json(self):
        return self.get_json(self.url, fallback_data={})
    def get_books_by_agegroup(self, age_group):

        age_group_mapping = {
            "overall": "loanBooks",
            "infant": "age0Books",
            "toddler": "age6Books",
            "elementary": "age8Books",
            "teen": "age14Books",
            "adult": "age20Books"
        }

        # Fallback to 'loanBooks' if invalid
        book_key = age_group_mapping.get(age_group.lower(), "loanBooks")
        res = self.get_cached_json()
        raw_books = res.get("response", {}).get(book_key, [])

        books = []
        for item in raw_books:
            book = item.get("book", {})
            books.append({
                "title": book.get("bookname", "N/A"),
                "authors": book.get("authors", "N/A"),
                "isbn13": book.get("isbn13", "N/A"),
                "cover": book.get("bookImageURL", "N/A")
            })

        return books