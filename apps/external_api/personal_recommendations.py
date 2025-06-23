from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache
from apps.recommendations.models import UserHistory
from apps.books.models import Book
import pdb

class ReturningUserRecommendationFlow(ExternalAPIService):
    def __init__(self, username: str):
        self.username = username
        super().__init__()

    def get_user_isbns(self):
        #pdb.set_trace()
        histories = (
            UserHistory.objects
            .filter(user__username=self.username)
            .order_by('-session_end')
            .select_related('book')
        )

        seen = set()
        ordered_isbns = []

        for h in histories:
            isbn = h.book.isbn13 if h.book else None
            if isbn and isbn not in seen:
                seen.add(isbn)
                ordered_isbns.append(isbn)
            if len(ordered_isbns) == 3:
                break

        return ordered_isbns

    @api_cache(3600)
    def get_avid_reader_recommendations(self):
        #pdb.set_trace()
        isbns = self.get_user_isbns()
        if not isbns:
            return []

        isbn_param = ";".join(isbns)  # API expects semicolon-separated string

        url = f"http://data4library.kr/api/recommandList?authKey={self.auth_key}&isbn13={isbn_param}&type=reader&format=json"
        res = self.get_json(url, fallback_data={})
        parsed = []
        for item in res.get("response", {}).get("docs", [])[:10]:
            book_data = item.get("book", {})
            parsed.append({
                "title": book_data.get("bookname"),
                "isbn13": book_data.get("isbn13"),
                "author": book_data.get("authors"),
                "cover": book_data.get("bookImageURL")
            })

        return parsed
