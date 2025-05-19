from apps.books.models import book
def fetch_from_naru(title: str, author: str) -> book:
    mock_response = {
        "isbn": "9781234567890",
        "title": title,
        "author": author,
        "summary": f"A great book called {title} by {author}.",
        "cover_url": "https://example.com/cover.jpg"
    }
    Book = book.objects.create(**mock_response)
    print("[debug] Fetched and saved:", Book)
    return Book

def get_or_fetch_book(title: str, author: str) -> book:
    try:
        Book = book.objects.get(title__iexact=title, author__iexact=author)
        print(f'[DEBUG] found {Book} in DB')
        return Book
    except book.DoesNotExist:
        print(f"[DEBUG] {Book} not available in DB, fetching using Naru API")
        return fetch_from_naru(title,author)


