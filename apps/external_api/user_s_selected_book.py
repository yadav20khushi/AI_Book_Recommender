from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache

class UsersSelectedBook(ExternalAPIService):
    def __init__(self, auth_key):
        super().__init__(auth_key=auth_key)  # call parent init to set up auth_key etc.

    def get_description(self, isbn13: str):

        url = f"https://data4library.kr/api/usageAnalysisList?authKey={self.auth_key}&isbn13={isbn13}&format=json&loanInfoYN=N"
        res = self.get_json(url, fallback_data={})
        data = res.get('response', {}).get('book', {})

        book_desc = [{
            'title': data.get('bookname', 'N/A'),
            'authors': data.get('authors', 'N/A'),
            'isbn13': data.get('isbn13', 'N/A'),
            'description': data.get('description', 'N/A'),
            'cover': data.get('bookImageURL', '')
        }]

        return book_desc


    @api_cache(3600)
    def get_similar_books(self, isbn13: str, recommendation_type: str = "reader"):
        if recommendation_type not in ["reader", "mania"]:
            recommendation_type = "reader"  # fallback

        url = f"http://data4library.kr/api/recommandList?authKey={self.auth_key}&isbn13={isbn13}&type={recommendation_type}&format=json"

        #print("SIMILAR BOOKS URL:", url)

        res = self.get_json(url, fallback_data={})
        parsed = []

        #print("RESPONSE FROM API:", json.dumps(res, indent=2, ensure_ascii=False))

        for item in res.get("response", {}).get("docs", [])[:10]:
            book_data = item.get("book", {})
            parsed.append({
                "title": book_data.get("bookname"),
                "isbn13": book_data.get("isbn13"),
                "author": book_data.get("authors"),
                "cover": book_data.get("bookImageURL")
            })
        return parsed

    @api_cache(3600)
    def check_availability(self, isbn13: str, lib_code: str) -> str:
        """
        Trigger only if user wants to check book's availability
        """
        url = f"https://data4library.kr/api/bookExist?authKey={self.auth_key}&libCode={lib_code}&isbn13={isbn13}&format=json"
        res = self.get_json(url)
        if res.get('response', {}).get('result', {}).get('hasBook') == 'Y':
            return "해당 도서는 선택하신 도서관에서 이용하실 수 있습니다."  #Return in korean
        else:
            return "죄송하지만, 해당 도서가 현재 선택하신 도서관에는 비치되어 있지 않습니다."