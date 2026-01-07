"""
Task Storage - Simple JSON-based task saving and loading
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class TaskStorage:
    """Simple file-based task storage"""
    
    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = tasks_dir
        self.ensure_tasks_dir()
    
    def ensure_tasks_dir(self):
        """Ensure tasks directory exists"""
        if not os.path.exists(self.tasks_dir):
            os.makedirs(self.tasks_dir)
    
    def save_task(self, task: Dict) -> bool:
        """Save task to JSON file"""
        try:
            # Add metadata
            task['created_at'] = datetime.now().isoformat()
            task['modified_at'] = datetime.now().isoformat()
            
            # Generate filename from task name
            filename = self._generate_filename(task['name'])
            filepath = os.path.join(self.tasks_dir, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(task, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving task: {e}")
            return False
    
    def load_task(self, task_name: str) -> Optional[Dict]:
        """Load task from JSON file"""
        try:
            filename = self._generate_filename(task_name)
            filepath = os.path.join(self.tasks_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error loading task: {e}")
            return None
    
    def list_tasks(self) -> List[Dict]:
        """List all available tasks"""
        tasks = []
        
        try:
            for filename in os.listdir(self.tasks_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.tasks_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            task = json.load(f)
                            tasks.append({
                                'name': task.get('name', 'Unknown'),
                                'description': task.get('description', ''),
                                'modified_at': task.get('modified_at', ''),
                                'uses_data': task.get('uses_data', True),
                                'actions_count': len(task.get('actions', []))
                            })
                    except Exception as e:
                        print(f"Error reading task file {filename}: {e}")
                        
        except Exception as e:
            print(f"Error listing tasks: {e}")
        
        # Sort by modified date (newest first)
        tasks.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
        return tasks
    
    def delete_task(self, task_name: str) -> bool:
        """Delete task file"""
        try:
            filename = self._generate_filename(task_name)
            filepath = os.path.join(self.tasks_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def _generate_filename(self, task_name: str) -> str:
        """Generate safe filename from task name"""
        # Remove invalid characters and replace spaces with underscores
        safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        return f"{safe_name}.json"
    
    def create_task_template(self, name: str, description: str, browser: str, url: str, uses_data: bool = False) -> Dict:
        """Create a basic task template"""
        return {
            'name': name,
            'description': description,
            'uses_data': uses_data,
            'error_handling': 'stop_on_error',  # Default: stop on first error (hidden from UI)
            'setup': {
                'browser': browser.lower(),
                'url': url
            },
            'actions': []
        }