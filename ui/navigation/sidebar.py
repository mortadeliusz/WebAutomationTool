"""
Side Navigation - Clean navigation component using PageController
"""

import customtkinter as ctk
from ui.navigation.controller import PageController
from ui.navigation.registry import get_pages
from ui.components.menu_item_label import MenuItemLabel


class SideNav(ctk.CTkFrame):
    """Navigation sidebar using PageController pattern"""
    
    def __init__(self, parent, page_controller: PageController):
        super().__init__(parent, width=200)
        self.controller = page_controller
        self.menu_items = {}  # Store menu item references for highlighting
        
        self.create_navigation()
    
    def create_navigation(self) -> None:
        """Build navigation menu from page registry"""
        pages = get_pages()
        
        for page_config in pages:
            name = page_config["name"]
            menu_text = page_config["menu_text"]
            
            menu_item = MenuItemLabel(
                self,
                text=menu_text,
                on_click=lambda n=name: self.navigate_to(n)
            )
            menu_item.pack(pady=10, padx=10, fill="x")
            
            self.menu_items[name] = menu_item
    
    def navigate_to(self, page_name: str) -> None:
        """Navigate to specified page"""
        self.controller.show_page(page_name)
    
    def update_highlighting(self, current_page: str) -> None:
        """Update menu highlighting for current page"""
        for page_name, menu_item in self.menu_items.items():
            menu_item.set_current(page_name == current_page)