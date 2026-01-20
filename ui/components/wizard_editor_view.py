import customtkinter as ctk
from typing import Callable, Optional, Dict


class WizardEditorView(ctk.CTkFrame):
    """Placeholder wizard editor for testing view switching"""
    
    def __init__(self, parent, on_save: Callable[[], None], on_cancel: Callable[[], None]):
        super().__init__(parent)
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.current_workflow: Optional[Dict] = None
        self.setup_ui()
    
    def setup_ui(self):
        # Header with back button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        back_button = ctk.CTkButton(
            header_frame, text="← Back", width=80, command=self.on_cancel
        )
        back_button.pack(side="left")
        
        self.title_label = ctk.CTkLabel(
            header_frame, text="Wizard Mode", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=20)
        
        # Placeholder content
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        placeholder_label = ctk.CTkLabel(
            content_frame,
            text="🧙♂️ Wizard Editor Placeholder\n\nThis is where the step-by-step wizard will be implemented.\n\nCurrently testing view switching mechanism.",
            font=ctk.CTkFont(size=16), justify="center"
        )
        placeholder_label.pack(expand=True)
        
        self.workflow_name_label = ctk.CTkLabel(
            content_frame, text="No workflow loaded",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.workflow_name_label.pack(pady=20)
        
        # Save button (placeholder)
        save_button = ctk.CTkButton(
            self, text="Save Workflow (Placeholder)",
            command=self.save_workflow, height=40
        )
        save_button.pack(fill="x", padx=20, pady=(0, 20))
    
    def load_workflow(self, workflow_name: Optional[str]):
        if workflow_name:
            from src.utils.workflow_files import load_workflow
            self.current_workflow = load_workflow(workflow_name)
            self.title_label.configure(text=f"Wizard: {workflow_name}")
            self.workflow_name_label.configure(text=f"Editing: {workflow_name}")
        else:
            from src.utils.workflow_files import create_workflow
            self.current_workflow = create_workflow("New Workflow")
            self.title_label.configure(text="Wizard: New Workflow")
            self.workflow_name_label.configure(text="Creating: New Workflow")
    
    def save_workflow(self):
        print("Wizard save clicked - placeholder")
        self.on_save()