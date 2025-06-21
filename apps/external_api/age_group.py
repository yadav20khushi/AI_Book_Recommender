from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache


#User will land here if they select Age Group

class AgeGroupRecommendationFlow(ExternalAPIService):
    def __init__(self, lib_code="127058", age_group="overall"):  #we can hard code the age groups on the user interface
        #lib_code=127058 is by default
        self.lib_code = lib_code
        self.age_group = age_group
        self.url = f"https://data4library.kr/api/extends/loanItemSrchByLib?authKey={self.auth_key}&libCode={self.lib_code}&format=json"

    @api_cache(ttl=3600)
    def get_books_by_agegroup(self):
        res = self.get_json(self.url, fallback_data={})

        age_group_mapping = {
            "overall": "loanBooks",
            "infant": "age0Books",
            "toddler": "age6Books",
            "elementary": "age8Books",
            "teen": "age14Books",
            "adult": "age20Books"
        }

        # Default to 'loanBooks' if key is missing or age group not found
        book_key = age_group_mapping.get(self.age_group.lower(), "loanBooks")
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
        return books #Will be shown to user and the book selected by user will trigger users_selected_book.py
