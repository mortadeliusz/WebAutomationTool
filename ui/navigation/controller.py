"""
Page Controller - Manages page navigation and lifecycle
"""

import customtkinter as ctk
from typing import Dict, Optional, Type, Callable
from src.utils.state_manager import set_last_visited_page


class PageController:
    """Handles page registration, navigation, and lifecycle management"""
    
    def __init__(self, container: ctk.CTkFrame, sidebar=None):
        self.container = container
        self.sidebar = sidebar
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.current_page: Optional[ctk.CTkFrame] = None
        self.current_page_name: Optional[str] = None
    
    def add_page(self, name: str, page_class: Type[ctk.CTkFrame], navigate_callback: Optional[Callable] = None) -> None:
        """Register a page class and create instance with navigation callback"""
        if navigate_callback:
            page = page_class(self.container, navigate_callback=navigate_callback)
        else:
            page = page_class(self.container)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_remove()  # Hide initially
        self.pages[name] = page
    
    def show_page(self, name: str) -> bool:
        """Show specified page, hide current page, update state and highlighting"""
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
        self.current_page_name = name
        
        # Update state and highlighting
        set_last_visited_page(name)
        if self.sidebar and hasattr(self.sidebar, 'update_highlighting'):
            self.sidebar.update_highlighting(name)
        
        return True
    
    def get_current_page_name(self) -> Optional[str]:
        """Get name of currently active page"""
        return self.current_page_name
    
    def get_page(self, name: str) -> Optional[ctk.CTkFrame]:
        """Get page instance by name"""
        return self.pages.get(name)