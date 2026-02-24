"""
Global application services - initialized once by App

This module provides global access to application services without prop drilling.
Services are initialized once at app startup and cleaned up on shutdown.
"""

import asyncio
import logging
from typing import Optional, Any
from src.core.browser_controller import BrowserController

logger = logging.getLogger(__name__)

# Global service instances
_browser_controller: Optional[BrowserController] = None

def initialize_services() -> None:
    """Initialize all application services - called once by App on startup"""
    global _browser_controller
    _browser_controller = BrowserController()
    logger.info("Browser controller initialized")

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

async def cleanup_services() -> None:
    """Cleanup all services - called by App on shutdown"""
    global _browser_controller
    if _browser_controller:
        result = await _browser_controller.stop()
        if result['success']:
            logger.info("Browser controller cleaned up successfully")
        else:
            logger.warning(f"Browser controller cleanup had errors: {result.get('errors')}")
        _browser_controller = None
    clear_workflow_data_sample()

def reset_services() -> None:
    """Reset services for testing purposes"""
    global _browser_controller
    _browser_controller = None


# Session-level workflow data sample (not persisted)
_workflow_data_sample: Optional[Any] = None


def get_workflow_data_sample() -> Optional[Any]:
    """Get current workflow editing data sample"""
    return _workflow_data_sample


def set_workflow_data_sample(data_sample: Any) -> None:
    """Set workflow editing data sample"""
    global _workflow_data_sample
    _workflow_data_sample = data_sample


def clear_workflow_data_sample() -> None:
    """Clear data sample (on workflow save/cancel)"""
    global _workflow_data_sample
    _workflow_data_sample = None