import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, List, Dict, Any
import os
import pandas as pd
from async_tkinter_loop import async_handler

from src.utils.workflow_files import list_workflows, load_workflow
from src.core.data_loader import DataLoader
from src.core.workflow_executor import WorkflowExecutor
from ui.components.data_table import DataTable
from src.utils.state_manager import get_last_selected_workflow, set_last_selected_workflow


class WorkflowExecutionPage(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback=None):
        super().__init__(parent)
        self.navigate_callback = navigate_callback
        self.current_data: Optional[pd.DataFrame] = None
        self.workflows = self.load_available_workflows()
        self.setup_ui()
    
    def load_available_workflows(self) -> List[str]:
        """Load available workflow names from user_data/workflows/"""
        try:
            workflows = list_workflows()
            return [w['name'] for w in workflows] if workflows else []
        except Exception:
            return []
    
    def refresh_workflows(self):
        """Refresh workflow list from disk"""
        self.workflows = self.load_available_workflows()
        self.workflow_combo.configure(
            values=self.workflows if self.workflows else ["No workflows found"],
            state="readonly" if self.workflows else "disabled"
        )
    
    def on_show(self):
        """Called when page becomes visible - refresh workflow list and load last selected"""
        self.refresh_workflows()
        
        # Load last selected workflow
        last_workflow = get_last_selected_workflow()
        if last_workflow and last_workflow in self.workflows:
            self.workflow_combo.set(last_workflow)
    
    def setup_ui(self):
        """Setup the workflow execution UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Workflow selection
        workflow_frame = ctk.CTkFrame(self)
        workflow_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        workflow_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(workflow_frame, text="Workflow:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.workflow_combo = ctk.CTkComboBox(
            workflow_frame, 
            values=self.workflows if self.workflows else ["No workflows found"],
            state="readonly" if self.workflows else "disabled",
            command=self.on_workflow_selected
        )
        self.workflow_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
        
        # File selection
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        file_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(file_frame, text="Data File:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.file_button = ctk.CTkButton(
            file_frame, 
            text="Select File...", 
            command=self.select_data_file
        )
        self.file_button.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=10)
        
        # Data preview
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(preview_frame, text="Data Preview:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Data table component
        self.data_table = DataTable(preview_frame, max_rows=10)
        self.data_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Execute button
        self.execute_button = ctk.CTkButton(
            self, 
            text="Execute Workflow", 
            command=self.execute_workflow,
            state="disabled"
        )
        self.execute_button.grid(row=3, column=0, padx=10, pady=5)
        
        # Results area
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(results_frame, text="Results:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        self.results_label = ctk.CTkLabel(results_frame, text="No execution yet")
        self.results_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))
        
        # Status
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.grid(row=5, column=0, sticky="w", padx=10, pady=(5, 10))
    
    def on_workflow_selected(self, workflow_name: str):
        """Handle workflow selection from dropdown"""
        if workflow_name and workflow_name != "No workflows found":
            set_last_selected_workflow(workflow_name)
    
    def select_data_file(self):
        """Open file dialog and load selected data file"""
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_data_file(file_path)
    
    def load_data_file(self, file_path: str):
        """Load data from file and display preview"""
        try:
            self.status_label.configure(text="Loading data...")
            
            loader = DataLoader()
            df = loader.load_from_file(file_path)
            
            # Store data and update table
            self.current_data = df
            self.data_table.set_data(df)
            
            # Enable execute button if we have data
            self.execute_button.configure(state="normal")
            
            filename = os.path.basename(file_path)
            self.status_label.configure(text=f"Loaded: {filename} ({len(df)} rows)")
                
        except Exception as e:
            self.status_label.configure(text=f"Error loading file: {str(e)}")
            self.data_table.clear()
            self.current_data = None
            self.execute_button.configure(state="disabled")
    
    @async_handler
    async def execute_workflow(self):
        """Execute the selected workflow with loaded data"""
        try:
            # Get selected workflow
            workflow_name = self.workflow_combo.get()
            if not workflow_name or workflow_name == "No workflows found":
                self.status_label.configure(text="No workflow selected")
                return
            
            # Load workflow definition
            workflow_def = load_workflow(workflow_name)
            if not workflow_def:
                self.status_label.configure(text="Failed to load workflow")
                return
            
            # Check if data is loaded
            if self.current_data is None:
                self.status_label.configure(text="No data loaded")
                return
            
            # Update UI state
            self.execute_button.configure(state="disabled")
            self.status_label.configure(text="Executing workflow...")
            self.results_label.configure(text="Execution in progress...")
            
            # Execute workflow
            executor = WorkflowExecutor()
            result = await executor.execute_workflow(workflow_def, self.current_data)
            
            # Display results
            if result['success']:
                results_text = f"Completed: {result['successful_rows']}/{result['total_rows']} rows successful"
                if result['failed_rows'] > 0:
                    results_text += f", {result['failed_rows']} failed"
                self.results_label.configure(text=results_text)
                self.status_label.configure(text="Workflow execution completed")
            else:
                self.results_label.configure(text=f"Execution failed: {result.get('error', 'Unknown error')}")
                self.status_label.configure(text="Workflow execution failed")
            
        except Exception as e:
            self.results_label.configure(text=f"Error: {str(e)}")
            self.status_label.configure(text="Execution error")
        
        finally:
            # Re-enable execute button
            self.execute_button.configure(state="normal")


# Backward compatibility alias
class TaskExecutionPage(WorkflowExecutionPage):
    """Alias for backward compatibility with old page name"""
    pass