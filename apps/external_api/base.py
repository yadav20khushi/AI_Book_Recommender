import requests
import logging

class ExternalAPIService:
    def __init__(self):
        from django.conf import settings
        self.auth_key = settings.DATA4LIBRARY_API_KEY
        self.logger = logging.getLogger(__name__)

    def get_json(self, url, fallback_data=None):
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.logger.warning(f"JSON API failed: {url} -> {e}")
            return fallback_data

