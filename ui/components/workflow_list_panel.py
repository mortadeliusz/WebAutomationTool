"""
Workflow List Panel - Display and manage workflow list
"""

import customtkinter as ctk
from typing import Dict, List, Optional, Callable
from src.utils.workflow_files import list_workflows, delete_workflow


class WorkflowListPanel(ctk.CTkFrame):
    def __init__(self, parent, on_workflow_selected: Callable[[str], None], on_status_update: Callable[[str], None]):
        super().__init__(parent)
        self.on_workflow_selected = on_workflow_selected
        self.on_status_update = on_status_update
        self.selected_workflow_name: Optional[str] = None
        self.setup_ui()
        self.refresh_workflow_list()
    
    def setup_ui(self):
        """Setup the workflow list UI"""
        # Header
        header = ctk.CTkLabel(self, text="Existing Workflows:", font=ctk.CTkFont(weight="bold"))
        header.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Workflow list
        self.workflow_listbox = ctk.CTkScrollableFrame(self, height=200)
        self.workflow_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Control buttons
        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        
        self.load_button = ctk.CTkButton(controls, text="Load", command=self.load_selected)
        self.load_button.pack(side="left", padx=(0, 5))
        
        self.delete_button = ctk.CTkButton(controls, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=5)
    
    def refresh_workflow_list(self):
        """Refresh the workflow list display"""
        # Clear existing items
        for widget in self.workflow_listbox.winfo_children():
            widget.destroy()
        
        workflows = list_workflows()
        
        if not workflows:
            no_workflows = ctk.CTkLabel(self.workflow_listbox, text="No workflows found")
            no_workflows.pack(pady=20)
            return
        
        # Display workflows
        for workflow in workflows:
            workflow_frame = ctk.CTkFrame(self.workflow_listbox)
            workflow_frame.pack(fill="x", padx=5, pady=2)
            
            info_text = f"{workflow['name']} ({workflow['browsers']}) - {workflow['actions_count']} actions"
            workflow_label = ctk.CTkLabel(workflow_frame, text=info_text)
            workflow_label.pack(side="left", padx=10, pady=5)
            
            # Make clickable
            workflow_frame.bind("<Button-1>", lambda e, name=workflow['name']: self.select_workflow(name))
            workflow_label.bind("<Button-1>", lambda e, name=workflow['name']: self.select_workflow(name))
    
    def select_workflow(self, workflow_name: str):
        """Select a workflow"""
        self.selected_workflow_name = workflow_name
        self.on_status_update(f"Selected: {workflow_name}")
    
    def load_selected(self):
        """Load the selected workflow"""
        if not self.selected_workflow_name:
            self.on_status_update("No workflow selected")
            return
        
        self.on_workflow_selected(self.selected_workflow_name)
    
    def delete_selected(self):
        """Delete the selected workflow"""
        if not self.selected_workflow_name:
            self.on_status_update("No workflow selected")
            return
        
        if delete_workflow(self.selected_workflow_name):
            self.on_status_update(f"Deleted: {self.selected_workflow_name}")
            self.refresh_workflow_list()
            self.selected_workflow_name = None
        else:
            self.on_status_update("Failed to delete workflow")