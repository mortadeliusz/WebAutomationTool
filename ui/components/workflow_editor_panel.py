"""
Workflow Editor Panel - Edit workflow metadata and actions
"""

import customtkinter as ctk
from typing import Dict, Optional, Callable, List
from src.utils.workflow_files import save_workflow, create_workflow


class WorkflowEditorPanel(ctk.CTkFrame):
    def __init__(self, parent, on_status_update: Callable[[str], None], on_workflow_saved: Callable[[], None]):
        super().__init__(parent)
        self.on_status_update = on_status_update
        self.on_workflow_saved = on_workflow_saved
        self.current_workflow: Optional[Dict] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the workflow editor UI"""
        # Metadata form
        form_label = ctk.CTkLabel(self, text="Workflow Details:", font=ctk.CTkFont(weight="bold"))
        form_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Name field
        name_frame = ctk.CTkFrame(self)
        name_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(name_frame, text="Name:").pack(side="left", padx=(10, 5))
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Enter workflow name")
        self.name_entry.pack(side="right", fill="x", expand=True, padx=(0, 10))
        
        # Browser field
        browser_frame = ctk.CTkFrame(self)
        browser_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(browser_frame, text="Browser:").pack(side="left", padx=(10, 5))
        self.browser_combo = ctk.CTkComboBox(browser_frame, values=["chrome", "firefox"])
        self.browser_combo.pack(side="right", padx=(0, 10))
        self.browser_combo.set("chrome")
        
        # URL field
        url_frame = ctk.CTkFrame(self)
        url_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(url_frame, text="Starting URL:").pack(side="left", padx=(10, 5))
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://example.com")
        self.url_entry.pack(side="right", fill="x", expand=True, padx=(0, 10))
        
        # Control buttons
        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=10, pady=10)
        
        self.new_button = ctk.CTkButton(controls, text="New Workflow", command=self.create_new)
        self.new_button.pack(side="left", padx=(0, 5))
        
        self.save_button = ctk.CTkButton(controls, text="Save", command=self.save_current)
        self.save_button.pack(side="left", padx=5)
        
        # Actions section
        from ui.components.actions_list import ActionsList
        self.actions_list = ActionsList(self, self.on_actions_changed)
        self.actions_list.pack(fill="both", expand=True, padx=10, pady=(20, 10))
    
    def load_workflow(self, workflow: Dict):
        """Load workflow data into the editor"""
        self.current_workflow = workflow
        
        # Populate form
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, workflow.get('name', ''))
        
        browser_type = workflow.get('browsers', {}).get('main', {}).get('browser_type', 'chrome')
        self.browser_combo.set(browser_type)
        
        starting_url = workflow.get('browsers', {}).get('main', {}).get('starting_url', '')
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, starting_url)
        
        # Load actions into ActionsList
        actions = workflow.get('actions', [])
        self.actions_list.set_actions(actions)
    
    def create_new(self):
        """Create a new workflow"""
        self.current_workflow = create_workflow("New Workflow")
        self.load_workflow(self.current_workflow)
        self.on_status_update("New workflow created")
    
    def save_current(self):
        """Save the current workflow"""
        if not self.current_workflow:
            self.on_status_update("No workflow to save")
            return
        
        # Update workflow with form data
        self.current_workflow['name'] = self.name_entry.get() or "Unnamed Workflow"
        self.current_workflow['browsers']['main']['browser_type'] = self.browser_combo.get()
        self.current_workflow['browsers']['main']['starting_url'] = self.url_entry.get()
        
        if save_workflow(self.current_workflow):
            self.on_status_update(f"Saved: {self.current_workflow['name']}")
            self.on_workflow_saved()
        else:
            self.on_status_update("Failed to save workflow")
    

    
    def on_actions_changed(self, actions: List[Dict]):
        """Handle actions list changes"""
        if self.current_workflow:
            self.current_workflow['actions'] = actions
    
    def clear_form(self):
        """Clear the form"""
        self.current_workflow = None
        self.name_entry.delete(0, "end")
        self.browser_combo.set("chrome")
        self.url_entry.delete(0, "end")
        self.actions_list.set_actions([])