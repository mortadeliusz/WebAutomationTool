"""
Number Input Field - Numeric input with validation
"""

import customtkinter as ctk


class NumberInputField(ctk.CTkFrame):
    """Field for numeric input with validation"""
    
    def __init__(self, parent, label: str = "Value", placeholder: str = "0", min_value: int = 0):
        super().__init__(parent)
        self.label_text = label
        self.placeholder = placeholder
        self.min_value = min_value
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the number input UI"""
        # Label
        self.label = ctk.CTkLabel(self, text=self.label_text)
        self.label.pack(side="left", padx=(0, 10))
        
        # Entry field
        self.entry = ctk.CTkEntry(self, placeholder_text=self.placeholder, width=100)
        self.entry.pack(side="left")
        
        # Validate on focus out
        self.entry.bind("<FocusOut>", self.validate)
    
    def validate(self, event=None):
        """Validate numeric input"""
        value = self.entry.get()
        if not value:
            return
        
        try:
            num = int(value)
            if num < self.min_value:
                self.entry.delete(0, 'end')
                self.entry.insert(0, str(self.min_value))
        except ValueError:
            self.entry.delete(0, 'end')
            self.entry.insert(0, str(self.min_value))
    
    def get_value(self) -> str:
        """Get the numeric value as string"""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the numeric value"""
        self.entry.delete(0, 'end')
        self.entry.insert(0, str(value))
