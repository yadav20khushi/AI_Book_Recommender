import random
from apps.recommendations.models import PromptLog, RecommendedBook
from apps.books.services import  get_or_fetch_book
def built_prompt(genre: str, age_group: str) -> str:
    templates = [
        f"Recommend 5 {genre} books suitable for {age_group}.",
        f"I'm looking for {genre} books that would be perfect for {age_group}. List five.",
        f"Can you suggest five {genre} books for someone in the {age_group} category?",
        f"What are 5 highly-rated {genre} books for {age_group} readers?",
        f"Give me a list of 5 {genre} books that are great for {age_group}."
    ]
    return random.choice(templates)

def call_clova(prompt: str) -> str:
    print(f"sending prompt to clova: {prompt}")

    mock_response = """
    1. The Hobbit by J.R.R. Tolkien
    2. Percy Jackson and the Olympians by Rick Riordan
    3. Harry Potter and the Sorcerer's Stone by J.K. Rowling
    4. Eragon by Christopher Paolini
    5. The Chronicles of Narnia by C.S. Lewis
    """
    return mock_response.strip()

def parse_response(response: str) -> list:
    """
    Extract book titles from Clova response.
    """
    books = []
    for line in response.strip().split('\n'):
        # Remove leading numbering (e.g., '1.')
        parts = line.strip().split('.', 1)
        if len(parts) == 2:
            title = parts[1].strip()
            books.append(title)
        else:
            books.append(line.strip())  # fallback
    return books

def get_recommendations(genre: str, age_group: str) -> str:
    prompt = built_prompt(genre, age_group)
    response = call_clova(prompt)
    books = parse_response(response)

    prompt_log = PromptLog.objects.create(prompt=prompt, response=response)

    recommended_books = []
    for index, line in enumerate(books):
        if 'by' in line:
            title, author = line.split('by', 1)
        else:
            title, author = line, "Unknown"

        book = get_or_fetch_book(title.strip(), author.strip())

        RecommendedBook.objects.create(
            prompt_log=prompt_log,
            book=book,
            rank=index + 1  # ranks 1 to 5
        )

        recommended_books.append(book)

    return recommended_books