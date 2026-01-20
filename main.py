import customtkinter as ctk
import json
from async_tkinter_loop.mixins import AsyncCTk
from src.app_services import initialize_services, cleanup_services
from src.utils.state_manager import save_session_to_preferences
from src.core.theme_manager import initialize_app_theme
from ui.main_layout import MainLayout

class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        self.setup_application()
        self.layout = MainLayout(self)
    
    def setup_application(self) -> None:
        """Initialize application configuration and services"""
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize theme system
        initialize_app_theme(self)
        
        self.title(config['title'])
        self.geometry(config['geometry'])
        
        # Initialize global services
        initialize_services()
        
        # Setup cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle application shutdown with proper service cleanup"""
        # Save session state to preferences
        save_session_to_preferences()
        
        # Run cleanup (now sync since we have async loop)
        import asyncio
        asyncio.create_task(cleanup_services())
        # Destroy the window
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.async_mainloop()