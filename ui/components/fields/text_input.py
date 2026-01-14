"""
Text Input Field Component
"""

import customtkinter as ctk
from typing import Optional


class TextInputField(ctk.CTkFrame):
    def __init__(self, parent, label: str, placeholder: str = "", optional: bool = False):
        super().__init__(parent)
        self.setup_ui(label, placeholder, optional)
    
    def setup_ui(self, label: str, placeholder: str, optional: bool):
        """Setup the text input field UI"""
        # Label
        label_text = f"{label}:" if not optional else f"{label} (optional):"
        self.label = ctk.CTkLabel(self, text=label_text)
        self.label.pack(side="left", padx=(10, 5))
        
        # Text input
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.pack(side="right", fill="x", expand=True, padx=(0, 10))
    
    def get_value(self) -> str:
        """Get the current value"""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)