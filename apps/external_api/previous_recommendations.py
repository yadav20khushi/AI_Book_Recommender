'''
    connect with returningUser_page.html, where just like YouTube, 10 books {their cover image, name and author}
    will already be displayed using the avid readers api, where will fetch previous browsed books isbn saved in
    book db/ userHistory db then pass this list of isbns to the api and display to user, where the user will select a book and then
    users_selected_book.py flow will be triggered
'''
from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache
from apps.recommendations.models import UserHistory
from apps.books.models import Book

class ReturningUserRecommendationFlow(ExternalAPIService):
    def __init__(self, username: str):
        self.username = username
        super().__init__()

    def get_user_isbns(self):
        # Get last 10 unique ISBNs viewed by the user
        histories = UserHistory.objects.filter(username=self.username).order_by('-session_end').select_related('book')
        isbns = list({h.book.isbn13 for h in histories if h.book and h.book.isbn13})[:10]
        return isbns

    @api_cache(ttl=3600)
    def get_avid_reader_recommendations(self):
        isbns = self.get_user_isbns()
        if not isbns:
            return []

        isbn_param = ";".join(isbns)  # API expects semicolon-separated string

        url = f"http://data4library.kr/api/recommandList?authKey={self.auth_key}&isbn13={isbn_param}&type=reader&format=json"
        res = self.get_json(url, fallback_data={})
        parsed = []

        for item in res.get("response", {}).get("docs", [])[:10]:
            book_data = item.get("doc", {})
            parsed.append({
                "title": book_data.get("bookname", "N/A"),
                "isbn13": book_data.get("isbn13", "N/A"),
                "author": book_data.get("authors", "N/A"),
                "cover": book_data.get("bookImageURL", "")
            })

        return parsed  # To render in returningUser_page.html
