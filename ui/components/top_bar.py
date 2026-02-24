"""
Top Bar - Application header with user info and logout
"""

import customtkinter as ctk
import webbrowser
import logging
from typing import Optional
from src.types import UserSessionData
from ui.components.confirm_dialog import ConfirmDialog
from ui.components.user_menu import UserMenu
from src.core.theme_manager import switch_theme, get_button_colors
from config import BACKEND_URL

logger = logging.getLogger(__name__)


class TopBar(ctk.CTkFrame):
    """Top bar with app title, user email, and logout button"""
    
    def __init__(self, parent: ctk.CTk, user_data: Optional[UserSessionData] = None):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data or {}
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup top bar UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Get button colors from theme
        button_colors = get_button_colors()
        
        # App title (left)
        title_label = ctk.CTkLabel(
            self,
            text="Web Automation Tool",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # User email button with dropdown indicator (right)
        email = self.user_data.get('email', 'Not logged in')
        self.email_button = ctk.CTkButton(
            self,
            text=f"{email} ▼",
            command=self.show_user_menu,
            fg_color="transparent",
            hover_color=button_colors.get("hover_color", ("gray70", "gray30")),
            text_color=("gray14", "gray84"),
            font=ctk.CTkFont(size=12)
        )
        self.email_button.grid(row=0, column=1, padx=20, pady=10, sticky="e")
    
    def show_user_menu(self) -> None:
        """Show user menu dropdown"""
        UserMenu(
            self.parent,
            self.email_button,
            on_theme_change=self.handle_theme_change,
            on_logout=self.logout
        )
    
    def handle_theme_change(self, theme: str) -> None:
        """Handle theme change from menu"""
        switch_theme(theme)
    
    def logout(self) -> None:
        """Handle logout - confirm, open browser, cleanup, close app"""
        # Show confirmation dialog
        dialog = ConfirmDialog(
            self.parent,
            title="Confirm Logout",
            message="Logging out will close the application. Continue?",
            confirm_text="Log Out",
            cancel_text="Cancel"
        )
        
        confirmed = dialog.get_result()
        
        if confirmed:
            logger.info("User logout initiated")
            
            # Open browser to logout page (clears Firebase session)
            try:
                logout_url = f"{BACKEND_URL}/ui/auth/logout.html"
                webbrowser.open(logout_url)
                logger.info(f"Opened logout URL: {logout_url}")
            except Exception as e:
                logger.error(f"Failed to open logout URL: {e}")
            
            # Cleanup and close app
            self.parent.on_closing()
