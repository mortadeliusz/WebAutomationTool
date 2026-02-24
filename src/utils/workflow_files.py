"""
Workflow File Utilities - Simple file operations for workflow management
"""

import json
import os
import logging
from typing import List, Optional
from datetime import datetime
from src.types import WorkflowDefinition, WorkflowMetadata

logger = logging.getLogger(__name__)


def ensure_workflows_dir(workflows_dir: str = "user_data/workflows") -> None:
    """Ensure workflows directory exists"""
    if not os.path.exists(workflows_dir):
        os.makedirs(workflows_dir)


def save_workflow(workflow: WorkflowDefinition, workflows_dir: str = "user_data/workflows") -> bool:
    """Save workflow to JSON file"""
    try:
        ensure_workflows_dir(workflows_dir)
        
        # Validate workflow structure
        if not _validate_workflow(workflow):
            logger.error(f"Invalid workflow structure: {workflow.get('name', 'Unknown')}")
            return False
        
        # Add metadata
        if 'created_at' not in workflow:
            workflow['created_at'] = datetime.now().isoformat()
        workflow['modified_at'] = datetime.now().isoformat()
        
        # Generate filename from workflow name
        filename = _generate_filename(workflow['name'])
        filepath = os.path.join(workflows_dir, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Workflow saved: {workflow['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving workflow: {e}")
        return False


def load_workflow(workflow_name: str, workflows_dir: str = "user_data/workflows") -> Optional[WorkflowDefinition]:
    """Load workflow from JSON file"""
    try:
        filename = _generate_filename(workflow_name)
        filepath = os.path.join(workflows_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Workflow not found: {workflow_name}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
            
        # Validate loaded workflow
        if not _validate_workflow(workflow):
            logger.error(f"Invalid workflow structure in file: {workflow_name}")
            return None
            
        return workflow
            
    except Exception as e:
        logger.error(f"Error loading workflow: {e}")
        return None


def list_workflows(workflows_dir: str = "user_data/workflows") -> List[WorkflowMetadata]:
    """List all available workflows with metadata"""
    workflows = []
    
    try:
        ensure_workflows_dir(workflows_dir)
        
        for filename in os.listdir(workflows_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(workflows_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        workflow = json.load(f)
                        
                    # Extract browser info for display
                    browsers_info = ""
                    if 'browsers' in workflow:
                        browser_types = [browser['browser_type'] for browser in workflow['browsers'].values()]
                        browsers_info = ", ".join(browser_types)
                    
                    workflows.append({
                        'name': workflow.get('name', 'Unknown'),
                        'browsers': browsers_info,
                        'actions_count': len(workflow.get('actions', [])),
                        'created_at': workflow.get('created_at', ''),
                        'modified_at': workflow.get('modified_at', '')
                    })
                except Exception as e:
                    logger.error(f"Error reading workflow file {filename}: {e}")
                    
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
    
    # Sort by modified date (newest first)
    workflows.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
    return workflows


def delete_workflow(workflow_name: str, workflows_dir: str = "user_data/workflows") -> bool:
    """Delete workflow file"""
    try:
        filename = _generate_filename(workflow_name)
        filepath = os.path.join(workflows_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Workflow deleted: {workflow_name}")
            return True
        
        logger.warning(f"Workflow not found for deletion: {workflow_name}")
        return False
        
    except Exception as e:
        logger.error(f"Error deleting workflow: {e}")
        return False


def create_workflow(name: str, browser_type: str = "chrome", starting_url: str = "") -> WorkflowDefinition:
    """Create a new workflow with basic structure"""
    return {
        'name': name,
        'browsers': {
            'main': {
                'browser_type': browser_type,
                'starting_url': starting_url
            }
        },
        'actions': []
    }


def _validate_workflow(workflow: WorkflowDefinition) -> bool:
    """Validate workflow structure"""
    try:
        # Required fields
        if 'name' not in workflow or not workflow['name']:
            return False
        
        if 'browsers' not in workflow or not isinstance(workflow['browsers'], dict):
            return False
        
        if 'actions' not in workflow or not isinstance(workflow['actions'], list):
            return False
        
        # Validate browsers structure
        for alias, browser in workflow['browsers'].items():
            if not isinstance(browser, dict):
                return False
            if 'browser_type' not in browser or 'starting_url' not in browser:
                return False
        
        # Validate actions structure
        for action in workflow['actions']:
            if not isinstance(action, dict):
                return False
            if 'type' not in action or 'browser_alias' not in action:
                return False
        
        return True
        
    except (KeyError, TypeError, AttributeError):
        return False


def validate_workflow(workflow: dict) -> tuple[bool, str]:
    """Validate workflow structure for execution"""
    # Check browsers exist
    if 'browsers' not in workflow or not workflow['browsers']:
        return False, "Workflow must have at least one browser"
    
    # Check actions have valid browser_alias
    browser_aliases = set(workflow['browsers'].keys())
    for i, action in enumerate(workflow.get('actions', [])):
        alias = action.get('browser_alias')
        if not alias:
            return False, f"Action {i+1} missing browser_alias"
        if alias not in browser_aliases:
            return False, f"Action {i+1} references non-existent browser '{alias}'"
    
    return True, None


def _generate_filename(workflow_name: str) -> str:
    """Generate safe filename from workflow name"""
    # Remove invalid characters and replace spaces with underscores
    safe_name = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    return f"{safe_name}.json"