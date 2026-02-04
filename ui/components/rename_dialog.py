"""
Rename Dialog - Simple dialog for renaming browser alias
"""

import customtkinter as ctk
from typing import Callable


class RenameDialog(ctk.CTkToplevel):
    """Simple rename dialog"""
    
    def __init__(self, parent, current_alias: str, on_save: Callable):
        super().__init__(parent)
        self.on_save = on_save
        self.current_alias = current_alias
        
        self.title("Rename Browser")
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Label
        label = ctk.CTkLabel(
            self,
            text=f"Rename browser '{self.current_alias}':",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=(20, 10), padx=20)
        
        # Entry
        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10, padx=20)
        self.entry.insert(0, self.current_alias)
        self.entry.select_range(0, "end")
        self.entry.focus()
        self.entry.bind("<Return>", lambda e: self._on_save_clicked())
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save_clicked
        )
        save_btn.pack(side="left", padx=5)
    
    def _on_save_clicked(self):
        """Handle save button click"""
        new_alias = self.entry.get().strip()
        if new_alias:
            self.on_save(new_alias)
            self.destroy()
