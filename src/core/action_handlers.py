"""
Action Handlers - Registry-based action execution system
"""

from typing import Dict, Callable, Any
from playwright.async_api import Page
from src.core.template_processing import resolve_expression


async def handle_click(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle click action on page element"""
    selector = action.get('selector', '')
    if not selector:
        return {'success': False, 'error': 'No selector specified for click action'}
    
    try:
        await page.click(selector, timeout=5000)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Click error: {str(e)}'}


async def handle_fill_field(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle fill field action on page element"""
    selector = action.get('selector', '')
    value = action.get('value', '')
    
    if not selector:
        return {'success': False, 'error': 'No selector specified for fill_field action'}
    
    # Resolve template expression if row_data provided
    if row_data:
        value = resolve_expression(value, row_data)
    
    try:
        await page.fill(selector, value, timeout=5000)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Fill field error: {str(e)}'}


# Action handler registry
ACTION_HANDLERS: Dict[str, Callable] = {
    'click': handle_click,
    'fill_field': handle_fill_field,
}


def get_action_handler(action_type: str) -> Callable:
    """Get handler function for action type"""
    return ACTION_HANDLERS.get(action_type)


def register_action_handler(action_type: str, handler: Callable) -> None:
    """Register new action handler"""
    ACTION_HANDLERS[action_type] = handler


# Field component definitions
FIELD_DEFINITIONS = {
    'action_type': {
        'component': 'dropdown',
        'label': 'Action Type',
        'values_source': 'registry'
    },
    'selector': {
        'component': 'selector_picker',
        'label': 'Element Selector',
        'placeholder': '//input[@name="example"]',
        'has_picker': True,
        'has_advanced': True
    },
    'value': {
        'component': 'text_input',
        'label': 'Value',
        'placeholder': '{{col("Email")}}'
    },
    'description': {
        'component': 'text_input',
        'label': 'Description',
        'placeholder': 'Action description',
        'optional': True
    }
}

# Action schemas - define which fields each action type needs
ACTION_SCHEMAS = {
    'click': {
        'required': ['selector'],
        'optional': ['description']
    },
    'fill_field': {
        'required': ['selector', 'value'],
        'optional': ['description']
    }
}


def get_available_action_types() -> list[str]:
    """Get list of available action types"""
    return list(ACTION_HANDLERS.keys())


def get_action_schema(action_type: str) -> dict:
    """Get schema for specific action type"""
    return ACTION_SCHEMAS.get(action_type, {})


def get_field_definition(field_name: str) -> dict:
    """Get field definition for UI component generation"""
    return FIELD_DEFINITIONS.get(field_name, {})


def get_required_fields(action_type: str) -> list[str]:
    """Get required fields for action type"""
    schema = get_action_schema(action_type)
    return schema.get('required', [])


def get_optional_fields(action_type: str) -> list[str]:
    """Get optional fields for action type"""
    schema = get_action_schema(action_type)
    return schema.get('optional', [])