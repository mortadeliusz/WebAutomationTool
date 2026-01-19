"""
Workflow Management Page - Create and edit automation workflows
Uses mini-controller pattern for list-detail view switching
"""

import customtkinter as ctk
from typing import Optional
from ui.components.workflow_list_view import WorkflowListView
from ui.components.workflow_editor_view import WorkflowEditorView


class WorkflowManagementPage(ctk.CTkFrame):
    """Mini-controller for workflow list-detail views"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_views()
        self.show_list_view()
    
    def setup_views(self):
        """Setup list and editor views with grid management"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # List view
        self.list_view = WorkflowListView(
            self,
            on_edit=self.show_editor_view,
            on_new=lambda: self.show_editor_view(None),
            on_delete=self.on_workflow_deleted
        )
        self.list_view.grid(row=0, column=0, sticky="nsew")
        
        # Editor view
        self.editor_view = WorkflowEditorView(
            self,
            on_save=self.on_workflow_saved,
            on_cancel=self.show_list_view
        )
        self.editor_view.grid(row=0, column=0, sticky="nsew")
        self.editor_view.grid_remove()
    
    def show_list_view(self):
        """Show list view, hide editor view"""
        self.editor_view.grid_remove()
        self.list_view.grid()
        self.list_view.refresh()
    
    def show_editor_view(self, workflow_name: Optional[str]):
        """Show editor view, hide list view"""
        self.list_view.grid_remove()
        self.editor_view.grid()
        self.editor_view.load_workflow(workflow_name)
    
    def on_workflow_saved(self):
        """Handle workflow save - return to list"""
        self.show_list_view()
    
    def on_workflow_deleted(self, workflow_name: str):
        """Handle workflow deletion"""
        # List view already refreshed itself
        pass