"""
Browser Test Page - Simple test for browser controller functionality
"""

import customtkinter as ctk
from async_tkinter_loop import async_handler
from src.app_services import get_browser_controller

class BrowserTestPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.browser_controller = get_browser_controller()
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = ctk.CTkLabel(self, text="Browser Test", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Button 1: Launch Chrome
        self.launch_btn = ctk.CTkButton(
            self, 
            text="Launch Chrome", 
            command=self.launch_chrome,
            width=200,
            height=40
        )
        self.launch_btn.pack(pady=10)
        
        # Button 2: Navigate to Google
        self.google_btn = ctk.CTkButton(
            self, 
            text="Navigate to Google", 
            command=self.navigate_google,
            width=200,
            height=40
        )
        self.google_btn.pack(pady=10)
        
        # Button 3: Navigate to wp.pl
        self.wp_btn = ctk.CTkButton(
            self, 
            text="Navigate to wp.pl", 
            command=self.navigate_wp,
            width=200,
            height=40
        )
        self.wp_btn.pack(pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=20)
    
    @async_handler
    async def launch_chrome(self):
        """Launch Chrome browser"""
        try:
            self.status_label.configure(text="Launching Chrome...")
            result = await self.browser_controller.launch_browser("chrome")
            
            if result['success']:
                self.status_label.configure(text="Chrome launched successfully")
            else:
                self.status_label.configure(text=f"Failed to launch Chrome: {result['error']}")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
    
    @async_handler
    async def navigate_google(self):
        """Navigate to Google"""
        try:
            self.status_label.configure(text="Navigating to Google...")
            result = await self.browser_controller.navigate("https://www.google.com")
            
            if result['success']:
                self.status_label.configure(text="Navigated to Google")
            else:
                self.status_label.configure(text=f"Failed to navigate: {result['error']}")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
    
    @async_handler
    async def navigate_wp(self):
        """Navigate to wp.pl"""
        try:
            self.status_label.configure(text="Navigating to wp.pl...")
            result = await self.browser_controller.navigate("https://www.wp.pl")
            
            if result['success']:
                self.status_label.configure(text="Navigated to wp.pl")
            else:
                self.status_label.configure(text=f"Failed to navigate: {result['error']}")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")