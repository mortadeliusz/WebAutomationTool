"""
Data Loader - Handle loading and processing of various data formats
"""

import pandas as pd
import json
import yaml
import io
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

class DataLoader:
    """Handles loading data from various formats and sources"""
    
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.json', '.yaml', '.yml'}
    
    def __init__(self):
        self.current_data = None
        self.current_columns = []
    
    def load_from_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Load data from file path"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = self._process_json_data(data)
            elif file_path.suffix.lower() in {'.yaml', '.yml'}:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                df = self._process_json_data(data)
            
            self.current_data = df
            self.current_columns = list(df.columns)
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load {file_path.name}: {str(e)}")
    
    def load_from_text(self, text_content: str, format_hint: Optional[str] = None) -> pd.DataFrame:
        """Load data from text content (copy/paste)"""
        text_content = text_content.strip()
        
        if not text_content:
            raise ValueError("No data provided")
        
        try:
            # Try to detect format
            if format_hint == 'json' or (text_content.startswith('{') or text_content.startswith('[')):
                data = json.loads(text_content)
                df = self._process_json_data(data)
            elif format_hint == 'yaml' or text_content.startswith('---'):
                data = yaml.safe_load(text_content)
                df = self._process_json_data(data)
            else:
                # Default to CSV
                df = pd.read_csv(io.StringIO(text_content))
            
            self.current_data = df
            self.current_columns = list(df.columns)
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse data: {str(e)}")
    
    def _process_json_data(self, data: Any) -> pd.DataFrame:
        """Process JSON/YAML data into DataFrame"""
        if isinstance(data, list):
            if not data:
                raise ValueError("Empty data list")
            
            # Check if list of objects (most common case)
            if isinstance(data[0], dict):
                df = pd.json_normalize(data)
            else:
                # List of simple values
                df = pd.DataFrame({'value': data})
        elif isinstance(data, dict):
            # Single object - convert to single-row DataFrame
            df = pd.json_normalize([data])
        else:
            raise ValueError("JSON data must be a list or object")
        
        return df
    
    def get_preview(self, df: pd.DataFrame, rows: int = 10) -> Dict[str, Any]:
        """Get preview data for UI display"""
        preview_df = df.head(rows)
        
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'preview_rows': len(preview_df),
            'columns': list(df.columns),
            'data': preview_df.to_dict('records'),
            'column_types': {col: str(df[col].dtype) for col in df.columns}
        }
    
    def get_columns(self) -> List[str]:
        """Get list of available columns"""
        return self.current_columns.copy() if self.current_columns else []
    
    def validate_columns(self, required_columns: List[str]) -> Dict[str, bool]:
        """Validate that required columns exist in current data"""
        if not self.current_columns:
            return {col: False for col in required_columns}
        
        return {col: col in self.current_columns for col in required_columns}