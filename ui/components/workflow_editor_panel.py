"""
Workflow Editor Panel - Edit workflow metadata and actions
"""

import customtkinter as ctk
from typing import Dict, Optional, Callable, List
from src.utils.workflow_files import save_workflow, create_workflow
from ui.components.browser_config_section import BrowserConfigSection


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
        
        # Browser configuration section
        self.browser_config = BrowserConfigSection(self)
        self.browser_config.pack(fill="x", padx=10, pady=10)
        
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
        
        # Load browser config
        browser_config = workflow.get('browsers', {}).get('main', {})
        self.browser_config.set_config(browser_config)
        
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
        self.current_workflow['browsers']['main'] = self.browser_config.get_config()
        
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
        self.browser_config.set_config({"browser_type": "chrome", "starting_url": ""})
        self.actions_list.set_actions([])