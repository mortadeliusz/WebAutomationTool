"""
User Preferences Management
"""

import json
import os
from pathlib import Path

class UserPreferences:
    def __init__(self):
        self.config_dir = Path("config")
        self.prefs_file = self.config_dir / "user_preferences.json"
        self.default_preferences = {
            "theme": "🌙 Dark Mode",
            "lastSelectedTask": None,
            "last_visited_page": "workflow_management",
            "last_selected_workflow": "",
            "wizard_mode": True  # New users start with wizard
        }
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_all(self):
        """Load all user preferences from file"""
        try:
            if self.prefs_file.exists():
                with open(self.prefs_file, 'r') as f:
                    preferences = json.load(f)
                # Merge with defaults to handle new preferences
                return {**self.default_preferences, **preferences}
            else:
                return self.default_preferences.copy()
        except (json.JSONDecodeError, IOError):
            # Return defaults if file is corrupted or unreadable
            return self.default_preferences.copy()
    
    def save_all(self, preferences):
        """Save all preferences to file"""
        try:
            with open(self.prefs_file, 'w') as f:
                json.dump(preferences, f, indent=2)
        except IOError as e:
            print(f"Failed to save user preferences: {e}")
    
    def get_preference(self, key, default=None):
        """Get single preference value"""
        preferences = self.load_all()
        return preferences.get(key, default)
    
    def set_preference(self, key, value):
        """Set single preference value"""
        preferences = self.load_all()
        preferences[key] = value
        self.save_all(preferences)


# Global instance for easy access
_user_prefs = UserPreferences()

def get_user_preference(key: str, default=None):
    """Get user preference value"""
    return _user_prefs.get_preference(key, default)

def set_user_preference(key: str, value):
    """Set user preference value"""
    _user_prefs.set_preference(key, value)