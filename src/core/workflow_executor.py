"""
Workflow Executor - Orchestrate workflow execution with data iteration
"""

import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
from tkinter import messagebox
from src.core.action_execution import execute_action
from src.app_services import get_browser_controller
from src.utils.workflow_files import validate_workflow


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
                'total': int,
                'successful': int,
                'failed': int,
                'errors': List[Dict]
            }
        """
        # Validate workflow
        valid, error = validate_workflow(workflow_def)
        if not valid:
            raise Exception(f"Invalid workflow: {error}")
        
        # Check for empty data
        if len(data) == 0:
            messagebox.showinfo("No Data", "Data file is empty. No rows to process.")
            return {'total': 0, 'successful': 0, 'failed': 0, 'errors': []}
        
        # Check for empty actions
        if not workflow_def.get('actions'):
            raise Exception("Workflow has no actions to execute")
        
        # Launch/get browsers (use as-is if exists)
        browser_controller = get_browser_controller()
        for alias, config in workflow_def['browsers'].items():
            page = await browser_controller.get_page(
                config['browser_type'],
                alias,
                config.get('starting_url'),
                force_navigate=False  # Use as-is if exists
            )
            
            if not page:
                raise Exception(f"Failed to get browser '{alias}'")
        
        # Execute rows (skip failed)
        results = {'total': len(data), 'successful': 0, 'failed': 0, 'errors': []}
        
        for index, row in data.iterrows():
            try:
                for action_index, action in enumerate(workflow_def['actions']):
                    result = await execute_action(action, row.to_dict())
                    if not result['success']:
                        raise Exception(result['error'])
                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'row': index + 1,
                    'action': action_index + 1 if 'action_index' in locals() else 'N/A',
                    'description': action.get('description', 'No description') if 'action' in locals() else 'N/A',
                    'error': str(e)
                })
        
        # Show summary
        self._show_execution_summary(results)
        
        return results
    
    def _show_execution_summary(self, results: dict):
        """Show execution summary with error details"""
        if results['failed'] > 0:
            # Save errors to CSV
            import csv
            error_file = Path("user_data/logs") / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            error_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(error_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['row', 'action', 'description', 'error']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results['errors'])
            
            # Show summary
            response = messagebox.askquestion(
                "Workflow Completed with Errors",
                f"Processed {results['total']} rows:\n"
                f"✓ {results['successful']} successful\n"
                f"✗ {results['failed']} failed\n\n"
                f"View error details?",
                icon='warning'
            )
            
            if response == 'yes':
                import os
                os.startfile(str(error_file))  # Windows
        else:
            messagebox.showinfo(
                "Workflow Completed",
                f"Successfully processed all {results['successful']} rows."
            )
