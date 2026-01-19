"""
Action Value Input - Text input with data expression helper
Domain-specific component for action value field
"""

import customtkinter as ctk
from ui.components.fields.data_expression_helper import DataExpressionHelper
from src.app_services import get_workflow_data_sample


class ActionValueInput(ctk.CTkFrame):
    """Value input field with data expression helper"""
    
    def __init__(self, parent, label: str, placeholder: str = "", optional: bool = False, on_load_data=None):
        super().__init__(parent)
        self.on_load_data_callback = on_load_data
        self.setup_ui(label, placeholder, optional)
    
    def setup_ui(self, label: str, placeholder: str, optional: bool):
        """Setup the value input field UI"""
        # Label
        label_text = f"{label}:" if not optional else f"{label} (optional):"
        self.label = ctk.CTkLabel(self, text=label_text)
        self.label.pack(side="left", padx=(10, 5))
        
        # Container for entry + helper
        input_container = ctk.CTkFrame(self, fg_color="transparent")
        input_container.pack(side="right", fill="x", expand=True, padx=(0, 10))
        
        # Entry
        self.entry = ctk.CTkEntry(input_container, placeholder_text=placeholder)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Expression helper
        self.helper = DataExpressionHelper(
            input_container,
            target_entry=self.entry,
            data_sample=get_workflow_data_sample(),
            on_load_data=self.on_load_data_clicked
        )
        self.helper.pack(side="left")
        
        # Help button
        help_btn = ctk.CTkButton(
            input_container,
            text="❓",
            width=30,
            command=self.show_help
        )
        help_btn.pack(side="left", padx=(5, 0))
    
    def get_value(self) -> str:
        """Get the current value"""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
    
    def refresh_data_sample(self):
        """Refresh data sample from service"""
        self.helper.set_data_sample(get_workflow_data_sample())
    
    def on_load_data_clicked(self):
        """Callback when user clicks Load in educational popup"""
        if self.on_load_data_callback:
            self.on_load_data_callback()
    
    def show_help(self):
        """Show educational popup"""
        from ui.components.fields.data_expression_helper import EducationalPopup
        EducationalPopup(self, on_load_data=self.on_load_data_clicked)
