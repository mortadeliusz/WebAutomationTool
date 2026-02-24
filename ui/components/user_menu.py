"""
User Menu - Custom dropdown menu for user actions
"""

import customtkinter as ctk
import logging
from typing import Callable, Optional
from src.utils.state_manager import get_session_state
from src.core.theme_manager import get_current_theme_default

logger = logging.getLogger(__name__)


class UserMenu(ctk.CTkToplevel):
    """Custom dropdown menu for user actions (theme, logout, etc.)"""
    
    def __init__(
        self,
        parent: ctk.CTk,
        anchor_widget: ctk.CTkButton,
        on_theme_change: Callable[[str], None],
        on_logout: Callable[[], None]
    ):
        super().__init__(parent)
        self.parent = parent
        self.anchor_widget = anchor_widget
        self.on_theme_change = on_theme_change
        self.on_logout = on_logout
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Get current theme
        self.current_theme = get_session_state("pref_theme") or get_current_theme_default()
        
        self.setup_ui()
        self.position_menu()
        
        # Close on click outside
        self.bind("<FocusOut>", lambda e: self.destroy())
        
        # Grab focus
        self.focus()
    
    def setup_ui(self) -> None:
        """Setup menu UI"""
        # Menu container
        menu_frame = ctk.CTkFrame(self, corner_radius=8)
        menu_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Theme options
        self.create_menu_item(
            menu_frame,
            "🌙 Dark Mode",
            lambda: self.switch_theme("🌙 Dark Mode"),
            is_current=self.current_theme == "🌙 Dark Mode"
        )
        
        self.create_menu_item(
            menu_frame,
            "☀️ Light Mode",
            lambda: self.switch_theme("☀️ Light Mode"),
            is_current=self.current_theme == "☀️ Light Mode"
        )
        
        # Separator
        separator = ctk.CTkFrame(menu_frame, height=1, fg_color="gray40")
        separator.pack(fill="x", padx=10, pady=5)
        
        # Logout
        self.create_menu_item(
            menu_frame,
            "Log Out",
            self.handle_logout
        )
    
    def create_menu_item(
        self,
        parent: ctk.CTkFrame,
        text: str,
        command: Callable[[], None],
        is_current: bool = False
    ) -> None:
        """Create a menu item button"""
        # Add checkmark if current
        display_text = f"✓ {text}" if is_current else f"   {text}"
        
        btn = ctk.CTkButton(
            parent,
            text=display_text,
            command=command,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            text_color=("gray14", "gray84"),
            anchor="w",
            height=32
        )
        btn.pack(fill="x", padx=5, pady=2)
    
    def position_menu(self) -> None:
        """Position menu below anchor widget"""
        # Update to get actual size
        self.update_idletasks()
        
        # Get anchor widget position
        anchor_x = self.anchor_widget.winfo_rootx()
        anchor_y = self.anchor_widget.winfo_rooty()
        anchor_height = self.anchor_widget.winfo_height()
        anchor_width = self.anchor_widget.winfo_width()
        
        # Get menu size
        menu_width = 200
        menu_height = self.winfo_reqheight()
        
        # Position below anchor, aligned to right edge
        x = anchor_x + anchor_width - menu_width
        y = anchor_y + anchor_height + 5
        
        # Ensure menu stays on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if x + menu_width > screen_width:
            x = screen_width - menu_width - 10
        
        if y + menu_height > screen_height:
            y = anchor_y - menu_height - 5  # Show above if no room below
        
        self.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
    
    def switch_theme(self, theme: str) -> None:
        """Handle theme switch"""
        logger.info(f"Theme switched to: {theme}")
        self.on_theme_change(theme)
        self.destroy()
    
    def handle_logout(self) -> None:
        """Handle logout"""
        self.destroy()
        self.on_logout()
