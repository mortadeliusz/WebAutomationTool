"""
Selector Picker Field Component - Text input with element picker button
"""

import customtkinter as ctk
from typing import Optional, Callable


class SelectorPickerField(ctk.CTkFrame):
    def __init__(self, parent, label: str, placeholder: str = "", has_picker: bool = True, has_advanced: bool = False):
        super().__init__(parent)
        self.has_picker = has_picker
        self.on_picker_click: Optional[Callable] = None
        self.setup_ui(label, placeholder)
    
    def setup_ui(self, label: str, placeholder: str):
        """Setup the selector picker field UI"""
        # Label
        self.label = ctk.CTkLabel(self, text=f"{label}:")
        self.label.pack(side="left", padx=(10, 5))
        
        # Input container
        input_container = ctk.CTkFrame(self)
        input_container.pack(side="right", fill="x", expand=True, padx=(0, 10))
        
        # Text input
        self.entry = ctk.CTkEntry(input_container, placeholder_text=placeholder)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Picker button
        if self.has_picker:
            self.picker_button = ctk.CTkButton(
                input_container, 
                text="🎯", 
                width=30,
                command=self.on_picker_clicked
            )
            self.picker_button.pack(side="right")
    
    def on_picker_clicked(self):
        """Handle picker button click"""
        if self.on_picker_click:
            self.on_picker_click(self)
    
    def set_picker_callback(self, callback: Callable):
        """Set callback for picker button"""
        self.on_picker_click = callback
    
    def get_value(self) -> str:
        """Get the current value"""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    
    def set_picker_result(self, selector: str):
        """Set the result from element picker"""
        self.set_value(selector)