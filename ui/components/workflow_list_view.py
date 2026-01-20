"""
Workflow List View - Display workflows with edit/delete actions
"""

import customtkinter as ctk
from typing import Callable, Optional
from src.utils.workflow_files import list_workflows, delete_workflow


class WorkflowListView(ctk.CTkFrame):
    def __init__(
        self, 
        parent, 
        on_edit: Callable[[str], None],
        on_new: Callable[[], None],
        on_delete: Callable[[str], None],
        on_execute: Optional[Callable[[str], None]] = None
    ):
        super().__init__(parent)
        self.on_edit = on_edit
        self.on_new = on_new
        self.on_delete = on_delete
        self.on_execute = on_execute
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup the list view UI"""
        # Header
        header = ctk.CTkLabel(
            self, 
            text="Workflows", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Scrollable workflow list
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # New workflow button
        new_button = ctk.CTkButton(
            self, 
            text="+ New Workflow", 
            command=self.on_new,
            height=40
        )
        new_button.pack(padx=20, pady=(0, 20), fill="x")
    
    def refresh(self):
        """Refresh workflow list from disk"""
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        workflows = list_workflows()
        
        if not workflows:
            empty_label = ctk.CTkLabel(
                self.list_frame, 
                text="No workflows yet\nClick 'New Workflow' to create one",
                text_color="gray"
            )
            empty_label.pack(pady=40)
            return
        
        # Display workflow cards
        for workflow in workflows:
            self.create_workflow_card(workflow)
    
    def create_workflow_card(self, workflow: dict):
        """Create a clickable workflow card with separate delete button"""
        # Row container for card + delete button
        row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=5)
        
        # Clickable card (left side, expands)
        card = ctk.CTkFrame(row)
        card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Make card clickable
        workflow_name = workflow['name']
        card.bind("<Button-1>", lambda e: self.on_edit(workflow_name))
        card.configure(cursor="hand2")
        
        # Hover effect
        card.bind("<Enter>", lambda e: card.configure(border_width=2, border_color="#1f538d"))
        card.bind("<Leave>", lambda e: card.configure(border_width=0))
        
        # Workflow info inside card
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind click to info frame too
        info_frame.bind("<Button-1>", lambda e: self.on_edit(workflow_name))
        
        name_label = ctk.CTkLabel(
            info_frame, 
            text=workflow['name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e: self.on_edit(workflow_name))
        
        details = f"{workflow['actions_count']} actions"
        if workflow['browsers']:
            details += f" • {workflow['browsers']}"
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=details,
            text_color="gray",
            anchor="w"
        )
        details_label.pack(anchor="w")
        details_label.bind("<Button-1>", lambda e: self.on_edit(workflow_name))
        
        # Button container (right side)
        button_container = ctk.CTkFrame(row, fg_color="transparent")
        button_container.pack(side="right")
        
        # Execute button (if callback provided)
        if self.on_execute:
            execute_button = ctk.CTkButton(
                button_container,
                text="▶️",
                width=40,
                command=lambda: self.on_execute(workflow['name'])
            )
            execute_button.pack(side="right", padx=(0, 5))
        
        # Delete button
        delete_button = ctk.CTkButton(
            button_container,
            text="🗑️",
            width=40,
            fg_color="darkred",
            hover_color="red",
            command=lambda: self.delete_workflow(workflow['name'])
        )
        delete_button.pack(side="right")
    
    def delete_workflow(self, workflow_name: str):
        """Delete workflow with confirmation"""
        # TODO: Add confirmation dialog
        if delete_workflow(workflow_name):
            self.on_delete(workflow_name)
            self.refresh()
