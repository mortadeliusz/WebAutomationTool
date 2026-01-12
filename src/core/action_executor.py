"""
Action Executor - Execute individual browser actions (Async)
"""

import asyncio
from typing import Dict, Optional
from src.core.browser_controller import BrowserController

class ActionExecutor:
    """Execute individual browser actions using injected BrowserController"""
    
    def __init__(self, browser_controller: BrowserController):
        self.controller = browser_controller
    
    async def execute_action(self, action: Dict) -> Dict[str, any]:
        """
        Execute a single action
        Returns: {'success': bool, 'error': str}
        """
        try:
            action_type = action.get('type', '')
            
            if action_type == 'navigate':
                return await self._execute_navigate(action)
            elif action_type == 'click':
                return await self._execute_click(action)
            elif action_type == 'set_value':
                return await self._execute_set_value(action)
            elif action_type == 'wait':
                return await self._execute_wait(action)
            else:
                return {
                    'success': False, 
                    'error': f'Unknown action type: {action_type}'
                }
            
        except Exception as e:
            return {
                'success': False, 
                'error': f'Action execution error: {str(e)}'
            }
    
    async def _execute_navigate(self, action: Dict) -> Dict[str, any]:
        """Execute navigate action"""
        url = action.get('url', '')
        if not url:
            return {
                'success': False, 
                'error': 'No URL specified for navigate action'
            }
        
        result = await self.controller.navigate(url)
        if result['success']:
            await asyncio.sleep(1)  # Wait for navigation
        
        return result
    
    async def _execute_click(self, action: Dict) -> Dict[str, any]:
        """Execute click action"""
        selector = action.get('selector', '')
        if not selector:
            return {
                'success': False, 
                'error': 'No selector specified for click action'
            }
        
        page = self.controller.get_page()
        if not page:
            return {
                'success': False, 
                'error': 'No active browser page'
            }
        
        try:
            await page.click(selector, timeout=5000)
            await asyncio.sleep(0.5)  # Brief pause after click
            return {'success': True, 'error': None}
        except Exception as e:
            return {
                'success': False, 
                'error': f'Click error: {str(e)}'
            }
    
    async def _execute_set_value(self, action: Dict) -> Dict[str, any]:
        """Execute set value action"""
        selector = action.get('selector', '')
        value = action.get('value', '')
        
        if not selector:
            return {
                'success': False, 
                'error': 'No selector specified for set_value action'
            }
        
        page = self.controller.get_page()
        if not page:
            return {
                'success': False, 
                'error': 'No active browser page'
            }
        
        try:
            await page.fill(selector, value, timeout=5000)
            await asyncio.sleep(0.5)  # Brief pause after input
            return {'success': True, 'error': None}
        except Exception as e:
            return {
                'success': False, 
                'error': f'Set value error: {str(e)}'
            }
    
    async def _execute_wait(self, action: Dict) -> Dict[str, any]:
        """Execute wait action"""
        try:
            duration = action.get('duration', 1)
            await asyncio.sleep(duration)
            return {'success': True, 'error': None}
        except Exception as e:
            return {
                'success': False, 
                'error': f'Wait error: {str(e)}'
            }