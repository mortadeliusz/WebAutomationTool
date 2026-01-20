import customtkinter as ctk
from typing import Callable, Optional


class TwoOptionToggle(ctk.CTkFrame):
    """Generic two-option toggle component with clickable label pattern"""
    
    def __init__(self, parent, option1: str, option2: str, 
                 initial_option: str, on_change: Optional[Callable[[str], None]] = None):
        super().__init__(parent, fg_color="transparent")
        self.option1 = option1
        self.option2 = option2
        self.current_option = initial_option
        self.on_change = on_change
        self.setup_ui()
    
    def setup_ui(self):
        # Current option display
        self.option_display = ctk.CTkLabel(
            self, text=self.current_option, 
            font=ctk.CTkFont(weight="bold")
        )
        self.option_display.pack(side="left")
        
        # Toggle button (clickable label)
        other_option = self.get_other_option()
        toggle_text = f"Switch to {other_option} ⚙"
        self.toggle_label = ctk.CTkLabel(
            self, text=toggle_text, font=ctk.CTkFont(size=10),
            text_color="gray", cursor="hand2"
        )
        self.toggle_label.pack(side="left", padx=(10, 0))
        
        # Bind events
        self.toggle_label.bind("<Button-1>", self.on_toggle_clicked)
        self.toggle_label.bind("<Enter>", self.on_hover_enter)
        self.toggle_label.bind("<Leave>", self.on_hover_leave)
    
    def get_other_option(self) -> str:
        return self.option2 if self.current_option == self.option1 else self.option1
    
    def on_toggle_clicked(self, event):
        # Switch to other option
        self.current_option = self.get_other_option()
        
        # Update UI
        self.option_display.configure(text=self.current_option)
        toggle_text = f"Switch to {self.get_other_option()}"
        self.toggle_label.configure(text=toggle_text)
        
        # Notify parent
        if self.on_change:
            self.on_change(self.current_option)
    
    def on_hover_enter(self, event):
        self.toggle_label.configure(text_color=("blue", "lightblue"))
    
    def on_hover_leave(self, event):
        self.toggle_label.configure(text_color="gray")
    
    def get_current_option(self) -> str:
        return self.current_option
    
    def set_option(self, option: str):
        if option in [self.option1, self.option2]:
            self.current_option = option
            self.option_display.configure(text=self.current_option)
            toggle_text = f"Switch to {self.get_other_option()} ⚙"
            self.toggle_label.configure(text=toggle_text)