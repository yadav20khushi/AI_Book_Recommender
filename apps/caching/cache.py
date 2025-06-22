import functools
import hashlib
import json
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def api_cache(timeout=3600):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key using the function name and arguments
            try:
                key_data = {
                    'function': func.__name__,
                    'args': str(args[1:]),  # Skip `self` for cleaner keys
                    'kwargs': kwargs
                }
                key_string = json.dumps(key_data, sort_keys=True)
                key_hash = hashlib.md5(key_string.encode()).hexdigest()
                cache_key = f"{func.__name__}:{args[0].__class__.__name__}:{key_hash}"
            except Exception as e:
                logger.warning(f"[CACHE] Failed to create cache key: {e}")
                return func(*args, **kwargs)

            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"[CACHE HIT] for key: {cache_key}")
                return cached_data

            logger.debug(f"[CACHE MISS] for key: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator
