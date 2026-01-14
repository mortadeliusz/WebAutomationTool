"""
Action Editor Dialog - Dynamic form generation from action schemas
"""

import customtkinter as ctk
from typing import Dict, Optional, Callable
from async_tkinter_loop import async_handler
from src.core.action_handlers import (
    get_available_action_types, get_action_schema, get_field_definition,
    get_required_fields, get_optional_fields
)
from ui.components.fields.text_input import TextInputField
from ui.components.fields.dropdown import DropdownField
from ui.components.fields.selector_picker import SelectorPickerField


class ActionEditorDialog(ctk.CTkToplevel):
    def __init__(self, parent, action: Optional[Dict] = None, on_save: Callable[[Dict], None] = None):
        super().__init__(parent)
        self.action = action or {}
        self.on_save = on_save
        self.result = None
        self.field_components = {}
        
        self.setup_ui()
        self.populate_form()
        
        # Modal setup
        self.transient(parent)
        self.grab_set()
        self.focus()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.title("Edit Action")
        self.geometry("500x400")
        
        # Action type dropdown (always shown)
        self.action_type_field = DropdownField(self, "Action Type", get_available_action_types())
        self.action_type_field.pack(fill="x", padx=20, pady=10)
        self.action_type_field.combo.configure(command=self.on_action_type_changed)
        
        # Dynamic fields container
        self.fields_container = ctk.CTkScrollableFrame(self)
        self.fields_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side="right", padx=(5, 0))
        
        self.save_button = ctk.CTkButton(button_frame, text="Save", command=self.save)
        self.save_button.pack(side="right", padx=(0, 5))
    
    def on_action_type_changed(self, action_type: str):
        """Handle action type change - rebuild form fields"""
        self.rebuild_fields(action_type)
    
    def rebuild_fields(self, action_type: str):
        """Rebuild form fields based on action type"""
        # Clear existing fields
        for widget in self.fields_container.winfo_children():
            widget.destroy()
        self.field_components.clear()
        
        # Get required and optional fields for this action type
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
                # Connect picker callback to element picker
                component.set_picker_callback(self.on_element_picker_clicked)
            else:
                # Fallback to text input
                component = TextInputField(
                    self.fields_container,
                    field_def.get('label', field_name),
                    field_def.get('placeholder', ''),
                    is_optional
                )
            
            component.pack(fill="x", padx=10, pady=5)
            self.field_components[field_name] = component
    
    def populate_form(self):
        """Populate form with action data"""
        if self.action:
            # Set action type
            action_type = self.action.get('type', '')
            if action_type in get_available_action_types():
                self.action_type_field.set_value(action_type)
                self.rebuild_fields(action_type)
                
                # Populate field values
                for field_name, component in self.field_components.items():
                    value = self.action.get(field_name, '')
                    if value:
                        component.set_value(value)
        else:
            # New action - set default type and rebuild fields
            action_types = get_available_action_types()
            if action_types:
                self.action_type_field.set_value(action_types[0])
                self.rebuild_fields(action_types[0])
    
    def save(self):
        """Save the action"""
        # Collect form data
        action_data = {
            'type': self.action_type_field.get_value(),
            'browser_alias': 'main'  # Default for now
        }
        
        # Get values from field components
        for field_name, component in self.field_components.items():
            value = component.get_value()
            if value:  # Only include non-empty values
                action_data[field_name] = value
        
        if self.on_save:
            self.on_save(action_data)
        
        self.result = action_data
        self.destroy()
    
    def cancel(self):
        """Cancel editing"""
        self.result = None
        self.destroy()
    
    @async_handler
    async def on_element_picker_clicked(self, selector_field):
        """Handle element picker button click"""
        try:
            # Get browser controller
            from src.app_services import get_browser_controller
            browser_controller = get_browser_controller()
            
            # Get browser alias from form (default to 'main')
            browser_alias = 'main'
            
            # Get page from browser controller (don't force navigate)
            page = await browser_controller.get_page("chrome", browser_alias, "https://www.google.com", force_navigate=False)
            
            if not page:
                print(f"No active page for browser alias: {browser_alias}")
                return
            
            # Launch element picker
            from src.core.element_picker_toggle import ElementPicker
            picker = ElementPicker()
            result = await picker.pick_element(page)
            
            if result['success']:
                # Set the selected element in the field
                selector_field.set_picker_result(result['selector'])
            else:
                print(f"Element picker failed: {result['error']}")
                
        except Exception as e:
            print(f"Error launching element picker: {str(e)}")
