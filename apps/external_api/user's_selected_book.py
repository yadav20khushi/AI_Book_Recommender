from apps.recommendations.recommendation import call_clova
from apps.external_api.base import ExternalAPIService
from apps.caching.cache import api_cache

class UsersSelectedBook(ExternalAPIService):
    def __init__(self, username: str):
        self.username = username
        super().__init__()  # call parent init to set up auth_key etc.

    def get_description(self, isbn13: str):
        """
        Trigger this for the book user selects from the bookList_page.html.
        Fetch book description and pass metadata + description to Clova.
        And display on clovaChat_page.html
        """
        url = f"https://data4library.kr/api/usageAnalysisList?authKey={self.auth_key}&isbn13={isbn13}&format=json&loanInfoYN=N"
        res = self.get_json(url, fallback_data={})
        data = res.get('response', {}).get('book', {})

        book_desc = [{
            'title': data.get('bookname', 'N/A'),
            'authors': data.get('authors', 'N/A'),
            'isbn13': data.get('isbn13', 'N/A'),
            'description': data.get('description', 'N/A')
        }]

        # Pass book description + username to Clova
        call_clova(book_desc, username=self.username)

        """
            After when the clova responds i.e exaplains the description then tiles will pop up
            with 1. similar books for readers  2. similar books for advanced readers 3. check book availability
            then the user can choose from these or ask a follow up question, but every time the clova responds, at 
            the end the pop ups will be shown.
        """

    @api_cache(ttl=3600)
    def get_similar_books(self, isbn13: str, recommendation_type: str = "reader"):
        if recommendation_type not in ["reader", "mania"]:
            recommendation_type = "reader"  # fallback

        url = f"http://data4library.kr/api/recommandList?authKey={self.auth_key}&isbn13={isbn13}&type={recommendation_type}&format=json"
        '''
            Later we can pass multiple isbns for personalised recommendations
        '''

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
        return parsed  # Will be shown to user and the book selected by user will trigger user's_selected_book.py

    @api_cache(ttl=3600)
    def check_availability(self, isbn13: str, lib_code: str) -> str:
        """
        Trigger only if user wants to check book's availability
        """
        url = f"https://data4library.kr/api/bookExist?authKey={self.auth_key}&libCode={lib_code}&isbn13={isbn13}&format=json"
        res = self.get_json(url)
        if res.get('response', {}).get('result', {}).get('hasBook') == 'Y':
            return "The Book is available in the library"  #Return in korean
        else:
            return "The Book is not available in the library"
