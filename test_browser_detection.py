"""
Test browser detection functionality
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.browser_detector import BrowserDetector

def test_browser_detection():
    """Test browser detection functionality"""
    print("Testing Browser Detection...")
    print("=" * 50)
    
    detector = BrowserDetector()
    
    print(f"Current platform: {detector.current_platform}")
    print()
    
    # Detect all browsers
    browsers = detector.detect_installed_browsers()
    
    if browsers:
        print("Detected browsers:")
        for browser_id, info in browsers.items():
            print(f"  {info['name']} ({browser_id})")
            print(f"    Path: {info['path']}")
            print(f"    Engine: {info['engine']}")
            print()
    else:
        print("No supported browsers found!")
        print()
        print("Supported browsers for your platform:")
        for browser_id, config in detector.SUPPORTED_BROWSERS.items():
            if detector.is_browser_supported(browser_id):
                print(f"  - {config['name']} ({browser_id})")
    
    print("=" * 50)

if __name__ == "__main__":
    test_browser_detection()