"""
Task Execution Thread - Execute tasks in worker thread with own browser and self-healing
"""

import time
from typing import Dict, List, Optional
from PyQt6.QtCore import QThread, pyqtSignal
import pandas as pd

from core.browser_controller import BrowserController
from core.xpath_failure_analyzer import XPathFailureAnalyzer
from core.element_picker import ElementPicker
from core.template_evaluator import TemplateEvaluator

class TaskExecutionThread(QThread):
    """Execute task in worker thread with own browser lifecycle"""
    
    # Signals for UI updates
    progress_update = pyqtSignal(int, int, str)  # current, total, message
    action_completed = pyqtSignal(int, bool, str)  # action_index, success, message
    execution_finished = pyqtSignal(dict)  # result summary
    healing_requested = pyqtSignal(str, list)  # failed_xpath, blacklist
    
    def __init__(self, task: Dict, data: Optional[pd.DataFrame] = None):
        super().__init__()
        self.task = task
        self.data = data
        self.template_evaluator = TemplateEvaluator()
        self.should_stop = False
        self.browser_controller = None
        self.failure_analyzer = None
        self.healing_response = None
    
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
            'actions_total': 0,
            'rows_processed': 0,
            'rows_total': len(self.data) if self.data is not None else 0
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
            
            # Initialize failure analyzer after browser is ready
            page = self.browser_controller.pages.get('main')
            if page:
                self.failure_analyzer = XPathFailureAnalyzer(page)
            
            # Execute pre-loop actions
            pre_actions = self.task.get('pre_loop_actions', [])
            if pre_actions:
                pre_result = self._execute_actions(pre_actions, "Pre-loop")
                if not pre_result['success']:
                    result['errors'].extend(pre_result['errors'])
                    result['message'] = 'Pre-loop actions failed'
                    self.execution_finished.emit(result)
                    return
            
            # Execute main loop (with or without data)
            loop_actions = self.task.get('loop_actions', [])
            if loop_actions:
                if self.data is not None:
                    # Data-driven execution
                    loop_result = self._execute_data_loop(loop_actions)
                else:
                    # Single execution
                    loop_result = self._execute_actions(loop_actions, "Main")
                
                result['actions_completed'] = loop_result.get('actions_completed', 0)
                result['rows_processed'] = loop_result.get('rows_processed', 0)
                
                if not loop_result['success']:
                    result['errors'].extend(loop_result['errors'])
                    result['message'] = loop_result.get('message', 'Loop execution failed')
                    self.execution_finished.emit(result)
                    return
            
            # Execute post-loop actions
            post_actions = self.task.get('post_loop_actions', [])
            if post_actions:
                post_result = self._execute_actions(post_actions, "Post-loop")
                if not post_result['success']:
                    result['errors'].extend(post_result['errors'])
                    result['message'] = 'Post-loop actions failed'
                    self.execution_finished.emit(result)
                    return
            
            # Success
            if self.data is not None:
                result['message'] = f'Task completed successfully. Processed {len(self.data)} rows.'
            else:
                result['message'] = f'Task completed successfully.'
            result['success'] = True
            
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
    
    def _execute_actions(self, actions: List[Dict], phase_name: str) -> Dict:
        """Execute a list of actions (for pre/post loop phases)"""
        result = {
            'success': True,
            'errors': [],
            'actions_completed': 0
        }
        
        for i, action in enumerate(actions):
            if self.should_stop:
                result['success'] = False
                result['message'] = f'{phase_name} execution cancelled at action {i+1}'
                break
            
            self.progress_update.emit(i, len(actions), f"{phase_name} action {i+1}: {action.get('description', action['type'])}")
            
            action_result = self._execute_action(action)
            self.action_completed.emit(i, action_result['success'], action_result.get('error', ''))
            
            if not action_result['success']:
                result['errors'].append(f"{phase_name} action {i+1} failed: {action_result['error']}")
                if action.get('stop_on_error', True):
                    result['success'] = False
                    result['message'] = f'{phase_name} stopped at action {i+1}'
                    break
            
            result['actions_completed'] = i + 1
        
        return result
    
    def _execute_data_loop(self, loop_actions: List[Dict]) -> Dict:
        """Execute loop actions for each row of data"""
        result = {
            'success': True,
            'errors': [],
            'actions_completed': 0,
            'rows_processed': 0
        }
        
        total_rows = len(self.data)
        
        for row_idx in range(total_rows):
            if self.should_stop:
                result['message'] = f'Data loop cancelled at row {row_idx + 1}'
                break
            
            self.progress_update.emit(row_idx, total_rows, f"Processing row {row_idx + 1} of {total_rows}")
            
            # Execute all actions for this row
            row_success = True
            for action_idx, action in enumerate(loop_actions):
                if self.should_stop:
                    break
                
                # Resolve templates for this row
                resolved_action = self._resolve_action_templates(action, row_idx)
                
                action_result = self._execute_action(resolved_action)
                
                if not action_result['success']:
                    error_msg = f"Row {row_idx + 1}, Action {action_idx + 1}: {action_result['error']}"
                    result['errors'].append(error_msg)
                    
                    if action.get('stop_on_error', True):
                        result['success'] = False
                        result['message'] = f'Data loop stopped at row {row_idx + 1}, action {action_idx + 1}'
                        return result
                    
                    row_success = False
                    break
            
            if row_success:
                result['rows_processed'] += 1
        
        result['actions_completed'] = len(loop_actions) * result['rows_processed']
        return result
    
    def _resolve_action_templates(self, action: Dict, row_index: int) -> Dict:
        """Resolve template expressions in action for specific data row"""
        resolved_action = action.copy()
        
        # Fields that might contain templates
        template_fields = ['value', 'url', 'selector']
        
        for field in template_fields:
            if field in action:
                original_value = action[field]
                default_value = action.get('default') if field == 'value' else None
                
                try:
                    resolved_value = self.template_evaluator.evaluate_template(
                        original_value, self.data, row_index, default_value
                    )
                    resolved_action[field] = resolved_value
                except Exception as e:
                    # If template resolution fails, use default or original
                    if default_value is not None:
                        resolved_action[field] = default_value
                    else:
                        resolved_action[field] = original_value
                    print(f"Warning: Template resolution failed for {field}: {e}")
        
        return resolved_action
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
        """Execute click action with self-healing on failure"""
        try:
            selector = action.get('selector', '')
            if not selector:
                return {'success': False, 'error': 'No selector specified for click action'}
            
            page = self.browser_controller.pages.get('main')
            if not page:
                return {'success': False, 'error': 'No active browser page'}
            
            # Try original selector
            try:
                page.click(selector, timeout=5000)
                time.sleep(0.5)
                return {'success': True, 'error': ''}
            
            except Exception as click_error:
                # Attempt self-healing
                return self._attempt_healing(action, str(click_error))
                
        except Exception as e:
            return {'success': False, 'error': f'Click error: {str(e)}'}
    
    def _execute_set_value(self, action: Dict) -> Dict:
        """Execute set value action with self-healing on failure"""
        try:
            selector = action.get('selector', '')
            value = action.get('value', '')
            
            if not selector:
                return {'success': False, 'error': 'No selector specified for set_value action'}
            
            page = self.browser_controller.pages.get('main')
            if not page:
                return {'success': False, 'error': 'No active browser page'}
            
            # Try original selector
            try:
                page.fill(selector, value, timeout=5000)
                time.sleep(0.5)
                return {'success': True, 'error': ''}
            
            except Exception as fill_error:
                # Attempt self-healing
                return self._attempt_healing(action, str(fill_error))
                
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
    
    def _attempt_healing(self, action: Dict, error_message: str) -> Dict:
        """Attempt to heal failed selector"""
        if not self.failure_analyzer:
            return {'success': False, 'error': f'Element not found: {error_message}'}
        
        try:
            # Analyze the failure
            failed_xpath = action.get('selector', '')
            blacklist = self.failure_analyzer.analyze_failure(failed_xpath)
            
            if blacklist:
                failure_summary = self.failure_analyzer.get_failure_summary(blacklist)
                print(f"🔍 Failure analysis: {failure_summary}")
                
                # For now, return failure with healing info
                # In full implementation, would signal UI for user intervention
                return {
                    'success': False, 
                    'error': f'Element not found. Analysis: {failure_summary}',
                    'healing_available': True,
                    'blacklist': blacklist
                }
            else:
                return {'success': False, 'error': f'Element not found: {error_message}'}
                
        except Exception as e:
            return {'success': False, 'error': f'Healing failed: {str(e)}'}