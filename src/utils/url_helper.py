"""
URL Helper - Normalize URLs with HTTPS->HTTP fallback
"""

from typing import Dict, Any
from playwright.async_api import Page


async def normalize_and_navigate(page: Page, url: str, timeout: int = 30000) -> Dict[str, Any]:
    """
    Normalize URL and navigate with HTTPS->HTTP fallback.
    
    Args:
        page: Playwright page object
        url: URL to navigate to (with or without protocol)
        timeout: Navigation timeout in milliseconds
        
    Returns:
        Dict with success status and error message
        
    Behavior:
        - If protocol specified: Use as-is
        - If no protocol: Try HTTPS first, fallback to HTTP
    """
    if not url:
        return {'success': False, 'error': 'No URL specified'}
    
    url = url.strip()
    
    # If protocol already specified, use as-is
    if url.startswith(('http://', 'https://', 'file://')):
        try:
            await page.goto(url, timeout=timeout)
            return {'success': True, 'error': None}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Try HTTPS first
    try:
        await page.goto(f'https://{url}', timeout=timeout)
        return {'success': True, 'error': None}
    except:
        # Fallback to HTTP
        try:
            await page.goto(f'http://{url}', timeout=timeout)
            return {'success': True, 'error': None}
        except Exception as e:
            return {'success': False, 'error': f'Failed to navigate: {str(e)}'}
