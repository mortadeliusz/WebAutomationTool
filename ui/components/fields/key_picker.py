"""
Key Picker Field - Capture keyboard key press
"""

import customtkinter as ctk


class KeyPickerField(ctk.CTkFrame):
    """Field for capturing keyboard key press"""
    
    def __init__(self, parent, label: str = "Key", placeholder: str = "Click 🎹 then press key"):
        super().__init__(parent)
        self.label_text = label
        self.placeholder = placeholder
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the key picker UI"""
        # Label
        self.label = ctk.CTkLabel(self, text=self.label_text)
        self.label.pack(side="left", padx=(0, 10))
        
        # Entry field
        self.entry = ctk.CTkEntry(self, placeholder_text=self.placeholder)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Picker button
        self.pick_button = ctk.CTkButton(
            self,
            text="🎹",
            width=40,
            command=self.start_key_capture
        )
        self.pick_button.pack(side="left")
    
    def start_key_capture(self):
        """Start listening for key press with overlay"""
        from ui.components.action_overlay import ActionOverlay
        
        # Show overlay
        self.overlay = ActionOverlay(
            parent=self.winfo_toplevel(),
            title="🎹 Key Capture Active",
            message="Press the key you want to use\nfor this action.\n\nExamples: Enter, Tab, Escape, Space",
            on_cancel=self.cancel_key_capture
        )
        
        # Start key capture
        self.entry.delete(0, 'end')
        self.entry.insert(0, "Press any key...")
        self.entry.focus()
        self.entry.bind("<Key>", self.on_key_pressed)
    
    def on_key_pressed(self, event):
        """Capture key press and close overlay"""
        key_name = event.keysym
        self.entry.delete(0, 'end')
        self.entry.insert(0, key_name)
        self.entry.unbind("<Key>")
        
        # Close overlay
        if hasattr(self, 'overlay'):
            self.overlay.close()
            delattr(self, 'overlay')
        
        return "break"  # Prevent default key behavior
    
    def cancel_key_capture(self):
        """Cancel key capture operation"""
        self.entry.unbind("<Key>")
        self.entry.delete(0, 'end')
        self.entry.insert(0, "")
    
    def get_value(self) -> str:
        """Get the captured key"""
        return self.entry.get()
    
    def set_value(self, value: str):
        """Set the key value"""
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
