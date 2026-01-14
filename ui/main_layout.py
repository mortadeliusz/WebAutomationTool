"""
Main Layout - Handles application UI structure and component wiring
"""

import customtkinter as ctk
from ui.navigation.sidebar import SideNav
from ui.navigation.controller import PageController
from ui.navigation.registry import get_pages


class MainLayout:
    """Manages the main application layout and UI component structure"""
    
    def __init__(self, parent: ctk.CTk):
        self.parent = parent
        self.setup_layout()
    
    def setup_layout(self) -> None:
        """Configure main application layout"""
        # Configure grid layout
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        
        # Create page container
        self.page_container = ctk.CTkFrame(self.parent)
        self.page_container.grid(row=0, column=1, sticky="nsew")
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)
        
        # Create page controller
        self.page_controller = PageController(self.page_container)
        
        # Register all pages from registry
        for page_config in get_pages():
            self.page_controller.add_page(page_config["name"], page_config["class"])
        
        # Create navigation sidebar
        self.side_nav = SideNav(self.parent, self.page_controller)
        self.side_nav.grid(row=0, column=0, sticky="ns")
        
        # Show default page
        self.page_controller.show_page("workflow_execution")