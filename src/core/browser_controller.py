"""
Browser Controller - Launch and manage browser instances
"""

from typing import Dict, Optional, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from utils.browser_detector import BrowserDetector

class BrowserController:
    """Control browser instances using Playwright with detected browsers"""
    
    def __init__(self):
        self.detector = BrowserDetector()
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.detected_browsers = self.detector.detect_installed_browsers()
    
    def start(self):
        """Start Playwright"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
    
    def stop(self):
        """Stop all browsers and Playwright safely"""
        # Close all pages safely
        for alias, page in list(self.pages.items()):
            try:
                if not page.is_closed():
                    page.close()
            except Exception as e:
                print(f"Warning: Could not close page {alias}: {e}")
        
        # Close all contexts safely
        for alias, context in list(self.contexts.items()):
            try:
                context.close()
            except Exception as e:
                print(f"Warning: Could not close context {alias}: {e}")
        
        # Close all browsers safely
        for alias, browser in list(self.browsers.items()):
            try:
                if browser.is_connected():
                    browser.close()
            except Exception as e:
                print(f"Warning: Could not close browser {alias}: {e}")
        
        # Stop playwright safely
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                print(f"Warning: Could not stop playwright: {e}")
        
        # Clear references
        self.pages.clear()
        self.contexts.clear()
        self.browsers.clear()
        self.playwright = None
    
    def launch_browser(self, browser_type: str, alias: str = "main") -> bool:
        """Launch a browser instance"""
        if not self.playwright:
            self.start()
        
        # Check if browser is detected
        if browser_type not in self.detected_browsers:
            raise ValueError(f"Browser '{browser_type}' not found on system")
        
        browser_info = self.detected_browsers[browser_type]
        executable_path = browser_info['path']
        
        try:
            # Launch browser based on engine type
            if browser_info['engine'] == 'chromium':
                browser = self.playwright.chromium.launch(
                    executable_path=executable_path,
                    headless=False  # Show browser window
                )
            elif browser_info['engine'] == 'gecko':
                browser = self.playwright.firefox.launch(
                    executable_path=executable_path,
                    headless=False
                )
            else:
                raise ValueError(f"Unsupported browser engine: {browser_info['engine']}")
            
            # Create context and page
            context = browser.new_context()
            page = context.new_page()
            
            # Store references
            self.browsers[alias] = browser
            self.contexts[alias] = context
            self.pages[alias] = page
            
            return True
            
        except Exception as e:
            print(f"Failed to launch {browser_type}: {e}")
            return False
    
    def navigate(self, url: str, alias: str = "main") -> bool:
        """Navigate to URL"""
        if alias not in self.pages:
            raise ValueError(f"No browser instance with alias '{alias}'")
        
        try:
            page = self.pages[alias]
            page.goto(url)
            return True
        except Exception as e:
            print(f"Failed to navigate to {url}: {e}")
            return False
    
    def wait_for_user_input(self, message: str = "Click Continue when ready") -> None:
        """Pause execution and wait for user input"""
        print(f"\n{message}")
        input("Press Enter to continue...")
    
    def get_available_browsers(self) -> Dict[str, str]:
        """Get list of available browsers"""
        return {
            browser_id: info['name'] 
            for browser_id, info in self.detected_browsers.items()
        }
    
    def is_browser_running(self, alias: str = "main") -> bool:
        """Check if browser process is running (simple check)"""
        if alias not in self.browsers:
            return False
        
        try:
            browser = self.browsers[alias]
            return browser.is_connected()
        except:
            return False
    
    def get_page_title(self, alias: str = "main") -> Optional[str]:
        """Get current page title"""
        if alias not in self.pages:
            return None
        
        try:
            return self.pages[alias].title()
        except Exception:
            return None
    
    def get_current_url(self, alias: str = "main") -> Optional[str]:
        """Get current page URL - useful for hybrid workflow"""
        if alias not in self.pages:
            return None
        
        try:
            return self.pages[alias].url
        except Exception:
            return None
    
    def wait_for_navigation(self, alias: str = "main", timeout: int = 30000) -> bool:
        """Wait for page navigation - useful when user manually navigates"""
        if alias not in self.pages:
            return False
        
        try:
            page = self.pages[alias]
            page.wait_for_load_state('networkidle', timeout=timeout)
            return True
        except Exception:
            return False