from django.core.cache import cache
import functools
import json

def cache_with_ttl(ttl_seconds):
    """
    Decorator to cache the result of a function in Redis with TTL.
    Assumes function returns JSON-serializable data.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            cache_key = f"{func.__name__}:" + ":".join(map(str, args)) + ":" + ":".join(f"{k}={v}" for k, v in kwargs.items())

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"[DEBUG] Cache hit for key: {cache_key}")
                return json.loads(cached_result)

            print(f"[DEBUG] Cache miss for key: {cache_key}, calling function...")
            result = func(*args, **kwargs)
            cache.set(cache_key, json.dumps(result), ttl_seconds)
            return result
        return wrapper
    return decorator
