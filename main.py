import customtkinter as ctk
import json
from async_tkinter_loop.mixins import AsyncCTk
from components.sidebar import Sidebar
from components.main_content import MainContent
from src.app_services import initialize_services, cleanup_services

class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Setup from config
        ctk.set_appearance_mode(config['appearance_mode'])
        ctk.set_default_color_theme(config['color_theme'])
        
        self.title(config['title'])
        self.geometry(config['geometry'])
        
        # Initialize global services
        initialize_services()
        
        # Setup cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create layout
        self.create_layout()
    
    def create_layout(self):
        # Create main content area
        self.main_content = MainContent(self)
        self.main_content.pack(side="right", fill="both", expand=True)
        
        # Create sidebar with main content dependency
        self.sidebar = Sidebar(self, self.main_content)
        self.sidebar.pack(side="left", fill="y")
    
    def on_closing(self):
        """Handle application shutdown with proper service cleanup"""
        # Run cleanup (now sync since we have async loop)
        import asyncio
        asyncio.create_task(cleanup_services())
        # Destroy the window
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.async_mainloop()