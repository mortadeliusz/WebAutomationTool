"""
Dropdown Field Component
"""

import customtkinter as ctk
from typing import List


class DropdownField(ctk.CTkFrame):
    def __init__(self, parent, label: str, values: List[str]):
        super().__init__(parent)
        self.setup_ui(label, values)
    
    def setup_ui(self, label: str, values: List[str]):
        """Setup the dropdown field UI"""
        # Label
        self.label = ctk.CTkLabel(self, text=f"{label}:")
        self.label.pack(side="left", padx=(10, 5))
        
        # Dropdown
        self.combo = ctk.CTkComboBox(self, values=values)
        self.combo.pack(side="right", padx=(0, 10))
        
        # Set first value as default
        if values:
            self.combo.set(values[0])
    
    def get_value(self) -> str:
        """Get the current value"""
        return self.combo.get()
    
    def set_value(self, value: str):
        """Set the value"""
        self.combo.set(value)