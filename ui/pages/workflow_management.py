"""
Workflow Management Page - Create and edit automation workflows
Uses mini-controller pattern for list-detail-wizard view switching
"""

import customtkinter as ctk
from typing import Optional
from ui.components.workflow_list_view import WorkflowListView
from ui.components.single_page_editor_view import SinglePageEditorView
from ui.components.wizard_editor_view import WizardEditorView
from ui.components.two_option_toggle import TwoOptionToggle
from src.utils.state_manager import get_wizard_mode_preference, set_wizard_mode_preference


class WorkflowManagementPage(ctk.CTkFrame):
    """Mini-controller for workflow list-detail-wizard views"""
    
    def __init__(self, parent, navigate_callback=None):
        super().__init__(parent)
        self.navigate_callback = navigate_callback
        self.wizard_mode = get_wizard_mode_preference()  # Controller manages mode
        self.setup_views()
        self.show_list_view()
    
    def setup_views(self):
        """Setup three views with grid management"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Content area
        
        # Mode toggle at controller level
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Editor Mode:",
            font=ctk.CTkFont(weight="bold")
        )
        mode_label.pack(side="left")
        
        # Two-option toggle
        initial_option = "Wizard Mode" if self.wizard_mode else "Single Page Mode"
        self.mode_toggle = TwoOptionToggle(
            mode_frame,
            "Wizard Mode",
            "Single Page Mode",
            initial_option=initial_option,
            on_change=self.on_mode_changed
        )
        self.mode_toggle.pack(side="left", padx=(10, 0))
        
        # List view
        self.list_view = WorkflowListView(
            self,
            on_edit=self.show_editor_view,
            on_new=lambda: self.show_editor_view(None),
            on_delete=self.on_workflow_deleted,
            on_execute=self.execute_workflow
        )
        self.list_view.grid(row=1, column=0, sticky="nsew")
        
        # Single page editor
        self.single_editor = SinglePageEditorView(
            self,
            on_save=self.on_workflow_saved,
            on_cancel=self.show_list_view
        )
        self.single_editor.grid(row=1, column=0, sticky="nsew")
        self.single_editor.grid_remove()
        
        # Wizard editor
        self.wizard_editor = WizardEditorView(
            self,
            on_save=self.on_workflow_saved,
            on_cancel=self.show_list_view
        )
        self.wizard_editor.grid(row=1, column=0, sticky="nsew")
        self.wizard_editor.grid_remove()
    
    def on_mode_changed(self, new_option: str):
        """Handle mode change via callback"""
        self.wizard_mode = (new_option == "Wizard Mode")
        set_wizard_mode_preference(self.wizard_mode)
    
    def show_list_view(self):
        """Show list view, hide both editors"""
        self.single_editor.grid_remove()
        self.wizard_editor.grid_remove()
        self.list_view.grid()
        self.list_view.refresh()
    
    def show_editor_view(self, workflow_name: Optional[str]):
        """Show appropriate editor based on current mode"""
        self.list_view.grid_remove()
        
        if self.wizard_mode:
            self.single_editor.grid_remove()
            self.wizard_editor.grid()
            self.wizard_editor.load_workflow(workflow_name)
        else:
            self.wizard_editor.grid_remove()
            self.single_editor.grid()
            self.single_editor.load_workflow(workflow_name)
    
    def on_workflow_saved(self):
        """Handle workflow save - return to list"""
        self.show_list_view()
    
    def on_workflow_deleted(self, workflow_name: str):
        """Handle workflow deletion"""
        # List view already refreshed itself
        pass
    
    def execute_workflow(self, workflow_name: str):
        """Execute workflow - navigate to execution page"""
        if self.navigate_callback:
            self.navigate_callback("workflow_execution", workflow_name=workflow_name)