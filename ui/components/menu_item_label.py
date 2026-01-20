"""
Menu Item Label - Custom navigation menu item with theme-aware styling
"""

import customtkinter as ctk
from typing import Callable, Optional
from src.core.theme_manager import get_component_colors


class MenuItemLabel(ctk.CTkLabel):
    """Custom menu item with hover effects and current page indication"""
    
    def __init__(self, parent, text: str, on_click: Optional[Callable] = None):
        # Load colors from theme
        self.colors = get_component_colors("MenuItemLabel")
        
        # Let CTkLabel use its defaults - no fg_color or text_color specified
        super().__init__(
            parent,
            text=text,
            cursor="hand2",
            font=ctk.CTkFont(size=14, weight="normal")
        )
        
        self.on_click = on_click
        self.is_current = False
        
        # Bind events
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
    
    def _handle_click(self, event):
        if self.on_click:
            self.on_click()
    
    def _on_hover_enter(self, event):
        if not self.is_current:
            self.configure(fg_color=self.colors.get("hover_bg", ["gray85", "gray20"]))
    
    def _on_hover_leave(self, event):
        if not self.is_current:
            self.configure(fg_color=self.colors.get("default_bg", "transparent"))
    
    def set_current(self, is_current: bool):
        """Set current page state"""
        self.is_current = is_current
        if is_current:
            self.configure(
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.colors.get("selected_bg", ["gray80", "gray25"])
            )
        else:
            self.configure(
                font=ctk.CTkFont(size=14, weight="normal"),
                fg_color=self.colors.get("default_bg", "transparent")
            )