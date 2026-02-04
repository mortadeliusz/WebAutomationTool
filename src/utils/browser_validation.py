"""
BrowserValidator - Centralized browser configuration validation
"""

from typing import Dict, Tuple


class BrowserValidator:
    """Browser configuration validation utilities"""
    
    VALID_BROWSER_TYPES = ['chrome', 'firefox', 'edge']
    
    @staticmethod
    def validate_config(
        alias: str,
        config: Dict,
        existing_browsers: Dict,
        old_alias: str = None
    ) -> Tuple[bool, str]:
        """
        Validate browser configuration
        
        Args:
            alias: Browser alias to validate
            config: Browser configuration dict
            existing_browsers: Dict of existing browser configs
            old_alias: Original alias if renaming (optional)
        
        Returns:
            (is_valid, error_message)
        """
        # Empty alias
        if not alias or not alias.strip():
            return False, "Alias cannot be empty"
        
        # Duplicate alias (skip if renaming to same name)
        if alias != old_alias and alias in existing_browsers:
            return False, f"Browser '{alias}' already exists"
        
        # Invalid browser type
        browser_type = config.get('browser_type')
        if browser_type not in BrowserValidator.VALID_BROWSER_TYPES:
            return False, f"Invalid browser type: {browser_type}"
        
        return True, ""
