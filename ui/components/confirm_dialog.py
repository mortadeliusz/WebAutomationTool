"""
Confirmation Dialog - Reusable modal dialog for confirmations
"""

import customtkinter as ctk
from typing import Optional


class ConfirmDialog(ctk.CTkToplevel):
    """Modal confirmation dialog matching app style"""
    
    def __init__(
        self, 
        parent: ctk.CTk, 
        title: str, 
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel"
    ):
        super().__init__(parent)
        self.result: bool = False
        
        self.title(title)
        self.geometry("400x150")
        
        # Message
        label = ctk.CTkLabel(self, text=message, wraplength=350)
        label.pack(pady=20, padx=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text=cancel_text, 
            command=self.cancel
        )
        cancel_btn.pack(side="left", padx=5)
        
        confirm_btn = ctk.CTkButton(
            button_frame, 
            text=confirm_text, 
            command=self.confirm
        )
        confirm_btn.pack(side="left", padx=5)
        
        # Modal setup
        self.transient(parent)
        self.grab_set()
        self.focus()
    
    def confirm(self) -> None:
        """User confirmed action"""
        self.result = True
        self.destroy()
    
    def cancel(self) -> None:
        """User cancelled action"""
        self.result = False
        self.destroy()
    
    def get_result(self) -> bool:
        """Get dialog result after it closes"""
        self.wait_window()
        return self.result
