#!/usr/bin/env python3
"""
CustomTkinter Theme Editor Launcher
Run this script to launch the theme editor tool
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from tools.theme_editor.main import main

if __name__ == "__main__":
    main()