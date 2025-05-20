import random
import time
from django.core.cache import cache
from django.conf import settings

def get_book_info(isbn: str) -> dict:
    cache_key = f"book_info:{isbn}"
    cached_data = cache.get(cache_key)
    if cached_data:
        print("[DEBUG] Cache hit!")
        return cached_data

    print("[DEBUG] Cache miss, mocking API call...")

    # Simulate retry logic
    try:
        # --- MOCK API CALL START ---
        time.sleep(1)  # Simulate network delay
        mock_data = {
            "isbn": isbn,
            "title": f"Mocked Book {random.randint(1, 100)}",
            "author": "Mock Author",
            "summary": "A mock summary for testing.",
            "cover_url": "https://example.com/mock_cover.jpg",
            "available": random.choice([True, False]),
        }
        # --- MOCK API CALL END ---

        cache.set(cache_key, mock_data, timeout=60 * 60)  # Cache for 1 hour
        return mock_data

    except Exception as e:
        print(f"[ERROR] Failed to fetch book info: {e}")
        return {"error": "Failed to retrieve book info"}

def get_availability(isbn: str) -> bool:

    cache_key = f"availability:{isbn}"
    cached = cache.get(cache_key)

    if cached is not None:
        print("[DEBUG] Cache hit for availability.")
        return cached

    print("[DEBUG] Cache miss for availability, mocking API call...")

    # Mocked logic: Randomly decide if available
    available = random.choice([True, False])

    # Cache for 1 hour (3600 seconds)
    cache.set(cache_key, available, timeout=3600)

    return available

def get_bestsellers(region: str) -> list:
    cache_key = f"bestsellers:{region}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print("[DEBUG] Cache hit for bestsellers.")
        return cached_data

    print("[DEBUG] Cache miss for bestsellers, mocking API call...")

    mock_bestsellers = [
        {
            "isbn": f"97812345678{str(i).zfill(2)}",
            "title": f"Mock Bestseller {i}",
            "author": f"Mock Author {i}",
            "summary": f"A bestselling book in {region}.",
            "cover_url": "https://example.com/mock_cover.jpg"
        }
        for i in range(1, 6)
    ]

    # Store in cache for future calls
    cache.set(cache_key, mock_bestsellers, timeout=60 * 60)  # 1 hour

    return mock_bestsellers