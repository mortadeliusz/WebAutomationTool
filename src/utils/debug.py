"""Debug configuration utility"""
import json
from pathlib import Path

_debug_enabled = None

def is_debug() -> bool:
    """Check if debug mode is enabled"""
    global _debug_enabled
    if _debug_enabled is None:
        config_path = Path(__file__).parent.parent.parent / "config.json"
        with open(config_path) as f:
            data = json.load(f)
            _debug_enabled = data.get('debug', False)
    return _debug_enabled
