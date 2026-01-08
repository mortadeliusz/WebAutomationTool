"""
Template Evaluator - Process template expressions in task actions
"""

import re
import pandas as pd
from typing import Any, Union, Optional

class TemplateEvaluator:
    """Evaluates template expressions like {{col('Email')}} and {{col(0)}}"""
    
    TEMPLATE_PATTERN = re.compile(r'\{\{([^}]+)\}\}')
    COL_FUNCTION_PATTERN = re.compile(r"col\s*\(\s*(['\"]?)([^'\"]+)\1\s*\)")
    
    def __init__(self):
        pass
    
    def is_template(self, value: Any) -> bool:
        """Check if value contains template expressions"""
        if not isinstance(value, str):
            return False
        return bool(self.TEMPLATE_PATTERN.search(value))
    
    def evaluate_template(self, value: Any, df: pd.DataFrame, row_index: int, default_value: Optional[str] = None) -> str:
        """Evaluate template expressions in value using data from specific row"""
        if not self.is_template(value):
            return str(value) if value is not None else ""
        
        def replace_expression(match):
            expression = match.group(1).strip()
            try:
                result = self._evaluate_expression(expression, df, row_index)
                return str(result) if result is not None else ""
            except Exception as e:
                # If template evaluation fails, use default value
                if default_value is not None:
                    return str(default_value)
                raise ValueError(f"Template evaluation failed: {expression} - {str(e)}")
        
        try:
            return self.TEMPLATE_PATTERN.sub(replace_expression, str(value))
        except Exception as e:
            if default_value is not None:
                return str(default_value)
            raise e
    
    def _evaluate_expression(self, expression: str, df: pd.DataFrame, row_index: int) -> Any:
        """Evaluate a single template expression"""
        # Match col('name') or col(0) patterns
        col_match = self.COL_FUNCTION_PATTERN.match(expression.strip())
        
        if col_match:
            quote_char = col_match.group(1)  # Empty string if no quotes
            param = col_match.group(2)
            
            if quote_char:
                # String parameter - column name
                column_name = param
                if column_name not in df.columns:
                    raise ValueError(f"Column '{column_name}' not found")
                return df.iloc[row_index][column_name]
            else:
                # No quotes - should be integer index
                try:
                    column_index = int(param)
                    if column_index < 0 or column_index >= len(df.columns):
                        raise ValueError(f"Column index {column_index} out of range")
                    return df.iloc[row_index, column_index]
                except ValueError:
                    raise ValueError(f"Invalid column index: {param}")
        
        raise ValueError(f"Unsupported expression: {expression}")
    
    def extract_required_columns(self, task_config: dict) -> set:
        """Extract all column names referenced in task templates"""
        required_columns = set()
        
        def extract_from_actions(actions):
            for action in actions:
                # Check value field
                if 'value' in action and self.is_template(action['value']):
                    columns = self._extract_columns_from_template(action['value'])
                    required_columns.update(columns)
                
                # Check other template fields (url, etc.)
                for field in ['url', 'selector']:
                    if field in action and self.is_template(action[field]):
                        columns = self._extract_columns_from_template(action[field])
                        required_columns.update(columns)
        
        # Extract from all action sections
        for section in ['initialization', 'pre_loop_actions', 'loop_actions', 'post_loop_actions']:
            if section in task_config:
                extract_from_actions(task_config[section])
        
        return required_columns
    
    def _extract_columns_from_template(self, template_value: str) -> set:
        """Extract column names from a template string"""
        columns = set()
        
        for match in self.TEMPLATE_PATTERN.finditer(template_value):
            expression = match.group(1).strip()
            col_match = self.COL_FUNCTION_PATTERN.match(expression)
            
            if col_match:
                quote_char = col_match.group(1)
                param = col_match.group(2)
                
                if quote_char:
                    # String parameter - column name
                    columns.add(param)
                # Note: We don't extract numeric indices as they're positional
        
        return columns
    
    def validate_task_templates(self, task_config: dict, df: pd.DataFrame) -> dict:
        """Validate that all template references can be resolved with given data"""
        required_columns = self.extract_required_columns(task_config)
        available_columns = set(df.columns)
        
        missing_columns = required_columns - available_columns
        
        return {
            'valid': len(missing_columns) == 0,
            'required_columns': list(required_columns),
            'missing_columns': list(missing_columns),
            'available_columns': list(available_columns)
        }