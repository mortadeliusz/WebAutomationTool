"""
Actions List Component - Display and manage workflow actions with inline editing
"""

import customtkinter as ctk
from typing import Dict, List, Optional, Callable
from async_tkinter_loop import async_handler
from src.core.action_handlers import (
    get_available_action_types, get_field_definition,
    get_required_fields, get_optional_fields
)
from ui.components.fields.text_input import TextInputField
from ui.components.fields.dropdown import DropdownField
from ui.components.fields.selector_picker import SelectorPickerField


class ActionsList(ctk.CTkFrame):
    def __init__(self, parent, on_actions_changed: Callable[[List[Dict]], None]):
        super().__init__(parent)
        self.on_actions_changed = on_actions_changed
        self.actions: List[Dict] = []
        self.editing_action = False
        self.field_components = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the actions list UI"""
        # Header
        header = ctk.CTkLabel(self, text="Actions:", font=ctk.CTkFont(weight="bold"))
        header.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Actions display
        self.actions_frame = ctk.CTkScrollableFrame(self, height=150)
        self.actions_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add action button
        self.add_button = ctk.CTkButton(self, text="Add Action", command=self.start_add_action)
        self.add_button.pack(padx=10, pady=(0, 10))
    
    def set_actions(self, actions: List[Dict]):
        """Set the actions list"""
        self.actions = actions.copy()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the actions display"""
        # Clear existing display
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        
        # Display existing actions
        for i, action in enumerate(self.actions):
            action_frame = ctk.CTkFrame(self.actions_frame)
            action_frame.pack(fill="x", padx=5, pady=2)
            
            action_text = f"{i+1}. {action.get('type', 'Unknown')} - {action.get('description', 'No description')}"
            action_label = ctk.CTkLabel(action_frame, text=action_text)
            action_label.pack(side="left", padx=10, pady=5)
        
        # Show inline editor if editing
        if self.editing_action:
            self.show_inline_editor()
    
    def start_add_action(self):
        """Start adding a new action"""
        if self.editing_action:
            return  # Already editing
        
        self.editing_action = True
        self.add_button.configure(state="disabled")
        self.refresh_display()
    
    def show_inline_editor(self):
        """Show inline action editor"""
        # Editor container
        editor_frame = ctk.CTkFrame(self.actions_frame)
        editor_frame.pack(fill="x", padx=5, pady=5)
        
        # Editor title
        title = ctk.CTkLabel(editor_frame, text="New Action:", font=ctk.CTkFont(weight="bold"))
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Action type dropdown
        self.action_type_field = DropdownField(editor_frame, "Action Type", get_available_action_types())
        self.action_type_field.pack(fill="x", padx=10, pady=5)
        self.action_type_field.combo.configure(command=self.on_action_type_changed)
        
        # Dynamic fields container
        self.fields_container = ctk.CTkFrame(editor_frame)
        self.fields_container.pack(fill="x", padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(editor_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_edit)
        cancel_button.pack(side="right", padx=(5, 0))
        
        save_button = ctk.CTkButton(button_frame, text="Save", command=self.save_action)
        save_button.pack(side="right", padx=(0, 5))
        
        # Build initial fields
        action_types = get_available_action_types()
        if action_types:
            self.action_type_field.set_value(action_types[0])
            self.rebuild_fields(action_types[0])
    
    def on_action_type_changed(self, action_type: str):
        """Handle action type change"""
        self.rebuild_fields(action_type)
    
    def rebuild_fields(self, action_type: str):
        """Rebuild form fields based on action type"""
        # Clear existing fields
        for widget in self.fields_container.winfo_children():
            widget.destroy()
        self.field_components.clear()
        
        # Get required and optional fields
        required_fields = get_required_fields(action_type)
        optional_fields = get_optional_fields(action_type)
        
        # Create field components
        for field_name in required_fields + optional_fields:
            field_def = get_field_definition(field_name)
            if not field_def:
                continue
            
            component_type = field_def.get('component', 'text_input')
            is_optional = field_name in optional_fields
            
            # Create appropriate component
            if component_type == 'text_input':
                component = TextInputField(
                    self.fields_container,
                    field_def.get('label', field_name),
                    field_def.get('placeholder', ''),
                    is_optional
                )
            elif component_type == 'selector_picker':
                component = SelectorPickerField(
                    self.fields_container,
                    field_def.get('label', field_name),
                    field_def.get('placeholder', ''),
                    field_def.get('has_picker', True),
                    field_def.get('has_advanced', False)
                )
                # Connect picker callback
                component.set_picker_callback(self.on_element_picker_clicked)
            else:
                # Fallback to text input
                component = TextInputField(
                    self.fields_container,
                    field_def.get('label', field_name),
                    field_def.get('placeholder', ''),
                    is_optional
                )
            
            component.pack(fill="x", padx=5, pady=2)
            self.field_components[field_name] = component
    
    def save_action(self):
        """Save the new action"""
        # Collect form data
        action_data = {
            'type': self.action_type_field.get_value(),
            'browser_alias': 'main'
        }
        
        # Get values from field components
        for field_name, component in self.field_components.items():
            value = component.get_value()
            if value:
                action_data[field_name] = value
        
        # Add to actions list
        self.actions.append(action_data)
        
        # Notify parent
        self.on_actions_changed(self.actions)
        
        # Reset editing state
        self.editing_action = False
        self.add_button.configure(state="normal")
        self.refresh_display()
    
    def cancel_edit(self):
        """Cancel editing"""
        self.editing_action = False
        self.add_button.configure(state="normal")
        self.refresh_display()
    
    @async_handler
    async def on_element_picker_clicked(self, selector_field):
        """Handle element picker button click"""
        try:
            from src.app_services import get_browser_controller
            from src.core.element_picker_toggle import ElementPicker
            
            browser_controller = get_browser_controller()
            page = await browser_controller.get_page("chrome", "main", "https://www.google.com", force_navigate=False)
            
            if not page:
                print("No active page for element picker")
                return
            
            picker = ElementPicker()
            result = await picker.pick_element(page)
            
            if result['success']:
                selector_field.set_picker_result(result['selector'])
            else:
                print(f"Element picker failed: {result['error']}")
                
        except Exception as e:
            print(f"Error launching element picker: {str(e)}")