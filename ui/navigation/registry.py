"""
Page Registry - Central configuration for all application pages
"""

from ui.pages.workflow_execution import WorkflowExecutionPage
from ui.pages.workflow_management import WorkflowManagementPage
from ui.pages.subscription import SubscriptionPage
from ui.pages.test_page import TestPage
from ui.pages.browser_test import BrowserTestPage

# Central page configuration
PAGES = [
    {
        "name": "workflow_execution",
        "class": WorkflowExecutionPage,
        "menu_text": "Workflow Execution"
    },
    {
        "name": "workflow_management", 
        "class": WorkflowManagementPage,
        "menu_text": "Workflow Management"
    },
    {
        "name": "subscription",
        "class": SubscriptionPage,
        "menu_text": "Subscription"
    },
    {
        "name": "test_page",
        "class": TestPage,
        "menu_text": "Test Page"
    },
    {
        "name": "browser_test",
        "class": BrowserTestPage,
        "menu_text": "Browser Test"
    }
]


def get_pages():
    """Get list of all registered pages"""
    return PAGES


def get_page_config(name: str):
    """Get configuration for specific page"""
    for page in PAGES:
        if page["name"] == name:
            return page
    return None