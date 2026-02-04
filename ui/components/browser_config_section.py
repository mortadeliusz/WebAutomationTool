"""
Browser Configuration Section - Container for browser instances
"""

import customtkinter as ctk
from typing import Dict, Callable
from tkinter import messagebox
from async_tkinter_loop import async_handler
from ui.components.accordion import Accordion
from ui.components.browser_instance import BrowserInstance
from src.utils.browser_validation import BrowserValidator
from src.app_services import get_browser_controller


class BrowserConfigSection(ctk.CTkFrame):
    """Container for browser instance(s)"""
    
    def __init__(self, parent, get_workflow: Callable, on_workflow_changed: Callable):
        super().__init__(parent, fg_color="transparent")
        self.get_workflow = get_workflow
        self.on_workflow_changed = on_workflow_changed
        self.instances = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the browser configuration UI"""
        # Accordion for collapsible section
        self.accordion = Accordion(self, title="Browser Configuration", expanded=True)
        self.accordion.pack(fill="x", padx=5, pady=5)
        
        # Create instances based on workflow
        self.refresh_instances()
    
    def refresh_instances(self):
        """Rebuild instances when workflow browsers change"""
        # Clear existing
        for widget in self.accordion.content_frame.winfo_children():
            widget.destroy()
        
        workflow = self.get_workflow()
        if not workflow:
            return  # No workflow loaded yet
        
        browsers = workflow.get('browsers', {})
        show_alias = len(browsers) > 1
        show_delete = len(browsers) > 1
        
        # Create instances
        self.instances = {}
        for alias, config in browsers.items():
            instance = BrowserInstance(
                self.accordion.content_frame,
                alias=alias,
                show_alias=show_alias,
                show_delete=show_delete,
                on_save=self.save_config,
                on_delete=self.delete_browser,
                on_rename=self.rename_browser
            )
            instance.set_config(config)
            instance.pack(fill="x", padx=5, pady=5)
            self.instances[alias] = instance
        
        # TEMPORARY: Add Browser button (recreated after refresh)
        add_btn = ctk.CTkButton(
            self.accordion.content_frame,
            text="+ Add Browser",
            command=self.add_browser,
            fg_color="#2b8a3e",
            hover_color="#2f9e44"
        )
        add_btn.pack(fill="x", padx=5, pady=5)
    
    def save_config(self, alias: str, config: Dict):
        """Save browser configuration"""
        workflow = self.get_workflow()
        if not workflow:
            return
        
        # Validate
        is_valid, error = BrowserValidator.validate_config(
            alias,
            config,
            workflow['browsers'],
            old_alias=alias
        )
        
        if not is_valid:
            messagebox.showerror("Validation Error", error)
            return
        
        # Update config
        workflow['browsers'][alias] = config
        
        # Save
        from src.utils.workflow_files import save_workflow
        if not save_workflow(workflow):
            messagebox.showerror("Save Failed", "Could not save workflow.")
            return
        
        # Notify parent
        self.on_workflow_changed()
    
    def rename_browser(self, old_alias: str):
        """Open rename dialog for browser"""
        from ui.components.rename_dialog import RenameDialog
        
        dialog = RenameDialog(
            parent=self.winfo_toplevel(),
            current_alias=old_alias,
            on_save=lambda new_alias: self._do_rename(old_alias, new_alias)
        )
    
    def _do_rename(self, old_alias: str, new_alias: str):
        """Execute browser rename with validation and save-first pattern"""
        workflow = self.get_workflow()
        if not workflow:
            return
        
        # Validate
        is_valid, error = BrowserValidator.validate_config(
            new_alias,
            workflow['browsers'][old_alias],
            workflow['browsers'],
            old_alias=old_alias
        )
        
        if not is_valid:
            messagebox.showerror("Validation Error", error)
            return
        
        # Store original state for rollback
        original_browser = workflow['browsers'][old_alias].copy()
        original_actions = [a.copy() for a in workflow.get('actions', [])]
        
        # Update workflow (in-memory)
        workflow['browsers'][new_alias] = workflow['browsers'].pop(old_alias)
        
        # Cascade to actions
        for action in workflow['actions']:
            if action.get('browser_alias') == old_alias:
                action['browser_alias'] = new_alias
        
        # SAVE FIRST
        from src.utils.workflow_files import save_workflow
        if not save_workflow(workflow):
            # Rollback
            workflow['browsers'][old_alias] = original_browser
            if new_alias in workflow['browsers']:
                del workflow['browsers'][new_alias]
            workflow['actions'] = original_actions
            messagebox.showerror("Save Failed", "Could not save workflow. Rename cancelled.")
            return
        
        # Update runtime
        browser_controller = get_browser_controller()
        browser_controller.rename_browser_alias(old_alias, new_alias)
        
        # Notify parent and refresh
        self.on_workflow_changed()
        self.refresh_instances()
    
    @async_handler
    async def delete_browser(self, alias: str):
        """Delete browser with confirmation and save-first pattern"""
        workflow = self.get_workflow()
        if not workflow:
            return
        
        # Validate not last browser
        if len(workflow['browsers']) == 1:
            messagebox.showerror(
                "Cannot Delete",
                "Workflow must have at least one browser."
            )
            return
        
        # Count actions using this browser
        action_count = sum(
            1 for action in workflow.get('actions', [])
            if action.get('browser_alias') == alias
        )
        
        # Confirm deletion
        if action_count > 0:
            response = messagebox.askyesno(
                "Delete Browser",
                f"{action_count} action(s) use this browser.\n\n"
                f"If you proceed, they will be deleted.\n\n"
                f"Continue?",
                icon='warning'
            )
            if not response:
                return
        
        # Store original state for rollback
        original_browser = workflow['browsers'][alias].copy()
        original_actions = [a.copy() for a in workflow.get('actions', [])]
        
        # Update workflow (in-memory)
        del workflow['browsers'][alias]
        workflow['actions'] = [
            action for action in workflow['actions']
            if action.get('browser_alias') != alias
        ]
        
        # SAVE FIRST (before closing browser)
        from src.utils.workflow_files import save_workflow
        if not save_workflow(workflow):
            # Rollback on save failure
            workflow['browsers'][alias] = original_browser
            workflow['actions'] = original_actions
            messagebox.showerror(
                "Save Failed",
                "Could not save workflow. Deletion cancelled."
            )
            return
        
        # NOW close browser (after successful save)
        browser_controller = get_browser_controller()
        if browser_controller.is_browser_running(alias):
            await browser_controller.close_browser_page(alias)
        
        # Notify parent
        self.on_workflow_changed()
        
        # Refresh UI
        self.refresh_instances()
    
    def add_browser(self):
        """TEMPORARY: Add new browser for testing"""
        workflow = self.get_workflow()
        if not workflow:
            return
        
        # Generate unique alias
        existing_aliases = set(workflow['browsers'].keys())
        counter = 2
        while f"browser{counter}" in existing_aliases:
            counter += 1
        new_alias = f"browser{counter}"
        
        # Add new browser with default config
        workflow['browsers'][new_alias] = {
            'browser_type': 'chrome',
            'starting_url': ''
        }
        
        # Save
        from src.utils.workflow_files import save_workflow
        if not save_workflow(workflow):
            messagebox.showerror("Save Failed", "Could not save workflow.")
            return
        
        # Notify parent and refresh
        self.on_workflow_changed()
        self.refresh_instances()
