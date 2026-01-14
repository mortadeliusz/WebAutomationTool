"""
Action Executor - Execute individual browser actions (Async)
"""

import asyncio
from typing import Dict, Optional
from src.app_services import get_browser_controller
from src.core.action_handlers import get_action_handler

class ActionExecutor:
    """Execute individual browser actions using registry pattern"""
    
    def __init__(self):
        self.controller = get_browser_controller()
    
    async def execute_action(self, action: Dict) -> Dict[str, any]:
        """
        Execute a single action using registered handlers
        Returns: {'success': bool, 'error': str}
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
            
            # Resolve browser context
            browser_alias = action.get('browser_alias', 'main')
            page = self.controller.get_page(browser_alias)
            
            if not page:
                return {'success': False, 'error': f'No page for browser: {browser_alias}'}
            
            # Execute action
            return await handler(action, page)
            
        except Exception as e:
            return {'success': False, 'error': f'Action execution error: {str(e)}'}