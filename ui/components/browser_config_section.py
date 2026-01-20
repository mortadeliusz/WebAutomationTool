"""
Browser Configuration Section - Collapsible browser settings
"""

import customtkinter as ctk
from typing import Dict, Optional
from async_tkinter_loop import async_handler
from src.app_services import get_browser_controller


class BrowserConfigSection(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_expanded = True
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the browser configuration UI"""
        # Header with collapse button
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=5, pady=5)
        
        self.collapse_button = ctk.CTkButton(
            header, 
            text="▼ Browser Configuration",
            command=self.toggle_collapse,
            width=200,
            anchor="w"
        )
        self.collapse_button.pack(side="left", padx=5)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(header, text="⚪ Not Running")
        self.status_label.pack(side="left", padx=10)
        
        # Content frame (collapsible)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="x", padx=10, pady=5)
        
        # Browser type
        browser_frame = ctk.CTkFrame(self.content_frame)
        browser_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(browser_frame, text="Browser Type:").pack(side="left", padx=(10, 5))
        self.browser_combo = ctk.CTkComboBox(
            browser_frame, 
            values=["chrome", "firefox", "edge"],
            width=150
        )
        self.browser_combo.pack(side="left", padx=5)
        self.browser_combo.set("chrome")
        
        # Starting URL
        url_frame = ctk.CTkFrame(self.content_frame)
        url_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(url_frame, text="Starting URL:").pack(side="left", padx=(10, 5))
        self.url_entry = ctk.CTkEntry(
            url_frame, 
            placeholder_text="https://example.com (optional)"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Control buttons
        button_frame = ctk.CTkFrame(self.content_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.launch_button = ctk.CTkButton(
            button_frame,
            text="Launch Browser",
            command=self.on_launch_clicked
        )
        self.launch_button.pack(side="left", padx=(10, 5))
        
        self.close_button = ctk.CTkButton(
            button_frame,
            text="Close Browser",
            command=self.on_close_clicked,
            state="disabled"
        )
        self.close_button.pack(side="left", padx=5)
    
    def toggle_collapse(self):
        """Toggle the collapsed state"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.content_frame.pack(fill="x", padx=10, pady=5)
            self.collapse_button.configure(text="▼ Browser Configuration")
        else:
            self.content_frame.pack_forget()
            self.collapse_button.configure(text="▶ Browser Configuration")
    
    def get_config(self) -> Dict:
        """Get current browser configuration"""
        return {
            "browser_type": self.browser_combo.get(),
            "starting_url": self.url_entry.get()
        }
    
    def set_config(self, config: Dict):
        """Set browser configuration"""
        browser_type = config.get("browser_type", "chrome")
        self.browser_combo.set(browser_type)
        
        starting_url = config.get("starting_url", "")
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, starting_url)
        
        self.update_button_states()
    
    @async_handler
    async def on_launch_clicked(self):
        """Handle launch button click"""
        browser_type = self.browser_combo.get()
        starting_url = self.url_entry.get().strip()
        
        self.status_label.configure(text="⚪ Launching...")
        self.launch_button.configure(state="disabled")
        
        try:
            controller = get_browser_controller()
            
            if controller.is_browser_running("main"):
                self.status_label.configure(text="🟢 Already Running")
                self.launch_button.configure(state="disabled")
                self.close_button.configure(state="normal")
                return
            
            result = await controller.launch_browser(browser_type, "main")
            
            if result['success']:
                if starting_url:
                    nav_result = await controller.navigate(starting_url, "main")
                    if not nav_result['success']:
                        self.status_label.configure(text="⚠️ Navigation Failed")
                        self.launch_button.configure(state="normal")
                        return
                
                self.status_label.configure(text="🟢 Running")
                self.launch_button.configure(state="disabled")
                self.close_button.configure(state="normal")
            else:
                self.status_label.configure(text="🔴 Failed")
                self.launch_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text="🔴 Error")
            self.launch_button.configure(state="normal")
    
    def update_button_states(self):
        """Update button states based on browser status"""
        try:
            controller = get_browser_controller()
            is_running = controller.is_browser_running("main")
            
            if is_running:
                self.status_label.configure(text="🟢 Running")
                self.launch_button.configure(state="disabled")
                self.close_button.configure(state="normal")
            else:
                self.status_label.configure(text="⚪ Not Running")
                self.launch_button.configure(state="normal")
                self.close_button.configure(state="disabled")
        except:
            self.status_label.configure(text="⚪ Not Running")
            self.launch_button.configure(state="normal")
            self.close_button.configure(state="disabled")
    
    @async_handler
    async def on_close_clicked(self):
        """Handle close button click"""
        self.status_label.configure(text="⚪ Closing...")
        self.close_button.configure(state="disabled")
        
        try:
            controller = get_browser_controller()
            success = await controller.close_browser_page("main")
            
            if success:
                self.status_label.configure(text="⚪ Not Running")
                self.launch_button.configure(state="normal")
                self.close_button.configure(state="disabled")
            else:
                self.status_label.configure(text="⚠️ Close Failed")
                self.close_button.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text="🔴 Error")
            self.close_button.configure(state="normal")
