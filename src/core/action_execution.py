"""
Action Execution - Pure functions for executing actions
"""

from typing import Dict, Any
from src.app_services import get_browser_controller
from src.core.action_handlers import get_action_handler


async def execute_action(action: Dict, row_data: Dict = None) -> Dict[str, Any]:
    """
    Execute action
    
    Args:
        action: Action dictionary with type, selector, value, browser_alias, etc.
        row_data: Optional row data for template evaluation
    
    Returns:
        {'success': bool, 'error': str}
    """
    try:
        # Get action type
        action_type = action.get('type', '')
        if not action_type:
            return {'success': False, 'error': 'No action type specified'}
        
        # Get handler
        handler = get_action_handler(action_type)
        if not handler:
            return {'success': False, 'error': f'Unknown action type: {action_type}'}
        
        # Get browser alias from action
        browser_alias = action.get('browser_alias', 'main')
        
        # Get existing page (fail if not found)
        browser_controller = get_browser_controller()
        page = browser_controller.get_existing_page(browser_alias)
        
        if not page:
            return {'success': False, 'error': f'Browser not initialized: {browser_alias}'}
        
        # Execute action (handler decides what to resolve)
        return await handler(action, page, row_data)
        
    except Exception as e:
        return {'success': False, 'error': f'Action execution error: {str(e)}'}
