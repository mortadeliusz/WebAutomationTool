"""
Task Execution Thread - Execute tasks in worker thread with own browser
"""

import time
from typing import Dict, List
from PyQt6.QtCore import QThread, pyqtSignal

from core.browser_controller import BrowserController

class TaskExecutionThread(QThread):
    """Execute task in worker thread with own browser lifecycle"""
    
    # Signals for UI updates
    progress_update = pyqtSignal(int, int, str)  # current, total, message
    action_completed = pyqtSignal(int, bool, str)  # action_index, success, message
    execution_finished = pyqtSignal(dict)  # result summary
    
    def __init__(self, task: Dict):
        super().__init__()
        self.task = task
        self.should_stop = False
        self.browser_controller = None
    
    def stop_execution(self):
        """Request execution to stop"""
        self.should_stop = True
    
    def run(self):
        """Execute task with own browser lifecycle"""
        result = {
            'success': False,
            'message': '',
            'errors': [],
            'actions_completed': 0,
            'actions_total': len(self.task.get('actions', []))
        }
        
        # Create own browser controller
        self.browser_controller = BrowserController()
        
        try:
            print("🚀 Task execution starting with own browser...")
            
            # Setup phase
            setup_result = self._execute_setup(self.task.get('setup', {}))
            if not setup_result['success']:
                result['errors'].extend(setup_result['errors'])
                result['message'] = 'Setup failed'
                self.execution_finished.emit(result)
                return
            
            # Execute actions
            actions = self.task.get('actions', [])
            if not actions:
                result['message'] = 'No actions to execute'
                result['success'] = True
                self.execution_finished.emit(result)
                return
            
            for i, action in enumerate(actions):
                if self.should_stop:
                    result['message'] = f'Execution cancelled at action {i+1}'
                    break
                
                self.progress_update.emit(i, len(actions), f"Executing action {i+1}: {action.get('description', action['type'])}")
                
                action_result = self._execute_action(action)
                self.action_completed.emit(i, action_result['success'], action_result.get('error', ''))
                
                if not action_result['success']:
                    result['errors'].append(f"Action {i+1} failed: {action_result['error']}")
                    if action.get('stop_on_error', True):
                        result['message'] = f'Task stopped at action {i+1}'
                        break
                
                result['actions_completed'] = i + 1
            
            if not self.should_stop and result['actions_completed'] == len(actions):
                result['success'] = True
                result['message'] = f'Task completed successfully. Executed {len(actions)} actions.'
            
        except Exception as e:
            result['errors'].append(f"Task execution error: {str(e)}")
            result['message'] = 'Task execution failed'
        
        finally:
            # Always cleanup browser
            if self.browser_controller:
                try:
                    print("🧹 Cleaning up execution browser...")
                    self.browser_controller.stop()
                except Exception as e:
                    print(f"Warning: Execution browser cleanup error: {e}")
            
            self.execution_finished.emit(result)
    
    def _execute_setup(self, setup: Dict) -> Dict:
        """Execute task setup (launch browser, navigate)"""
        try:
            browser_type = setup.get('browser', 'chrome')
            url = setup.get('url', '')
            
            if not url:
                return {'success': False, 'errors': ['No URL specified in setup']}
            
            self.progress_update.emit(0, 1, f"Launching {browser_type} browser...")
            
            # Launch browser
            success = self.browser_controller.launch_browser(browser_type)
            if not success:
                return {'success': False, 'errors': [f'Failed to launch {browser_type} browser']}
            
            self.progress_update.emit(0, 1, f"Navigating to {url}...")
            
            # Navigate to URL
            nav_success = self.browser_controller.navigate(url)
            if not nav_success:
                return {'success': False, 'errors': [f'Failed to navigate to {url}']}
            
            # Wait a moment for page to load
            time.sleep(2)
            
            return {'success': True, 'errors': []}
            
        except Exception as e:
            return {'success': False, 'errors': [f'Setup error: {str(e)}']}
    
    def _execute_action(self, action: Dict) -> Dict:
        """Execute a single action"""
        if self.should_stop:
            return {'success': False, 'error': 'Execution cancelled'}
        
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
            
            success = self.browser_controller.navigate(url)
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
            
            page = self.browser_controller.pages.get('main')
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
            
            page = self.browser_controller.pages.get('main')
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
            
            # Break wait into smaller chunks to allow cancellation
            chunks = max(1, int(duration * 10))  # 0.1 second chunks
            chunk_duration = duration / chunks
            
            for _ in range(chunks):
                if self.should_stop:
                    return {'success': False, 'error': 'Wait cancelled'}
                time.sleep(chunk_duration)
            
            return {'success': True, 'error': ''}
            
        except Exception as e:
            return {'success': False, 'error': f'Wait error: {str(e)}'}