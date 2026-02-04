"""
Browser Instance - Single editable browser card
"""

import customtkinter as ctk
from typing import Dict, Callable, Optional
from async_tkinter_loop import async_handler
from src.app_services import get_browser_controller, get_browser_state_observer


def get_browser_display_mapping() -> Dict[str, str]:
    """Get browser display mapping (cached, detects once per session)"""
    from src.utils.browser_detector import BrowserDetector
    
    global _browser_display_cache
    if '_browser_display_cache' not in globals():
        detector = BrowserDetector()
        installed = detector.detect_installed_browsers()
        
        installed_browsers = {}
        not_installed_browsers = {}
        
        for browser_id, config in detector.SUPPORTED_BROWSERS.items():
            display_name = config['name']
            if browser_id in installed:
                installed_browsers[browser_id] = display_name
            else:
                not_installed_browsers[browser_id] = display_name + " (not installed)"
        
        _browser_display_cache = {**installed_browsers, **not_installed_browsers}
    
    return _browser_display_cache


def _get_browser_id_from_display(display_name: str) -> str:
    """Get browser ID from display name (reverse lookup)"""
    mapping = get_browser_display_mapping()
    return next(k for k, v in mapping.items() if v == display_name)


class BrowserInstance(ctk.CTkFrame):
    """Single editable browser instance card"""
    
    def __init__(
        self,
        parent,
        alias: str,
        show_alias: bool,
        show_delete: bool,
        on_save: Callable,
        on_delete: Optional[Callable] = None,
        on_rename: Optional[Callable] = None
    ):
        super().__init__(parent)
        self.alias = alias
        self.show_alias = show_alias
        self.show_delete = show_delete
        self.on_save = on_save
        self.on_delete = on_delete
        self.on_rename = on_rename
        self.config = {"browser_type": "chrome", "starting_url": ""}
        
        # Subscribe to browser state changes
        observer = get_browser_state_observer()
        observer.subscribe(self._on_browser_state_changed)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the browser instance UI"""
        # Status and alias row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(header, text="⚪ Not Running")
        self.status_label.pack(side="left")
        
        if self.show_alias:
            alias_label = ctk.CTkLabel(
                header,
                text=f"  |  Alias: {self.alias}",
                font=ctk.CTkFont(weight="bold")
            )
            alias_label.pack(side="left")
            
            if self.on_rename:
                rename_btn = ctk.CTkButton(
                    header,
                    text="Rename",
                    width=70,
                    command=self._on_rename_clicked
                )
                rename_btn.pack(side="left", padx=(5, 0))
        
        # Browser type
        browser_frame = ctk.CTkFrame(self, fg_color="transparent")
        browser_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(browser_frame, text="Browser Type:").pack(side="left", padx=(0, 5))
        
        display_values = list(get_browser_display_mapping().values())
        self.browser_combo = ctk.CTkComboBox(
            browser_frame,
            values=display_values,
            width=200
        )
        self.browser_combo.pack(side="left")
        if display_values:
            self.browser_combo.set(display_values[0])
        
        # Starting URL
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(url_frame, text="Starting URL:").pack(side="left", padx=(0, 5))
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://example.com (optional)"
        )
        self.url_entry.pack(side="left", fill="x", expand=True)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.launch_button = ctk.CTkButton(
            button_frame,
            text="Launch",
            command=self._on_launch_clicked
        )
        self.launch_button.pack(side="left", padx=(0, 5))
        
        self.close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self._on_close_clicked,
            state="disabled"
        )
        self.close_button.pack(side="left", padx=(0, 5))
        
        self.save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save_clicked
        )
        self.save_button.pack(side="left")
        
        if self.show_delete and self.on_delete:
            delete_btn = ctk.CTkButton(
                button_frame,
                text="🗑️",
                width=40,
                command=self._on_delete_clicked
            )
            delete_btn.pack(side="right")
    
    def get_config(self) -> Dict:
        """Get current browser configuration"""
        return {
            "browser_type": _get_browser_id_from_display(self.browser_combo.get()),
            "starting_url": self.url_entry.get().strip()
        }
    
    def set_config(self, config: Dict):
        """Set browser configuration"""
        self.config = config.copy()
        
        # Set browser type
        browser_id = config.get("browser_type", "chrome")
        display_mapping = get_browser_display_mapping()
        display_name = display_mapping.get(browser_id, browser_id)
        self.browser_combo.set(display_name)
        
        # Set URL
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, config.get("starting_url", ""))
        
        self._update_button_states()
    
    def _on_save_clicked(self):
        """Handle save button click"""
        config = self.get_config()
        self.on_save(self.alias, config)
    
    def _on_rename_clicked(self):
        """Handle rename button click"""
        if self.on_rename:
            self.on_rename(self.alias)
    
    @async_handler
    async def _on_delete_clicked(self):
        """Handle delete button click"""
        if self.on_delete:
            await self.on_delete(self.alias)
    
    @async_handler
    async def _on_launch_clicked(self):
        """Handle launch button click"""
        browser_type = _get_browser_id_from_display(self.browser_combo.get())
        starting_url = self.url_entry.get().strip()
        
        self.status_label.configure(text="⚪ Launching...")
        self.launch_button.configure(state="disabled")
        
        try:
            controller = get_browser_controller()
            page = await controller.get_page(
                browser_type,
                self.alias,
                starting_url,
                force_navigate=True
            )
            
            if page:
                self.status_label.configure(text="🟢 Running")
                self.launch_button.configure(state="disabled")
                self.close_button.configure(state="normal")
            else:
                self.status_label.configure(text="🔴 Failed")
                self.launch_button.configure(state="normal")
        except Exception:
            self.status_label.configure(text="🔴 Error")
            self.launch_button.configure(state="normal")
    
    @async_handler
    async def _on_close_clicked(self):
        """Handle close button click"""
        self.status_label.configure(text="⚪ Closing...")
        self.close_button.configure(state="disabled")
        
        try:
            controller = get_browser_controller()
            success = await controller.close_browser_page(self.alias)
            
            if success:
                self.status_label.configure(text="⚪ Not Running")
                self.launch_button.configure(state="normal")
                self.close_button.configure(state="disabled")
            else:
                self.status_label.configure(text="⚠️ Close Failed")
                self.close_button.configure(state="normal")
        except Exception:
            self.status_label.configure(text="🔴 Error")
            self.close_button.configure(state="normal")
    
    def _on_browser_state_changed(self, event_type: str, alias: str):
        """React to browser state changes"""
        if alias == self.alias:
            self._update_button_states()
    
    def _update_button_states(self):
        """Update button states based on browser status"""
        try:
            controller = get_browser_controller()
            is_running = controller.is_browser_running(self.alias)
            
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
    
    def destroy(self):
        """Cleanup: unsubscribe from browser state observer"""
        try:
            observer = get_browser_state_observer()
            observer.unsubscribe(self._on_browser_state_changed)
        except:
            pass
        super().destroy()
