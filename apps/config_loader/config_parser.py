import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "seoul_library.json"

REQUIRED_KEYS = ["library_id", "enable_media", "theme_class", "naru_region_code"]

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
            config_data = json.load(file)

            # Check for required keys
            missing = [key for key in REQUIRED_KEYS if key not in config_data]
            if missing:
                raise KeyError(f"Missing required config keys: {', '.join(missing)}")

            return config_data

    except FileNotFoundError:
        print(f"Config file not found at {CONFIG_PATH}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON config")
        return {}
    except KeyError as e:
        print(str(e))
        return {}
