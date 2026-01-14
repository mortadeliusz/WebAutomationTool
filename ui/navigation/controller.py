"""
Page Controller - Manages page navigation and lifecycle
"""

import customtkinter as ctk
from typing import Dict, Optional, Type


class PageController:
    """Handles page registration, navigation, and lifecycle management"""
    
    def __init__(self, container: ctk.CTkFrame):
        self.container = container
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.current_page: Optional[ctk.CTkFrame] = None
    
    def add_page(self, name: str, page_class: Type[ctk.CTkFrame]) -> None:
        """Register a page class and create instance"""
        page = page_class(self.container)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_remove()  # Hide initially
        self.pages[name] = page
    
    def show_page(self, name: str) -> bool:
        """Show specified page, hide current page"""
        if name not in self.pages:
            return False
        
        # Hide current page
        if self.current_page:
            self.current_page.grid_remove()
        
        # Show new page
        page = self.pages[name]
        
        # Call lifecycle hook if page implements it
        if hasattr(page, 'on_show'):
            page.on_show()
        
        page.grid()
        self.current_page = page
        
        return True
    
    def get_current_page_name(self) -> Optional[str]:
        """Get name of currently active page"""
        if not self.current_page:
            return None
        
        for name, page in self.pages.items():
            if page == self.current_page:
                return name
        
        return None
    
    def get_page(self, name: str) -> Optional[ctk.CTkFrame]:
        """Get page instance by name"""
        return self.pages.get(name)