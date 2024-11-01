import json
from pathlib import Path

# Keep the settings file in the gui folder
SETTINGS_FILE = Path("src/gui/gui_settings.json")

def save_settings(term: str, session: str, days: dict[str, bool]) -> None:
    """Save the current GUI settings to a JSON file"""
    # Create gui directory if it doesn't exist
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    settings = {
        "term": term,
        "session": session,
        "days": days
    }
    
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)  # Added indent for better readability

def load_settings() -> dict:
    """Load settings from JSON file, return defaults if file doesn't exist"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "term": "",  # Will default to first term in list
            "session": "1",
            "days": {day: True for day in "MTWRFS"}
        } 