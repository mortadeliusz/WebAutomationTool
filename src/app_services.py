"""
Global application services - initialized once by App

This module provides global access to application services without prop drilling.
Services are initialized once at app startup and cleaned up on shutdown.
"""

import asyncio
from typing import Optional
from src.core.browser_controller import BrowserController

# Global service instances
_browser_controller: Optional[BrowserController] = None

def initialize_services():
    """Initialize all application services - called once by App on startup"""
    global _browser_controller
    _browser_controller = BrowserController()

def get_browser_controller() -> BrowserController:
    """
    Get browser controller instance
    
    Returns:
        BrowserController instance
        
    Raises:
        RuntimeError: If services not initialized - call initialize_services() first
    """
    if not _browser_controller:
        raise RuntimeError("Services not initialized - call initialize_services() first")
    return _browser_controller

async def cleanup_services():
    """Cleanup all services - called by App on shutdown"""
    global _browser_controller
    if _browser_controller:
        await _browser_controller.stop()
        _browser_controller = None
    clear_workflow_data_sample()

def reset_services():
    """Reset services for testing purposes"""
    global _browser_controller
    _browser_controller = None


# Session-level workflow data sample (not persisted)
_workflow_data_sample = None


def get_workflow_data_sample():
    """Get current workflow editing data sample"""
    return _workflow_data_sample


def set_workflow_data_sample(data_sample):
    """Set workflow editing data sample"""
    global _workflow_data_sample
    _workflow_data_sample = data_sample


def clear_workflow_data_sample():
    """Clear data sample (on workflow save/cancel)"""
    global _workflow_data_sample
    _workflow_data_sample = None