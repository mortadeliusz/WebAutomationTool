"""
Browser State Observer - Event system for browser state changes
"""

from typing import Callable, List


class BrowserStateObserver:
    """Simple observer pattern for browser state changes"""
    
    def __init__(self):
        self.listeners: List[Callable[[str, str], None]] = []
    
    def subscribe(self, callback: Callable[[str, str], None]):
        """Subscribe to browser state changes
        
        Args:
            callback: Function(event_type: str, alias: str) -> None
        """
        if callback not in self.listeners:
            self.listeners.append(callback)
    
    def unsubscribe(self, callback: Callable[[str, str], None]):
        """Unsubscribe from browser state changes"""
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def notify(self, event_type: str, alias: str):
        """Notify all subscribers of state change
        
        Args:
            event_type: 'launched', 'closed', 'navigated'
            alias: Browser alias (e.g., 'main')
        """
        for callback in self.listeners:
            try:
                callback(event_type, alias)
            except Exception as e:
                print(f"Error in browser state listener: {e}")
