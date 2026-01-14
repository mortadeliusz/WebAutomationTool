"""
Browser Controller - Launch and manage browser instances (Async)
"""

import asyncio
from typing import Dict, Optional, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from src.utils.browser_detector import BrowserDetector

class BrowserController:
    """Control browser instances using async Playwright with detected browsers"""
    
    def __init__(self):
        self.detector = BrowserDetector()
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.detected_browsers = self.detector.detect_installed_browsers()
    
    async def start(self) -> Dict[str, Any]:
        """Start Playwright"""
        if not self.playwright:
            try:
                self.playwright = await async_playwright().start()
                return {'success': True, 'error': None}
            except Exception as e:
                return {'success': False, 'error': f"Failed to start Playwright: {str(e)}"}
        return {'success': True, 'error': None}
    
    async def stop(self) -> Dict[str, Any]:
        """Stop all browsers and Playwright safely"""
        errors = []
        
        # Close all pages safely
        for alias, page in list(self.pages.items()):
            try:
                if not page.is_closed():
                    await page.close()
            except Exception as e:
                errors.append(f"Could not close page {alias}: {str(e)}")
        
        # Close all contexts safely
        for alias, context in list(self.contexts.items()):
            try:
                await context.close()
            except Exception as e:
                errors.append(f"Could not close context {alias}: {str(e)}")
        
        # Close all browsers safely
        for alias, browser in list(self.browsers.items()):
            try:
                if browser.is_connected():
                    await browser.close()
            except Exception as e:
                errors.append(f"Could not close browser {alias}: {str(e)}")
        
        # Stop playwright safely
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                errors.append(f"Could not stop playwright: {str(e)}")
        
        # Clear references
        self.pages.clear()
        self.contexts.clear()
        self.browsers.clear()
        self.playwright = None
        
        return {
            'success': len(errors) == 0,
            'errors': errors
        }
    
    async def launch_browser(self, browser_type: str, alias: str = "main") -> Dict[str, Any]:
        """Launch a browser instance"""
        if not self.playwright:
            start_result = await self.start()
            if not start_result['success']:
                return start_result
        
        # Check if browser is detected
        if browser_type not in self.detected_browsers:
            return {
                'success': False, 
                'error': f"Browser '{browser_type}' not found on system"
            }
        
        browser_info = self.detected_browsers[browser_type]
        executable_path = browser_info['path']
        
        try:
            # Launch browser based on engine type
            if browser_info['engine'] == 'chromium':
                browser = await self.playwright.chromium.launch(
                    executable_path=executable_path,
                    headless=False  # Show browser window
                )
            elif browser_info['engine'] == 'gecko':
                browser = await self.playwright.firefox.launch(
                    executable_path=executable_path,
                    headless=False
                )
            else:
                return {
                    'success': False,
                    'error': f"Unsupported browser engine: {browser_info['engine']}"
                }
            
            # Create context and page
            context = await browser.new_context()
            page = await context.new_page()
            
            # Store references
            self.browsers[alias] = browser
            self.contexts[alias] = context
            self.pages[alias] = page
            
            return {'success': True, 'error': None}
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to launch {browser_type}: {str(e)}"
            }
    
    async def navigate(self, url: str, alias: str = "main") -> Dict[str, Any]:
        """Navigate to URL"""
        if alias not in self.pages:
            return {
                'success': False,
                'error': f"No browser instance with alias '{alias}'"
            }
        
        try:
            page = self.pages[alias]
            await page.goto(url)
            return {'success': True, 'error': None}
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to navigate to {url}: {str(e)}"
            }
    
    def get_available_browsers(self) -> Dict[str, str]:
        """Get list of available browsers"""
        return {
            browser_id: info['name'] 
            for browser_id, info in self.detected_browsers.items()
        }
    
    async def get_page(self, browser_type: str, alias: str = "main", 
                       initial_url: str = None, force_navigate: bool = False) -> Optional[Page]:
        """
        Get browser page with configurable navigation behavior.
        
        Args:
            browser_type: Browser to use (chrome, firefox, etc.)
            alias: Browser instance identifier
            initial_url: URL for navigation
            force_navigate: If True, always navigate to initial_url
                           If False, navigate only if browser newly launched
                           
        Returns:
            Page object for automation, or None if failed
            
        Behavior:
            - If browser exists and force_navigate=False: Return existing page (preserve user navigation)
            - If browser missing: Launch browser, navigate to initial_url if provided
            - If force_navigate=True: Always navigate to initial_url
        """
        if not self.playwright:
            start_result = await self.start()
            if not start_result['success']:
                return None
        
        # Check if browser already exists and is healthy
        browser_exists = self.is_browser_running(alias)
        
        if not browser_exists:
            # Browser doesn't exist - launch new one
            launch_result = await self.launch_browser(browser_type, alias)
            if not launch_result['success']:
                return None
            
            # Navigate to initial URL if provided (new browser)
            if initial_url:
                nav_result = await self.navigate(initial_url, alias)
                if not nav_result['success']:
                    return None
        else:
            # Browser exists - navigate only if forced
            if force_navigate and initial_url:
                nav_result = await self.navigate(initial_url, alias)
                if not nav_result['success']:
                    return None
        
        return self.pages.get(alias)
    
    def get_page_direct(self, alias: str = "main") -> Optional[Page]:
        """Get page instance directly for backwards compatibility"""
        return self.pages.get(alias)
    
    def is_browser_running(self, alias: str = "main") -> bool:
        """Check if browser process is running (simple check)"""
        if alias not in self.browsers:
            return False
        
        try:
            browser = self.browsers[alias]
            return browser.is_connected()
        except:
            return False
    
    async def get_page_title(self, alias: str = "main") -> Optional[str]:
        """Get current page title"""
        if alias not in self.pages:
            return None
        
        try:
            return await self.pages[alias].title()
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
    
    async def wait_for_navigation(self, alias: str = "main", timeout: int = 30000) -> Dict[str, Any]:
        """Wait for page navigation - useful when user manually navigates"""
        if alias not in self.pages:
            return {
                'success': False,
                'error': f"No browser instance with alias '{alias}'"
            }
        
        try:
            page = self.pages[alias]
            await page.wait_for_load_state('networkidle', timeout=timeout)
            return {'success': True, 'error': None}
        except Exception as e:
            return {
                'success': False,
                'error': f"Navigation wait failed: {str(e)}"
            }
    
    def get_existing_page(self, alias: str = "main") -> Optional[Page]:
        """Get existing page or None if not found"""
        return self.pages.get(alias)
    
    async def launch_browser_page(self, browser_type: str, alias: str = "main") -> Optional[Page]:
        """Launch new browser and return page or None if failed"""
        result = await self.launch_browser(browser_type, alias)
        return self.pages.get(alias) if result['success'] else None
    
    async def close_browser_page(self, alias: str = "main") -> bool:
        """Close browser page and return True if successful, False if not found or failed"""
        if alias not in self.browsers:
            return False
        
        try:
            if alias in self.pages and not self.pages[alias].is_closed():
                await self.pages[alias].close()
            if alias in self.contexts:
                await self.contexts[alias].close()
            if self.browsers[alias].is_connected():
                await self.browsers[alias].close()
            
            self.pages.pop(alias, None)
            self.contexts.pop(alias, None)
            self.browsers.pop(alias, None)
            return True
        except:
            return False