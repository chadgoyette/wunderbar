import json
import os

SETTINGS_FILE = "settings.json"

# Updated default settings structure:
DEFAULT_SETTINGS = {
    "rotor_speed": 50,  # Default rotor speed
    "sizes": {
        "Strawberry Banana (w/ Yogurt)": {
            "Small": {"Flavor": 1.25, "Yogurt": 2.50, "Ice": 3.75},
            "Medium": {"Flavor": 2.00, "Yogurt": 3.00, "Ice": 4.50},
            "Large": {"Flavor": 2.75, "Yogurt": 3.75, "Ice": 5.25}
        },
        "Strawberry Banana (No Yogurt)": {
            "Small": {"Flavor": 1.25, "Yogurt": 0.0, "Ice": 3.75},
            "Medium": {"Flavor": 2.00, "Yogurt": 0.0, "Ice": 4.50},
            "Large": {"Flavor": 2.75, "Yogurt": 0.0, "Ice": 5.25}
        },
        "Mango Pineapple (w/ Yogurt)": {
            "Small": {"Flavor": 1.10, "Yogurt": 2.20, "Ice": 3.30},
            "Medium": {"Flavor": 1.90, "Yogurt": 2.90, "Ice": 4.40},
            "Large": {"Flavor": 2.70, "Yogurt": 3.70, "Ice": 5.20}
        },
        "Mango Pineapple (No Yogurt)": {
            "Small": {"Flavor": 1.10, "Yogurt": 0.0, "Ice": 3.30},
            "Medium": {"Flavor": 1.90, "Yogurt": 0.0, "Ice": 4.40},
            "Large": {"Flavor": 2.70, "Yogurt": 0.0, "Ice": 5.20}
        },
        # Other flavors can remain unchanged or be updated similarly
        "Caramel Frappe": {
            "Small": {"Flavor": 1.10, "Yogurt": 2.20, "Ice": 3.30},
            "Medium": {"Flavor": 1.90, "Yogurt": 2.90, "Ice": 4.40},
            "Large": {"Flavor": 2.70, "Yogurt": 3.70, "Ice": 5.20}
        },
        "Mocha Frappe": {
            "Small": {"Flavor": 1.10, "Yogurt": 2.20, "Ice": 3.30},
            "Medium": {"Flavor": 1.90, "Yogurt": 2.90, "Ice": 4.40},
            "Large": {"Flavor": 2.70, "Yogurt": 3.70, "Ice": 5.20}
        }
    }
}

def load_settings():
    """Load settings from the JSON file, or create default if missing."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)  # Create file with default settings if missing.
        return DEFAULT_SETTINGS

    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save settings to the JSON file."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        print("[INFO] Settings saved:", settings)
    except Exception as e:
        print(f"[ERROR] Failed to save settings: {e}")
