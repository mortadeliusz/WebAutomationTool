"""
State management utilities for navigation and workflow selection
Hybrid approach: Direct preferences for critical state, session state for high-frequency updates
"""

from typing import Optional
from src.core.user_preferences import get_user_preference, set_user_preference

# Session state for high-frequency updates (window size, theme, etc.)
_session_state = {}

def get_last_visited_page() -> str:
    """Get last visited page with fallback to default"""
    try:
        return get_user_preference("last_visited_page", "workflow_management")
    except Exception:
        return "workflow_management"

def set_last_visited_page(page_name: str) -> bool:
    """Set last visited page with immediate persistence"""
    try:
        set_user_preference("last_visited_page", page_name)
        return True
    except Exception:
        return False

def get_last_selected_workflow() -> str:
    """Get last selected workflow with fallback to empty"""
    try:
        return get_user_preference("last_selected_workflow", "")
    except Exception:
        return ""

def set_last_selected_workflow(workflow_name: str) -> bool:
    """Set last selected workflow with immediate persistence"""
    try:
        set_user_preference("last_selected_workflow", workflow_name)
        return True
    except Exception:
        return False

def get_wizard_mode_preference() -> bool:
    """Get wizard mode preference with fallback to True (new users start with wizard)"""
    try:
        return get_user_preference("wizard_mode", True)
    except Exception:
        return True  # Default to wizard for new users

def set_wizard_mode_preference(enabled: bool) -> bool:
    """Set wizard mode preference with immediate persistence"""
    try:
        set_user_preference("wizard_mode", enabled)
        return True
    except Exception:
        return False  # Graceful degradation

def get_wizard_mode() -> bool:
    """Get wizard mode preference with fallback to True"""
    try:
        return get_user_preference("wizard_mode", True)
    except Exception:
        return True

def set_wizard_mode(enabled: bool) -> bool:
    """Set wizard mode preference with immediate persistence"""
    try:
        set_user_preference("wizard_mode", enabled)
        return True
    except Exception:
        return False

def get_session_state(key: str, default=None):
    """Get session-level state (high-frequency updates)"""
    return _session_state.get(key, default)

def set_session_state(key: str, value):
    """Set session-level state (persisted on app close)"""
    _session_state[key] = value

def get_state(key: str, default=None):
    """Get any application state with fallback"""
    try:
        return get_user_preference(key, default)
    except Exception:
        return default

def set_state(key: str, value):
    """Set any application state"""
    try:
        set_user_preference(key, value)
        return True
    except Exception:
        return False

def save_session_to_preferences():
    """Save session state to preferences on app close"""
    try:
        for key, value in _session_state.items():
            if key.startswith("pref_"):  # Only save designated session keys
                pref_key = key[5:]  # Remove "pref_" prefix
                set_user_preference(pref_key, value)
    except Exception:
        pass  # Graceful degradation on save failure

def clear_session_state():
    """Clear session state (for testing or reset)"""
    global _session_state
    _session_state = {}