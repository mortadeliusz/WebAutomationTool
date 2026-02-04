"""
Workflow Management Page - Create and edit automation workflows
Uses mini-controller pattern for list-detail view switching
"""

import customtkinter as ctk
from typing import Optional
from ui.components.workflow_list_view import WorkflowListView
from ui.components.workflow_single_page_editor import WorkflowSinglePageEditor



class WorkflowManagementPage(ctk.CTkFrame):
    """Mini-controller for workflow list-detail views"""
    
    def __init__(self, parent, navigate_callback=None):
        super().__init__(parent)
        self.navigate_callback = navigate_callback
        self.setup_ui()
        self.show_list()
    
    def setup_ui(self):
        """Setup list and editor views"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # List view
        self.list_view = WorkflowListView(
            self,
            on_edit=self.show_editor,
            on_new=self.show_new_editor,
            on_delete=self.on_workflow_deleted,
            on_execute=self.execute_workflow
        )
        self.list_view.grid(row=0, column=0, sticky="nsew")
        
        # Editor view
        self.editor = WorkflowSinglePageEditor(
            self,
            on_save=self.on_workflow_saved,
            on_cancel=self.show_list
        )
        self.editor.grid(row=0, column=0, sticky="nsew")
        self.editor.grid_remove()

    
    def show_list(self):
        """Show list view"""
        self.editor.grid_remove()
        self.list_view.grid()
        self.list_view.refresh()
    
    def show_editor(self, workflow_name: str):
        """Show editor for existing workflow"""
        self.list_view.grid_remove()
        self.editor.grid()
        self.editor.load_workflow(workflow_name)
    
    def show_new_editor(self):
        """Show editor for new workflow"""
        self.list_view.grid_remove()
        self.editor.grid()
        self.editor.load_workflow(None)
    
    def on_workflow_saved(self):
        """Handle workflow save - return to list"""
        self.show_list()
    
    def on_workflow_deleted(self, workflow_name: str):
        """Handle workflow deletion - list refreshes itself"""
        pass
    
    def execute_workflow(self, workflow_name: str):
        """Execute workflow - navigate to execution page"""
        if self.navigate_callback:
            self.navigate_callback("workflow_execution", workflow_name=workflow_name)