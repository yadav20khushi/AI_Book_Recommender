from .config_parser import load_config

_config = None  # This will store the config data

def get_config():
    global _config
    if _config is None:
        _config = load_config()
    return _config
