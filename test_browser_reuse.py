"""
Test browser reuse functionality - CRITICAL for hybrid workflow
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.browser_controller import BrowserController
from core.element_picker import ElementPicker

async def test_browser_reuse():
    """Test that browser can be reused multiple times without issues"""
    
    controller = BrowserController()
    
    try:
        print("🚀 Test 1: Launch browser")
        success = await controller.launch_browser('chrome')
        print(f"   Launch result: {success}")
        
        print("🌐 Test 2: Navigate to Google")
        await controller.navigate('https://www.google.com')
        title = await controller.get_page_title()
        print(f"   Page title: {title}")
        
        print("🔍 Test 3: First element picker")
        page = controller.pages['main']
        picker = ElementPicker(page)
        print("   Element picker created - click any element on the page")
        result1 = await picker.pick_element()
        print(f"   First pick result: {result1['selector'][:50]}...")
        
        print("🔍 Test 4: Second element picker (CRITICAL TEST)")
        print("   Testing browser reuse - click another element")
        result2 = await picker.pick_element()
        print(f"   Second pick result: {result2['selector'][:50]}...")
        
        print("🌐 Test 5: Navigate to different site")
        await controller.navigate('https://www.github.com')
        title = await controller.get_page_title()
        print(f"   New page title: {title}")
        
        print("🔍 Test 6: Third element picker on new site")
        print("   Testing browser reuse after navigation - click an element")
        result3 = await picker.pick_element()
        print(f"   Third pick result: {result3['selector'][:50]}...")
        
        print("✅ ALL TESTS PASSED - Browser reuse is working!")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("🧹 Cleaning up...")
        await controller.stop()

if __name__ == "__main__":
    asyncio.run(test_browser_reuse())