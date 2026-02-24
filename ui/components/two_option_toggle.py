import customtkinter as ctk
from typing import Callable, Optional


class TwoOptionToggle(ctk.CTkFrame):
    """Toggle between two options with visual feedback"""
    
    def __init__(
        self, 
        parent, 
        option1: str, 
        option2: str, 
        initial_option: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None
    ):
        super().__init__(parent, fg_color="transparent")
        self.option1 = option1
        self.option2 = option2
        self.on_change = on_change
        self.current_option = initial_option or option1
        self.setup_ui()
    
    def setup_ui(self):
        """Setup toggle buttons"""
        self.button1 = ctk.CTkButton(
            self, text=self.option1, width=120, command=lambda: self.select_option(self.option1)
        )
        self.button1.pack(side="left", padx=(0, 2))
        
        self.button2 = ctk.CTkButton(
            self, text=self.option2, width=120, command=lambda: self.select_option(self.option2)
        )
        self.button2.pack(side="left", padx=(2, 0))
        
        self.update_appearance()
    
    def select_option(self, option: str):
        """Select an option and trigger callback"""
        if option != self.current_option:
            self.current_option = option
            self.update_appearance()
            if self.on_change:
                self.on_change(option)
    
    def update_appearance(self):
        """Update button appearance based on selection"""
        if self.current_option == self.option1:
            self.button1.configure(fg_color=["#3B8ED0", "#1F6AA5"])  # Selected
            self.button2.configure(fg_color=["gray70", "gray25"])     # Unselected
        else:
            self.button1.configure(fg_color=["gray70", "gray25"])     # Unselected
            self.button2.configure(fg_color=["#3B8ED0", "#1F6AA5"])  # Selected
    
    def get_selected(self) -> str:
        """Get currently selected option"""
        return self.current_option
    
    def set_selected(self, option: str):
        """Set selected option programmatically"""
        if option in [self.option1, self.option2]:
            self.current_option = option
            self.update_appearance()