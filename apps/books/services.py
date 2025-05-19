from apps.books.models import Book
import random
def fetch_from_naru(title: str, author: str) -> Book:
    mock_response = {
        "isbn": f"978{random.randint(1000000000, 9999999999)}",
        "title": title,
        "author": author,
        "summary": f"A great book called {title} by {author}.",
        "cover_url": "https://example.com/cover.jpg"
    }
    book, created = Book.objects.get_or_create(
        isbn=mock_response["isbn"],
        defaults=mock_response
    )
    #if not created: #this is a testing bug debug; mock_response isbn always same where isnb unique = True
        #print(f"[DEBUG] Book with ISBN {mock_response['isbn']} already exists. Using existing entry.")

    print('[debug] book fetched and saved in DB')
    return book

def get_or_fetch_book(title: str, author: str) -> Book:
    try:
        book = Book.objects.get(title__iexact=title, author__iexact=author)
        print(f'[DEBUG] found {Book} in DB')
        return book
    except Book.DoesNotExist:
        print(f"[DEBUG] book not available in DB, fetching using Naru API")
        return fetch_from_naru(title,author)


