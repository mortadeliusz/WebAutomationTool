"""
Action Handlers - Registry-based action execution system
"""

import asyncio
from typing import Dict, Callable, Any
from playwright.async_api import Page
from src.core.template_processing import resolve_expression


async def handle_click(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle click action on page element"""
    selector = action.get('selector', '')
    if not selector:
        return {'success': False, 'error': 'No selector specified for click action'}
    
    # Resolve template expression if row_data provided
    if row_data:
        selector = resolve_expression(selector, row_data)
    
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
    
    # Resolve template expressions if row_data provided
    if row_data:
        selector = resolve_expression(selector, row_data)
        value = resolve_expression(value, row_data)
    
    try:
        await page.fill(selector, value, timeout=5000)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Fill field error: {str(e)}'}


async def handle_navigate(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle navigate action"""
    url = action.get('url', '')
    if not url:
        return {'success': False, 'error': 'No URL specified'}
    
    # Resolve template expression if row_data provided
    if row_data:
        url = resolve_expression(url, row_data)
    
    try:
        await page.goto(url, timeout=30000)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Navigation error: {str(e)}'}


async def handle_type_text(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle type text action (character-by-character)"""
    selector = action.get('selector', '')
    value = action.get('value', '')
    
    if not selector:
        return {'success': False, 'error': 'No selector specified'}
    
    # Resolve template expressions if row_data provided
    if row_data:
        selector = resolve_expression(selector, row_data)
        value = resolve_expression(value, row_data)
    
    try:
        await page.type(selector, value, delay=50)  # 50ms delay between keystrokes
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Type text error: {str(e)}'}


async def handle_press_key(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle press key action"""
    key = action.get('key', '')
    if not key:
        return {'success': False, 'error': 'No key specified'}
    
    # Map tkinter keysym to Playwright key names
    KEY_MAP = {
        'Return': 'Enter',
        'space': 'Space',
        'BackSpace': 'Backspace',
    }
    
    playwright_key = KEY_MAP.get(key, key)
    
    try:
        await page.keyboard.press(playwright_key)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Press key error: {str(e)}'}


async def handle_wait_for_element(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle wait for element action"""
    selector = action.get('selector', '')
    timeout = int(action.get('timeout', 30000))
    
    if not selector:
        return {'success': False, 'error': 'No selector specified'}
    
    # Resolve template expression if row_data provided
    if row_data:
        selector = resolve_expression(selector, row_data)
    
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Element not found: {str(e)}'}


async def handle_wait_seconds(action: Dict, page: Page, row_data: Dict = None) -> Dict[str, Any]:
    """Handle wait seconds action"""
    seconds = float(action.get('seconds', 1))
    
    try:
        await asyncio.sleep(seconds)
        return {'success': True, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Wait error: {str(e)}'}


# Action handler registry
ACTION_HANDLERS: Dict[str, Callable] = {
    'click': handle_click,
    'fill_field': handle_fill_field,
    'navigate': handle_navigate,
    'type_text': handle_type_text,
    'press_key': handle_press_key,
    'wait_for_element': handle_wait_for_element,
    'wait_seconds': handle_wait_seconds,
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
        'component': 'action_value_input',
        'label': 'Value',
        'placeholder': '{{col("Email")}}'
    },
    'url': {
        'component': 'text_input',
        'label': 'URL',
        'placeholder': 'https://example.com or {{col("url")}}'
    },
    'key': {
        'component': 'key_picker',
        'label': 'Key',
        'placeholder': 'Click 🎹 then press key'
    },
    'timeout': {
        'component': 'number_input',
        'label': 'Timeout (ms)',
        'placeholder': '30000'
    },
    'seconds': {
        'component': 'number_input',
        'label': 'Seconds',
        'placeholder': '1'
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
    },
    'navigate': {
        'required': ['url'],
        'optional': ['description']
    },
    'type_text': {
        'required': ['selector', 'value'],
        'optional': ['description']
    },
    'press_key': {
        'required': ['key'],
        'optional': ['description']
    },
    'wait_for_element': {
        'required': ['selector'],
        'optional': ['timeout', 'description']
    },
    'wait_seconds': {
        'required': ['seconds'],
        'optional': ['description']
    }
}

# Action metadata - descriptions, categories, sorting
ACTION_METADATA = {
    'click': {
        'name': 'Click',
        'description': 'Click element',
        'category': 'common',
        'sort_order': 1
    },
    'fill_field': {
        'name': 'Fill Field',
        'description': 'Instantly fill input (fast, works with all frameworks)',
        'use_when': 'Standard forms, text fields, email fields',
        'category': 'common',
        'sort_order': 2
    },
    'navigate': {
        'name': 'Navigate',
        'description': 'Go to URL',
        'category': 'common'
    },
    'type_text': {
        'name': 'Type Text',
        'description': 'Type character-by-character with delay (human-like)',
        'use_when': 'Autocomplete fields, search suggestions, bot detection avoidance',
        'category': 'common'
    },
    'press_key': {
        'name': 'Press Key',
        'description': 'Press keyboard key (Enter, Tab, Escape, etc.)',
        'use_when': 'Submit forms, navigate fields, trigger shortcuts',
        'category': 'common'
    },
    'wait_for_element': {
        'name': 'Wait for Element',
        'description': 'Wait for element to appear',
        'use_when': 'Dynamic content, AJAX loading',
        'category': 'utility',
        'warning': 'Only use for dynamic content. Playwright auto-waits for most actions.'
    },
    'wait_seconds': {
        'name': 'Wait (Seconds)',
        'description': 'Wait fixed time',
        'use_when': 'Rate limiting, slow APIs',
        'category': 'utility',
        'warning': '⚠️ Last resort only. Try wait_for_element first.'
    }
}


def get_available_action_types() -> list[str]:
    """Get list of available action types"""
    return list(ACTION_HANDLERS.keys())


def get_actions_by_category(category: str) -> list[str]:
    """
    Get action types by category, sorted:
    1. Actions with sort_order (ascending)
    2. Actions without sort_order (alphabetical)
    """
    actions_with_order = []
    actions_without_order = []
    
    for action_type, metadata in ACTION_METADATA.items():
        if metadata.get('category') != category:
            continue
        
        sort_order = metadata.get('sort_order')
        if sort_order is not None:
            actions_with_order.append((action_type, sort_order))
        else:
            actions_without_order.append(action_type)
    
    # Sort each group
    sorted_with_order = [action for action, _ in sorted(actions_with_order, key=lambda x: x[1])]
    sorted_without_order = sorted(actions_without_order)
    
    return sorted_with_order + sorted_without_order


def get_action_metadata(action_type: str) -> dict:
    """Get metadata for specific action type"""
    return ACTION_METADATA.get(action_type, {})


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