'''
    users_selected_book calls clova by passing a list of dict of
    books metadata + desc. We want to pass this to clova, along with
    a prompt which tells it to communicate and explain about the book
    and answer followup questions. Also, we want to save only the book
    info data in userhistory db
'''
import requests
from datetime import datetime
from apps.recommendations.models import UserHistory
from apps.books.models import Book
import os

CLOVA_API_URL = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")

def call_clova(book_metadata: list[dict], username: str):
    if not book_metadata:
        return "No book data provided."

    selected = book_metadata[0]  # assuming single selected book
    title = selected.get("title", "N/A")
    author = selected.get("authors", "N/A")
    description = selected.get("description", "N/A")
    isbn13 = selected.get("isbn13", "N/A")
    cover = selected.get("cover", "")

    # Clova Prompt - Need a good korean prompt!
    user_prompt = (
        f"Please explain the following book to me like I am a curious reader:\n\n"
        f"Title: {title}\nAuthor: {author}\nDescription: {description}\n\n"
        f"Answer my questions about it in detail."
    )

    headers = {
        "Authorization": f"Bearer {CLOVA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that deeply understands books."},
            {"role": "user", "content": user_prompt}
        ],
        "maxTokens": 1024,
        "temperature": 0.7,
        "topP": 0.8,
    }

    try:
        response = requests.post(CLOVA_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # return Clova's answer
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Failed to contact Clova: {e}"

    # Save book + user history
    book_obj, _ = Book.objects.get_or_create(
        isbn13=isbn13,
        defaults={
            "title": title,
            "author": author,
            "summary": description,
            "cover_url": cover
        }
    )

    now = datetime.now()
    UserHistory.objects.create(
        username=username,
        book=book_obj,
        session_start=now,
        session_end=now  # update end later if needed
    )

    return clova_reply #Connect with user interface so that user's followup questions are sent here
