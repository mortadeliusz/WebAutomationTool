"""
Workflow Management Page - Create and edit automation workflows
"""

import customtkinter as ctk
from src.utils.workflow_files import load_workflow
from ui.components.workflow_list_panel import WorkflowListPanel
from ui.components.workflow_editor_panel import WorkflowEditorPanel
from ui.components.status_bar import StatusBar


class WorkflowManagementPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Title
        title = ctk.CTkLabel(self, text="Workflow Management", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Main container with two columns
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Workflow list
        self.workflow_list = WorkflowListPanel(
            main_frame, 
            on_workflow_selected=self.on_workflow_selected,
            on_status_update=self.on_status_update
        )
        self.workflow_list.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        # Right panel - Workflow editor
        self.workflow_editor = WorkflowEditorPanel(
            main_frame,
            on_status_update=self.on_status_update,
            on_workflow_saved=self.on_workflow_saved
        )
        self.workflow_editor.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Status bar
        self.status_bar = StatusBar(self)
        self.status_bar.pack(pady=(0, 10))
    
    def on_workflow_selected(self, workflow_name: str):
        """Handle workflow selection"""
        workflow = load_workflow(workflow_name)
        if workflow:
            self.workflow_editor.load_workflow(workflow)
            self.status_bar.update_status(f"Loaded: {workflow['name']}")
        else:
            self.status_bar.update_status("Failed to load workflow")
    
    def on_workflow_saved(self):
        """Handle workflow save"""
        self.workflow_list.refresh_workflow_list()
    
    def on_status_update(self, message: str):
        """Handle status updates"""
        self.status_bar.update_status(message)