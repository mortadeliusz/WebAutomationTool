"""
Browser Detection - Detect installed browsers on the system
"""

import os
import platform
import subprocess
import winreg
from typing import Dict, List, Optional

class BrowserDetector:
    """Detect installed browsers using multiple methods"""
    
    SUPPORTED_BROWSERS = {
        'chrome': {
            'name': 'Google Chrome',
            'engine': 'chromium',
            'platforms': ['windows', 'macos', 'linux']
        },
        'firefox': {
            'name': 'Mozilla Firefox', 
            'engine': 'gecko',
            'platforms': ['windows', 'macos', 'linux']
        },
        'edge': {
            'name': 'Microsoft Edge',
            'engine': 'chromium', 
            'platforms': ['windows']
        }
    }
    
    BROWSER_PATHS = {
        'chrome': {
            'windows': [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ],
            'macos': ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            'linux': ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
        },
        'firefox': {
            'windows': [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            'macos': ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            'linux': ["/usr/bin/firefox"]
        },
        'edge': {
            'windows': [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        }
    }
    
    def __init__(self):
        self.current_platform = self._get_current_platform()
    
    def _get_current_platform(self) -> str:
        """Get current platform name"""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macos'
        return system
    
    def detect_installed_browsers(self) -> Dict[str, Dict[str, str]]:
        """Detect all installed supported browsers"""
        browsers = {}
        
        for browser_id, config in self.SUPPORTED_BROWSERS.items():
            if self.current_platform in config['platforms']:
                path = self._find_browser_executable(browser_id)
                if path:
                    browsers[browser_id] = {
                        'name': config['name'],
                        'path': path,
                        'engine': config['engine']
                    }
        
        return browsers
    
    def _find_browser_executable(self, browser_id: str) -> Optional[str]:
        """Find executable path using multiple detection methods"""
        # Method 1: File system check
        paths = self.BROWSER_PATHS.get(browser_id, {}).get(self.current_platform, [])
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Method 2: Registry check (Windows only)
        if self.current_platform == 'windows':
            registry_path = self._check_windows_registry(browser_id)
            if registry_path:
                return registry_path
        
        # Method 3: Command line check
        command_path = self._check_command_availability(browser_id)
        if command_path:
            return command_path
        
        return None
    
    def _check_windows_registry(self, browser_id: str) -> Optional[str]:
        """Check Windows registry for browser installation"""
        if self.current_platform != 'windows':
            return None
        
        registry_keys = {
            'chrome': r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            'firefox': r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
            'edge': r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"
        }
        
        key_path = registry_keys.get(browser_id)
        if not key_path:
            return None
        
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                path = winreg.QueryValue(key, "")
                if path and os.path.exists(path):
                    return path
        except (WindowsError, FileNotFoundError):
            pass
        
        return None
    
    def _check_command_availability(self, browser_id: str) -> Optional[str]:
        """Check if browser is available in system PATH"""
        commands = {
            'chrome': ['chrome', 'google-chrome', 'chromium-browser'],
            'firefox': ['firefox'],
            'edge': ['msedge']
        }
        
        browser_commands = commands.get(browser_id, [])
        
        for command in browser_commands:
            try:
                result = subprocess.run(
                    [command, '--version'], 
                    capture_output=True, 
                    check=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return command  # Return command name, not full path
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def get_browser_info(self, browser_id: str) -> Optional[Dict[str, str]]:
        """Get information about a specific browser"""
        return self.SUPPORTED_BROWSERS.get(browser_id)
    
    def is_browser_supported(self, browser_id: str) -> bool:
        """Check if browser is supported on current platform"""
        config = self.SUPPORTED_BROWSERS.get(browser_id)
        if not config:
            return False
        return self.current_platform in config['platforms']