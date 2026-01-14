"""
Template Processing - Pure function for resolving template expressions
"""

import re
from typing import Dict


def resolve_expression(expression: str, row_data: Dict) -> str:
    """
    Resolve template expression with {{col()}} variables
    
    Args:
        expression: "Mr {{col('first_name')}} {{col('last_name')}}"
        row_data: {'first_name': 'John', 'last_name': 'Smith'}
    
    Returns:
        "Mr John Smith"
    """
    if not expression or '{{' not in expression:
        return expression
    
    def replace_match(match):
        func_call = match.group(1).strip()
        
        # Parse col('name')
        col_match = re.match(r"col\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", func_call)
        if col_match:
            return str(row_data.get(col_match.group(1), ''))
        
        # Parse col(0)
        col_idx_match = re.match(r"col\s*\(\s*(\d+)\s*\)", func_call)
        if col_idx_match:
            idx = int(col_idx_match.group(1))
            keys = list(row_data.keys())
            return str(row_data.get(keys[idx], '')) if idx < len(keys) else ''
        
        return f"{{{{UNKNOWN: {func_call}}}}}"
    
    return re.sub(r'\{\{([^}]+)\}\}', replace_match, expression)