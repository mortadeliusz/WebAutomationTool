"""
Theme Manager - Complete theme domain logic and CustomTkinter integration
"""

import customtkinter as ctk
import json
from pathlib import Path
from src.utils.state_manager import get_session_state, set_session_state

# Global theme colors cache
_custom_theme_colors = None

def initialize_app_theme(app: ctk.CTk):
    """Initialize theme on app startup"""
    # Load saved theme from persistence
    saved_theme = get_session_state("pref_theme") or get_current_theme_default()
    
    # Apply theme to app
    apply_theme_to_app(app, saved_theme)
    
    # Load custom theme file for CTk widgets
    load_custom_theme_file()

def switch_theme(theme_name: str):
    """Switch theme with persistence"""
    # Save to session state (persisted on app close)
    set_session_state("pref_theme", theme_name)
    
    # Apply immediately
    mode = "dark" if "Dark" in theme_name else "light"
    ctk.set_appearance_mode(mode)

def get_current_theme_default() -> str:
    """Get default theme for new users"""
    return "🌙 Dark Mode"

def apply_theme_to_app(app: ctk.CTk, theme: str):
    """Apply theme to CustomTkinter application"""
    mode = "dark" if "Dark" in theme else "light"
    ctk.set_appearance_mode(mode)

def load_custom_theme_file():
    """Load custom theme JSON file for CTk widgets"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        ctk.set_default_color_theme(config['color_theme'])
    except Exception:
        # Fallback to built-in theme
        ctk.set_default_color_theme("dark-blue")

def load_custom_theme_colors():
    """Load custom theme colors from JSON file"""
    global _custom_theme_colors
    if _custom_theme_colors is None:
        try:
            theme_file = Path("config/custom_theme.json")
            if theme_file.exists():
                with open(theme_file, 'r') as f:
                    _custom_theme_colors = json.load(f)
            else:
                _custom_theme_colors = {}
        except Exception:
            _custom_theme_colors = {}
    return _custom_theme_colors

def get_component_colors(component_name: str):
    """Get color definitions for a custom component"""
    theme_colors = load_custom_theme_colors()
    return theme_colors.get(component_name, {})