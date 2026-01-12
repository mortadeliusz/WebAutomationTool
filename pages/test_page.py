"""
Test page to demonstrate element picker functionality with new architecture
"""

import customtkinter as ctk
from async_tkinter_loop import async_handler
from src.app_services import get_browser_controller
from src.core.element_picker_toggle import ElementPicker

class TestPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Element Picker Test", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20)
        
        # URL input
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.pack(pady=10, padx=20, fill="x")
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="Test URL:")
        self.url_label.pack(side="left", padx=(10, 5))
        
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="https://example.com")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.insert(0, "https://www.google.com")
        
        # Buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=20, padx=20, fill="x")
        
        self.launch_button = ctk.CTkButton(
            self.button_frame, 
            text="Launch Browser", 
            command=self.launch_browser_clicked
        )
        self.launch_button.pack(side="left", padx=(10, 5))
        
        self.pick_button = ctk.CTkButton(
            self.button_frame, 
            text="Pick Element", 
            command=self.pick_element_clicked
        )
        self.pick_button.pack(side="left", padx=5)
        
        self.new_page_button = ctk.CTkButton(
            self.button_frame, 
            text="Force Navigate", 
            command=self.force_navigate_clicked
        )
        self.new_page_button.pack(side="left", padx=5)
        
        # Results
        self.results_label = ctk.CTkLabel(self, text="Results:")
        self.results_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.results_text = ctk.CTkTextbox(self, height=200)
        self.results_text.pack(pady=(0, 20), padx=20, fill="both", expand=True)
        
    @async_handler
    async def launch_browser_clicked(self):
        """Launch browser without navigation (preserve user state)"""
        await self._launch_browser()
    
    @async_handler
    async def pick_element_clicked(self):
        """Pick element using current browser state"""
        await self._pick_element()
    
    @async_handler
    async def force_navigate_clicked(self):
        """Force navigate to URL (like task execution)"""
        await self._force_navigate()
    
    async def _launch_browser(self):
        try:
            self.log_result("Launching browser...")
            controller = get_browser_controller()
            
            url = self.url_entry.get() or "https://www.google.com"
            page = await controller.get_page("chrome", "test", url)
            
            if page:
                current_url = page.url
                self.log_result(f"✅ Browser launched successfully at: {current_url}")
            else:
                self.log_result("❌ Failed to launch browser")
                
        except Exception as e:
            self.log_result(f"❌ Error: {str(e)}")
    
    async def _pick_element(self):
        try:
            self.log_result("Starting element picker...")
            controller = get_browser_controller()
            
            # Get existing browser (don't navigate - preserve user state)
            url = self.url_entry.get() or "https://www.google.com"
            page = await controller.get_page("chrome", "test", url, force_navigate=False)
            
            if not page:
                self.log_result("❌ No browser available. Launch browser first.")
                return
            
            self.log_result(f"Using browser at: {page.url}")
            self.log_result("Click an element in the browser window...")
            
            # Use stateless element picker
            picker = ElementPicker()
            result = await picker.pick_element(page)
            
            if result['success']:
                self.log_result(f"✅ Element picked successfully!")
                self.log_result(f"XPath: {result['selector']}")
            else:
                self.log_result(f"❌ Element picking failed: {result['error']}")
                
        except Exception as e:
            self.log_result(f"❌ Error: {str(e)}")
    
    async def _force_navigate(self):
        try:
            self.log_result("Force navigating to URL...")
            controller = get_browser_controller()
            
            url = self.url_entry.get() or "https://www.google.com"
            page = await controller.get_page("chrome", "test", url, force_navigate=True)
            
            if page:
                self.log_result(f"✅ Navigated to: {page.url}")
            else:
                self.log_result("❌ Failed to navigate")
                
        except Exception as e:
            self.log_result(f"❌ Error: {str(e)}")
    
    def log_result(self, message: str):
        """Add message to results text box"""
        current_text = self.results_text.get("1.0", "end-1c")
        if current_text:
            new_text = current_text + "\n" + message
        else:
            new_text = message
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", new_text)
        
        # Auto-scroll to bottom
        self.results_text.see("end")