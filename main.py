import customtkinter as ctk
import json
import sys
import base64
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from async_tkinter_loop.mixins import AsyncCTk
from src.app_services import initialize_services, cleanup_services
from src.utils.state_manager import save_session_to_preferences
from src.core.theme_manager import initialize_app_theme
from ui.main_layout import MainLayout
from src.types import UserSessionData

# Setup logging
log_dir = Path("user_data/logs")
log_dir.mkdir(parents=True, exist_ok=True)

handlers = [logging.StreamHandler()]  # Console for development

# Add rotating file handler
file_handler = RotatingFileHandler(
    log_dir / "app.log",
    maxBytes=1 * 1024 * 1024,  # 1MB per file
    backupCount=5  # Keep 5 files (5MB total)
)
handlers.append(file_handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger(__name__)


def parse_user_data() -> Optional[UserSessionData]:
    """Parse user data from command line args"""
    if '--session' in sys.argv:
        idx = sys.argv.index('--session')
        if idx + 1 < len(sys.argv):
            try:
                decoded = base64.b64decode(sys.argv[idx + 1]).decode()
                return json.loads(decoded)
            except (json.JSONDecodeError, base64.binascii.Error, UnicodeDecodeError, ValueError):
                logger.warning("Failed to parse session data from command line")
                return None
    return None


class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        logger.info("Application starting")
        
        # Parse user data from launcher
        self.user_data = parse_user_data() or {}
        
        self.setup_application()
        self.layout = MainLayout(self, self.user_data)
        logger.info("Application initialized successfully")
    
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
        logger.info("Services initialized")
        
        # Setup cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle application shutdown with proper service cleanup"""
        logger.info("Application shutting down")
        save_session_to_preferences()
        
        import asyncio
        
        async def cleanup_and_exit():
            await cleanup_services()
            self.destroy()
        
        asyncio.create_task(cleanup_and_exit())

if __name__ == "__main__":
    try:
        app = App()
        app.async_mainloop()
    except Exception as e:
        logger.exception("Application crashed with unhandled exception")
        raise