from apps.books.models import Book
from apps.external_api.services import get_book_info
import random
def fetch_from_naru(isbn: str, title: str = None, author: str = None) -> Book:
    try:
        book_data = get_book_info(isbn)
        book, _ = Book.objects.get_or_create(
            isbn=book_data["isbn"],
            defaults={
                "title": book_data["title"],
                "author": book_data["author"],
                "summary": book_data["summary"],
                "cover_url": book_data["cover_url"]
            }
        )
        print('[DEBUG] Book fetched and saved via External API')
        return book

    except Exception as e:
        print(f"[ERROR] External API failed: {e}")
        # fallback mock
        book, _ = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                "title": title or "Unknown Title",
                "author": author or "Unknown Author",
                "summary": "Fallback summary.",
                "cover_url": "https://example.com/fallback.jpg"
            }
        )
        return book

# To only check if a book exists in db and if not then trigger external_api then save in db and return to recommendations
def get_or_fetch_book(title: str, author: str, isbn: str = None) -> Book:
    try:
        return Book.objects.get(title=title, author=author)
    except Book.DoesNotExist:
        if isbn:
            return fetch_from_naru(isbn, title, author)
        else:
            # fallback mock ISBN just for testing
            fake_isbn = f"978{random.randint(1000000000, 9999999999)}"
            return fetch_from_naru(fake_isbn, title, author)


