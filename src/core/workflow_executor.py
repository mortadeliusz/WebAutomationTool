"""
Workflow Executor - Orchestrate workflow execution with data iteration
"""

import pandas as pd
from typing import Dict, List, Any
from src.core.action_execution import execute_action
from src.app_services import get_browser_controller


class WorkflowExecutor:
    """Orchestrate workflow execution across data rows"""
    
    async def execute_workflow(self, workflow_def: Dict, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute workflow for all data rows
        
        Args:
            workflow_def: Workflow definition with browsers and actions
            data: DataFrame with row data
        
        Returns:
            {
                'success': bool,
                'total_rows': int,
                'successful_rows': int,
                'failed_rows': int,
                'results': List[Dict]
            }
        """
        results = []
        successful_rows = 0
        failed_rows = 0
        
        actions = workflow_def.get('actions', [])
        browsers = workflow_def.get('browsers', {})
        
        if not actions:
            return {
                'success': False,
                'error': 'No actions in workflow',
                'total_rows': 0,
                'successful_rows': 0,
                'failed_rows': 0,
                'results': []
            }
        
        if not browsers:
            return {
                'success': False,
                'error': 'No browsers configured in workflow',
                'total_rows': 0,
                'successful_rows': 0,
                'failed_rows': 0,
                'results': []
            }
        
        # Initialize all browsers upfront
        browser_controller = get_browser_controller()
        for alias, config in browsers.items():
            page = browser_controller.get_existing_page(alias)
            if not page:
                page = await browser_controller.launch_browser_page(
                    config['browser_type'], alias
                )
                if page and config.get('starting_url'):
                    await browser_controller.navigate(config['starting_url'], alias)
        
        # Execute actions for each data row
        for index, row in data.iterrows():
            row_data = row.to_dict()
            row_results = []
            row_success = True
            
            # Execute each action in sequence
            for action in actions:
                result = await execute_action(action, row_data)
                row_results.append({
                    'action_type': action.get('type'),
                    'success': result.get('success'),
                    'error': result.get('error')
                })
                
                if not result.get('success'):
                    row_success = False
                    # Continue with next action even if one fails
            
            # Track row result
            if row_success:
                successful_rows += 1
            else:
                failed_rows += 1
            
            results.append({
                'row_index': int(index),
                'success': row_success,
                'actions': row_results
            })
        
        return {
            'success': True,
            'total_rows': len(data),
            'successful_rows': successful_rows,
            'failed_rows': failed_rows,
            'results': results
        }