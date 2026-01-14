"""
Status Bar - Display status messages
"""

import customtkinter as ctk


class StatusBar(ctk.CTkLabel):
    def __init__(self, parent):
        super().__init__(parent, text="Ready", font=ctk.CTkFont(size=12))
    
    def update_status(self, message: str):
        """Update the status message"""
        self.configure(text=message)