"""
Action Executor - Execute basic actions for dataless tasks
"""

import time
from typing import Dict, List
from core.browser_controller import BrowserController

class ActionExecutor:
    """Execute basic actions for dataless tasks"""
    
    def __init__(self):
        self.controller = BrowserController()
    
    def execute_task(self, task: Dict) -> Dict:
        """
        Execute a dataless task
        Returns: {'success': bool, 'message': str, 'errors': List[str]}
        """
        result = {
            'success': False,
            'message': '',
            'errors': []
        }
        
        try:
            # Setup phase
            setup_result = self._execute_setup(task.get('setup', {}))
            if not setup_result['success']:
                result['errors'].extend(setup_result['errors'])
                result['message'] = 'Setup failed'
                return result
            
            # Execute actions
            actions = task.get('actions', [])
            if not actions:
                result['message'] = 'No actions to execute'
                result['success'] = True
                return result
            
            for i, action in enumerate(actions):
                action_result = self._execute_action(action)
                if not action_result['success']:
                    result['errors'].append(f"Action {i+1} failed: {action_result['error']}")
                    if action.get('stop_on_error', True):
                        result['message'] = f'Task stopped at action {i+1}'
                        return result
            
            result['success'] = True
            result['message'] = f'Task completed successfully. Executed {len(actions)} actions.'
            
        except Exception as e:
            result['errors'].append(f"Task execution error: {str(e)}")
            result['message'] = 'Task execution failed'
        
        finally:
            # Cleanup
            self.controller.stop()
        
        return result
    
    def _execute_setup(self, setup: Dict) -> Dict:
        """Execute task setup (launch browser, navigate)"""
        try:
            browser_type = setup.get('browser', 'chrome')
            url = setup.get('url', '')
            
            if not url:
                return {'success': False, 'errors': ['No URL specified in setup']}
            
            # Launch browser
            success = self.controller.launch_browser(browser_type)
            if not success:
                return {'success': False, 'errors': [f'Failed to launch {browser_type} browser']}
            
            # Navigate to URL
            nav_success = self.controller.navigate(url)
            if not nav_success:
                return {'success': False, 'errors': [f'Failed to navigate to {url}']}
            
            # Wait a moment for page to load
            time.sleep(2)
            
            return {'success': True, 'errors': []}
            
        except Exception as e:
            return {'success': False, 'errors': [f'Setup error: {str(e)}']}
    
    def _execute_action(self, action: Dict) -> Dict:
        """Execute a single action"""
        try:
            action_type = action.get('type', '')
            
            if action_type == 'navigate':
                return self._execute_navigate(action)
            elif action_type == 'click':
                return self._execute_click(action)
            elif action_type == 'set_value':
                return self._execute_set_value(action)
            elif action_type == 'wait':
                return self._execute_wait(action)
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
            
        except Exception as e:
            return {'success': False, 'error': f'Action execution error: {str(e)}'}
    
    def _execute_navigate(self, action: Dict) -> Dict:
        """Execute navigate action"""
        try:
            url = action.get('url', '')
            if not url:
                return {'success': False, 'error': 'No URL specified for navigate action'}
            
            success = self.controller.navigate(url)
            if success:
                time.sleep(1)  # Wait for navigation
                return {'success': True, 'error': ''}
            else:
                return {'success': False, 'error': f'Failed to navigate to {url}'}
                
        except Exception as e:
            return {'success': False, 'error': f'Navigate error: {str(e)}'}
    
    def _execute_click(self, action: Dict) -> Dict:
        """Execute click action"""
        try:
            selector = action.get('selector', '')
            if not selector:
                return {'success': False, 'error': 'No selector specified for click action'}
            
            page = self.controller.pages.get('main')
            if not page:
                return {'success': False, 'error': 'No active browser page'}
            
            # Try to click the element
            page.click(selector, timeout=5000)
            time.sleep(0.5)  # Brief pause after click
            
            return {'success': True, 'error': ''}
            
        except Exception as e:
            return {'success': False, 'error': f'Click error: {str(e)}'}
    
    def _execute_set_value(self, action: Dict) -> Dict:
        """Execute set value action"""
        try:
            selector = action.get('selector', '')
            value = action.get('value', '')
            
            if not selector:
                return {'success': False, 'error': 'No selector specified for set_value action'}
            
            page = self.controller.pages.get('main')
            if not page:
                return {'success': False, 'error': 'No active browser page'}
            
            # Clear and fill the element
            page.fill(selector, value, timeout=5000)
            time.sleep(0.5)  # Brief pause after input
            
            return {'success': True, 'error': ''}
            
        except Exception as e:
            return {'success': False, 'error': f'Set value error: {str(e)}'}
    
    def _execute_wait(self, action: Dict) -> Dict:
        """Execute wait action"""
        try:
            duration = action.get('duration', 1)
            time.sleep(duration)
            return {'success': True, 'error': ''}
            
        except Exception as e:
            return {'success': False, 'error': f'Wait error: {str(e)}'}