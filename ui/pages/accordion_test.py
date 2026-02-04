import customtkinter as ctk
from ui.components.accordion import Accordion


class AccordionTestPage(ctk.CTkFrame):
    """Test page for Accordion component"""
    
    def __init__(self, parent, navigate_callback=None):
        super().__init__(parent)
        self.navigate_callback = navigate_callback
        self.setup_ui()
    
    def setup_ui(self):
        """Setup test page with multiple accordions"""
        # Page title
        title = ctk.CTkLabel(
            self, 
            text="Accordion Component Test", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Scrollable container
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Test Accordion 1: Workflow Setup (expanded by default)
        accordion1 = Accordion(container, "Workflow Setup", expanded=True)
        accordion1.pack(fill="x", pady=(0, 10))
        
        # Add content to accordion1
        name_label = ctk.CTkLabel(accordion1.content_frame, text="Workflow Name:")
        name_label.pack(anchor="w", pady=(10, 5))
        
        name_entry = ctk.CTkEntry(accordion1.content_frame, placeholder_text="Enter workflow name")
        name_entry.pack(fill="x", pady=(0, 10))
        
        browser_label = ctk.CTkLabel(accordion1.content_frame, text="Browser Type:")
        browser_label.pack(anchor="w", pady=(0, 5))
        
        browser_combo = ctk.CTkComboBox(accordion1.content_frame, values=["chrome", "firefox", "edge"])
        browser_combo.pack(fill="x", pady=(0, 10))
        
        # Test Accordion 2: Actions (collapsed by default)
        accordion2 = Accordion(container, "Actions", expanded=False)
        accordion2.pack(fill="x", pady=(0, 10))
        
        # Add content to accordion2
        actions_label = ctk.CTkLabel(accordion2.content_frame, text="Action List:")
        actions_label.pack(anchor="w", pady=(10, 5))
        
        for i in range(3):
            action_frame = ctk.CTkFrame(accordion2.content_frame)
            action_frame.pack(fill="x", pady=2)
            
            action_label = ctk.CTkLabel(action_frame, text=f"Action {i+1}: Click Element")
            action_label.pack(side="left", padx=10, pady=5)
            
            edit_btn = ctk.CTkButton(action_frame, text="Edit", width=60)
            edit_btn.pack(side="right", padx=10, pady=5)
        
        # Test Accordion 3: Advanced Settings (collapsed by default)
        accordion3 = Accordion(container, "Advanced Settings", expanded=False)
        accordion3.pack(fill="x", pady=(0, 10))
        
        # Add content to accordion3
        timeout_label = ctk.CTkLabel(accordion3.content_frame, text="Timeout (seconds):")
        timeout_label.pack(anchor="w", pady=(10, 5))
        
        timeout_entry = ctk.CTkEntry(accordion3.content_frame, placeholder_text="30")
        timeout_entry.pack(fill="x", pady=(0, 10))
        
        retry_label = ctk.CTkLabel(accordion3.content_frame, text="Retry Attempts:")
        retry_label.pack(anchor="w", pady=(0, 5))
        
        retry_entry = ctk.CTkEntry(accordion3.content_frame, placeholder_text="3")
        retry_entry.pack(fill="x", pady=(0, 10))
        
        debug_checkbox = ctk.CTkCheckBox(accordion3.content_frame, text="Enable Debug Mode")
        debug_checkbox.pack(anchor="w", pady=(0, 10))
        
        # Test buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        test_btn = ctk.CTkButton(button_frame, text="Test Action", height=40)
        test_btn.pack(side="left", padx=(10, 5), pady=10)
        
        save_btn = ctk.CTkButton(button_frame, text="Save Configuration", height=40)
        save_btn.pack(side="right", padx=(5, 10), pady=10)