"""
Action Overlay - Full app overlay for blocking operations
"""

import customtkinter as ctk
from typing import Callable


class ActionOverlay(ctk.CTkFrame):
    """Full app overlay for blocking operations with cancel support"""
    
    def __init__(self, parent, title: str, message: str, on_cancel: Callable):
        super().__init__(parent)
        self.on_cancel = on_cancel
        self.setup_ui(title, message)
        self.show()
    
    def setup_ui(self, title: str, message: str):
        """Setup overlay UI with centered content"""
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.place(relx=0.5, rely=0.4, anchor="center")
        
        # Message
        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        message_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            self,
            text="Cancel",
            command=self.on_cancel_clicked,
            width=120,
            height=35
        )
        cancel_button.place(relx=0.5, rely=0.6, anchor="center")
    
    def show(self):
        """Show overlay covering entire app"""
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.lift()  # Ensure it's on top
    
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        self.on_cancel()
        self.close()
    
    def close(self):
        """Remove overlay"""
        self.place_forget()
        self.destroy()