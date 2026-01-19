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
    def __init__(self, parent, on_actions_changed: Callable[[List[Dict]], None], on_load_data: Callable = None):
        super().__init__(parent)
        self.on_actions_changed = on_actions_changed
        self.on_load_data = on_load_data
        self.actions: List[Dict] = []
        self.editing_action = False
        self.editing_index: Optional[int] = None  # None = new action, int = editing existing
        self.field_components = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the actions list UI"""
        # Header
        header = ctk.CTkLabel(self, text="Actions:", font=ctk.CTkFont(weight="bold"))
        header.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Actions display with fixed height
        self.actions_frame = ctk.CTkScrollableFrame(self, height=300)
        self.actions_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add action button
        self.add_button = ctk.CTkButton(self, text="Add Action", command=self.start_add_action)
        self.add_button.pack(padx=10, pady=(0, 10))
    
    def set_actions(self, actions: List[Dict]):
        """Set the actions list"""
        self.actions = actions.copy()
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the actions display with in-place editing"""
        # Clear existing display
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        
        # Display actions or editor
        for i, action in enumerate(self.actions):
            if self.editing_index == i:
                # Replace card with editor
                self.create_inline_editor_at(i)
            else:
                # Show normal action card
                self.create_action_card(i, action)
        
        # If adding new action, show editor at bottom
        if self.editing_action and self.editing_index is None:
            self.create_inline_editor_at(None)
        
        # CRITICAL: Force scroll region update to prevent sync issues
        self.after(50, self._force_scroll_update)
    
    def _force_scroll_update(self):
        """Force scroll region update to prevent scrollbar sync issues"""
        try:
            canvas = self.actions_frame._parent_canvas
            canvas.configure(scrollregion=canvas.bbox("all"))
        except:
            pass
    
    def create_action_card(self, index: int, action: Dict):
        """Create a clickable action card with delete button"""
        # Row container for action card + delete button
        row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)
        
        # Clickable action card (left side, expands)
        action_card = ctk.CTkFrame(row)
        action_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Make card clickable
        action_card.bind("<Button-1>", lambda e: self.start_edit_action(index))
        action_card.configure(cursor="hand2")
        
        # Hover effect
        action_card.bind("<Enter>", lambda e: action_card.configure(border_width=2, border_color="#1f538d"))
        action_card.bind("<Leave>", lambda e: action_card.configure(border_width=0))
        
        action_text = f"{index+1}. {action.get('type', 'Unknown')} - {action.get('description', 'No description')}"
        action_label = ctk.CTkLabel(action_card, text=action_text)
        action_label.pack(side="left", padx=10, pady=5)
        action_label.bind("<Button-1>", lambda e: self.start_edit_action(index))
        
        # Delete button (right side, fixed width)
        delete_button = ctk.CTkButton(
            row,
            text="🗑️",
            width=40,
            fg_color="darkred",
            hover_color="red",
            command=lambda: self.delete_action(index)
        )
        delete_button.pack(side="right")
    
    def start_add_action(self):
        """Start adding a new action"""
        if self.editing_action:
            return  # Already editing
        
        self.editing_action = True
        self.editing_index = None  # None means new action
        self.add_button.configure(state="disabled")
        self.refresh_display()
    
    def start_edit_action(self, index: int):
        """Start editing an existing action"""
        # Auto-close any existing editor
        if self.editing_action:
            self.cancel_edit()
        
        self.editing_action = True
        self.editing_index = index
        self.add_button.configure(state="disabled")
        self.refresh_display()
    
    def delete_action(self, index: int):
        """Delete an action"""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
            self.on_actions_changed(self.actions)
            self.refresh_display()
    
    def create_inline_editor_at(self, index: Optional[int]):
        """Create inline editor at specified position (replaces card or appends)"""
        # Row container for editor + delete button
        row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)
        
        # Editor container (left side, expands)
        editor_frame = ctk.CTkFrame(row)
        editor_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Editor title
        title_text = f"Edit Action {index+1}:" if index is not None else "New Action:"
        title = ctk.CTkLabel(editor_frame, text=title_text, font=ctk.CTkFont(weight="bold"))
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
        
        # Delete button (right side, fixed width) - only for existing actions
        if index is not None:
            delete_button = ctk.CTkButton(
                row,
                text="🗑️",
                width=40,
                fg_color="darkred",
                hover_color="red",
                command=lambda: self.delete_action(index)
            )
            delete_button.pack(side="right")
        else:
            # Spacer for alignment with other rows
            spacer = ctk.CTkFrame(row, width=40, fg_color="transparent")
            spacer.pack(side="right")
        
        # Load existing action data if editing
        if index is not None and 0 <= index < len(self.actions):
            existing_action = self.actions[index]
            action_type = existing_action.get('type', '')
            if action_type:
                self.action_type_field.set_value(action_type)
                self.rebuild_fields(action_type)
                # Populate field values
                for field_name, component in self.field_components.items():
                    if field_name in existing_action:
                        component.set_value(existing_action[field_name])
        else:
            # Build initial fields for new action
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
            elif component_type == 'action_value_input':
                from ui.components.fields.action_value_input import ActionValueInput
                component = ActionValueInput(
                    self.fields_container,
                    field_def.get('label', field_name),
                    field_def.get('placeholder', ''),
                    is_optional,
                    on_load_data=self.on_load_data
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
        """Save the action (new or edited)"""
        # Collect form data
        action_data = {
            'type': self.action_type_field.get_value(),
            'browser_alias': 'main'  # Default to 'main' for single browser
        }
        
        # Get values from field components
        for field_name, component in self.field_components.items():
            value = component.get_value()
            if value:
                action_data[field_name] = value
        
        # Update existing or add new
        if self.editing_index is not None and 0 <= self.editing_index < len(self.actions):
            # Update existing action
            self.actions[self.editing_index] = action_data
        else:
            # Add new action
            self.actions.append(action_data)
        
        # Notify parent
        self.on_actions_changed(self.actions)
        
        # Reset editing state
        self.editing_action = False
        self.editing_index = None
        self.add_button.configure(state="normal")
        self.refresh_display()
    
    def cancel_edit(self):
        """Cancel editing"""
        self.editing_action = False
        self.editing_index = None
        self.add_button.configure(state="normal")
        self.refresh_display()
    
    def refresh_all_helpers(self):
        """Refresh data sample in all helper-enabled fields"""
        for component in self.field_components.values():
            if hasattr(component, 'refresh_data_sample'):
                component.refresh_data_sample()
    
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