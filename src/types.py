"""
Type definitions for common data structures across the application
"""

from typing import TypedDict, List, Dict, Any, Optional


class BrowserConfig(TypedDict):
    """Browser configuration in workflow"""
    browser_type: str
    starting_url: str


class ActionDefinition(TypedDict):
    """Action definition in workflow"""
    type: str
    browser_alias: str
    selector: Optional[str]
    value: Optional[str]


class WorkflowDefinition(TypedDict):
    """Complete workflow definition"""
    name: str
    browsers: Dict[str, BrowserConfig]
    actions: List[ActionDefinition]
    created_at: Optional[str]
    modified_at: Optional[str]


class WorkflowMetadata(TypedDict):
    """Workflow metadata for listing"""
    name: str
    browsers: str
    actions_count: int
    created_at: str
    modified_at: str


class ActionResult(TypedDict):
    """Result of action execution"""
    success: bool
    error: Optional[str]


class RowResult(TypedDict):
    """Result of workflow execution for a single row"""
    row_index: int
    success: bool
    actions: List[Dict[str, Any]]


class WorkflowExecutionResult(TypedDict):
    """Complete workflow execution result"""
    success: bool
    total_rows: int
    successful_rows: int
    failed_rows: int
    results: List[RowResult]
    error: Optional[str]


class BrowserOperationResult(TypedDict):
    """Result of browser operation"""
    success: bool
    error: Optional[str]
    errors: Optional[List[str]]


class UserSessionData(TypedDict, total=False):
    """User session data from launcher"""
    email: str
    access: bool
    subscription_tier: Optional[str]
