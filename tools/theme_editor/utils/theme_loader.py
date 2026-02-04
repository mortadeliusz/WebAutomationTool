import json
from pathlib import Path

class ThemeLoader:
    def __init__(self):
        self.theme_data = {}
        self.current_file = None
    
    def load_theme(self, file_path):
        """Load theme from JSON file"""
        try:
            with open(file_path, 'r') as f:
                self.theme_data = json.load(f)
            self.current_file = file_path
            return True
        except Exception as e:
            print(f"Error loading theme: {e}")
            return False
    
    def save_theme(self, file_path=None):
        """Save theme to JSON file"""
        target_file = file_path or self.current_file
        if not target_file:
            return False
        
        try:
            with open(target_file, 'w') as f:
                json.dump(self.theme_data, f, indent=2)
            if file_path:
                self.current_file = file_path
            return True
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
    
    def get_theme_data(self):
        """Get current theme data"""
        return self.theme_data
    
    def update_color(self, widget_class, attribute, index, new_color):
        """Update a specific color in the theme"""
        if widget_class in self.theme_data:
            if attribute in self.theme_data[widget_class]:
                if isinstance(self.theme_data[widget_class][attribute], list):
                    if 0 <= index < len(self.theme_data[widget_class][attribute]):
                        self.theme_data[widget_class][attribute][index] = new_color