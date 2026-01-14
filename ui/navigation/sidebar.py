"""
Side Navigation - Clean navigation component using PageController
"""

import customtkinter as ctk
from ui.navigation.controller import PageController
from ui.navigation.registry import get_pages


class SideNav(ctk.CTkFrame):
    """Navigation sidebar using PageController pattern"""
    
    def __init__(self, parent, page_controller: PageController):
        super().__init__(parent, width=200)
        self.controller = page_controller
        self.buttons = {}
        
        self.create_navigation()
    
    def create_navigation(self) -> None:
        """Build navigation menu from page registry"""
        pages = get_pages()
        
        for page_config in pages:
            name = page_config["name"]
            menu_text = page_config["menu_text"]
            
            button = ctk.CTkButton(
                self,
                text=menu_text,
                command=lambda n=name: self.navigate_to(n)
            )
            button.pack(pady=10, padx=10, fill="x")
            
            self.buttons[name] = button
    
    def navigate_to(self, page_name: str) -> None:
        """Navigate to specified page"""
        success = self.controller.show_page(page_name)
        
        if success:
            self.update_active_button(page_name)
    
    def update_active_button(self, active_page: str) -> None:
        """Update button styles to show active page"""
        for name, button in self.buttons.items():
            if name == active_page:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray84", "gray25"))