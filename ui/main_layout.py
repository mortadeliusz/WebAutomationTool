"""
Main Layout - Handles application UI structure and component wiring
"""

import customtkinter as ctk
from ui.navigation.sidebar import SideNav
from ui.navigation.controller import PageController
from ui.navigation.registry import get_pages
from ui.components.two_option_toggle import TwoOptionToggle
from src.utils.state_manager import get_last_visited_page, set_last_selected_workflow, get_session_state
from src.core.theme_manager import switch_theme, get_current_theme_default


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
        
        # Create left frame container
        left_frame = ctk.CTkFrame(self.parent)
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create page container
        self.page_container = ctk.CTkFrame(self.parent)
        self.page_container.grid(row=0, column=1, sticky="nsew")
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)
        
        # Create navigation sidebar (top of left frame)
        self.side_nav = SideNav(left_frame, None)  # Temporary, will be updated
        self.side_nav.pack(fill="both", expand=True)
        
        # Create theme toggle (bottom of left frame)
        current_theme = get_session_state("pref_theme") or get_current_theme_default()
        self.theme_toggle = TwoOptionToggle(
            left_frame,
            "🌙 Dark Mode", "☀️ Light Mode",
            current_theme,
            self.on_theme_changed
        )
        self.theme_toggle.pack(side="bottom", pady=10)
        
        # Create page controller with sidebar reference
        self.page_controller = PageController(self.page_container, self.side_nav)
        
        # Update sidebar with controller reference
        self.side_nav.controller = self.page_controller
        
        # Register all pages from registry with navigation callback
        for page_config in get_pages():
            self.page_controller.add_page(
                page_config["name"], 
                page_config["class"],
                navigate_callback=self.navigate_to_page
            )
        
        # Show default page based on user state
        default_page = get_last_visited_page()
        self.page_controller.show_page(default_page)
    
    def navigate_to_page(self, page_name: str, **context) -> None:
        """Navigation callback for pages with state management"""
        # Handle state updates based on context
        if 'workflow_name' in context:
            set_last_selected_workflow(context['workflow_name'])
        
        # Navigate to page (controller handles state and highlighting)
        self.page_controller.show_page(page_name)
    
    def on_theme_changed(self, new_theme: str):
        """Handle theme change from toggle"""
        switch_theme(new_theme)