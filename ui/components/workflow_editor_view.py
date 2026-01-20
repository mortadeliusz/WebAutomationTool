"""
Workflow Editor View - Full-screen workflow editing interface
"""

import customtkinter as ctk
from typing import Dict, Optional, Callable, List
from src.utils.workflow_files import save_workflow, create_workflow
from ui.components.browser_config_section import BrowserConfigSection
from ui.components.actions_list import ActionsList


class WorkflowEditorView(ctk.CTkFrame):
    def __init__(
        self, 
        parent,
        on_save: Callable[[], None],
        on_cancel: Callable[[], None]
    ):
        super().__init__(parent)
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.current_workflow: Optional[Dict] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the editor view UI"""
        # Header with back button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        back_button = ctk.CTkButton(
            header_frame,
            text="← Back",
            width=80,
            command=self.on_cancel
        )
        back_button.pack(side="left")
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Edit Workflow",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=20)
        
        # Data sample status indicator
        from ui.components.data_sample_status import DataSampleStatus
        self.data_status = DataSampleStatus(
            header_frame,
            on_load=self.load_data_sample,
            on_change=self.on_data_changed
        )
        self.data_status.pack(side="right")
        
        # Scrollable content
        content = ctk.CTkScrollableFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Workflow name
        name_label = ctk.CTkLabel(
            content,
            text="Workflow Name:",
            font=ctk.CTkFont(weight="bold")
        )
        name_label.pack(anchor="w", pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(
            content,
            placeholder_text="Enter workflow name"
        )
        self.name_entry.pack(fill="x", pady=(0, 20))
        
        # Browser configuration
        self.browser_config = BrowserConfigSection(content)
        self.browser_config.pack(fill="x", pady=(0, 20))
        
        # Actions section
        self.actions_list = ActionsList(content, self.on_actions_changed, on_load_data=self.load_data_sample)
        self.actions_list.pack(fill="both", expand=True, pady=(0, 20))
        
        # Save button
        save_button = ctk.CTkButton(
            self,
            text="Save Workflow",
            command=self.save_workflow,
            height=40
        )
        save_button.pack(fill="x", padx=20, pady=(0, 20))
    
    def load_workflow(self, workflow_name: Optional[str]):
        """Load workflow for editing or create new"""
        if workflow_name:
            from src.utils.workflow_files import load_workflow
            self.current_workflow = load_workflow(workflow_name)
            self.title_label.configure(text=f"Edit: {workflow_name}")
        else:
            self.current_workflow = create_workflow("New Workflow")
            self.title_label.configure(text="New Workflow")
        
        if self.current_workflow:
            # Populate form
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, self.current_workflow.get('name', ''))
            
            # Load browser config
            browser_config = self.current_workflow.get('browsers', {}).get('main', {})
            self.browser_config.set_config(browser_config)
            
            # Load actions
            actions = self.current_workflow.get('actions', [])
            self.actions_list.set_actions(actions)
    
    def save_workflow(self):
        """Save the current workflow"""
        if not self.current_workflow:
            return
        
        # Update workflow data
        self.current_workflow['name'] = self.name_entry.get() or "Unnamed Workflow"
        self.current_workflow['browsers']['main'] = self.browser_config.get_config()
        
        if save_workflow(self.current_workflow):
            from src.app_services import clear_workflow_data_sample
            clear_workflow_data_sample()
            self.on_save()
    
    def on_actions_changed(self, actions: List[Dict]):
        """Handle actions list changes and save to disk"""
        if self.current_workflow:
            self.current_workflow['actions'] = actions
            # Auto-save workflow when actions change
            save_workflow(self.current_workflow)
    
    def load_data_sample(self):
        """Load data sample for expression helper"""
        from tkinter import filedialog
        from src.core.data_loader import DataLoader
        from src.app_services import set_workflow_data_sample
        
        file_path = filedialog.askopenfilename(
            title="Select Data Sample",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                loader = DataLoader()
                df = loader.load_from_file(file_path)
                set_workflow_data_sample(df.head(10))
                self.on_data_changed()
            except Exception as e:
                print(f"Error loading data sample: {e}")
    
    def on_data_changed(self):
        """Called when data sample changes"""
        self.data_status.refresh()
        self.actions_list.refresh_all_helpers()
