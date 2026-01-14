"""
Element Picker - Clean slate implementation
"""

import re
from typing import Dict, Tuple, Optional, List
from playwright.async_api import Page

class ElementPicker:
    """Clean slate element picker - inject fresh, use once, remove completely"""
    
    def __init__(self):
        self.blacklist = []
    
    async def pick_element(self, page: Page, blacklist: List[Dict[str, str]] = None) -> Dict[str, any]:
        """
        Clean slate element picker - inject, use, remove completely
        """
        self.blacklist = blacklist or []
        
        try:
            # 1. CLEAN SLATE - Remove any existing picker artifacts
            await page.evaluate("""
                // Remove any existing overlays
                const existingOverlay = document.getElementById('element-picker-overlay');
                if (existingOverlay) existingOverlay.remove();
                
                // Clear any existing variables
                delete window.elementPickerActive;
                delete window.clickedElement;
                delete window.lastHighlighted;
                delete window.pickerListeners;
            """)
            
            # 2. INJECT FRESH PICKER
            await page.add_script_tag(content="""
                console.log('[PICKER] Starting fresh injection');
                console.log('[PICKER] Existing elementPickerActive:', window.elementPickerActive);
                console.log('[PICKER] Existing pickerListeners:', !!window.pickerListeners);
                console.log('[PICKER] Existing overlay:', !!document.getElementById('element-picker-overlay'));
                
                // Fresh picker state
                window.elementPickerActive = true;
                window.clickedElement = null;
                console.log('[PICKER] Set elementPickerActive to:', window.elementPickerActive);
                
                // Create overlay with unique reference
                let overlay = document.getElementById('element-picker-overlay');
                if (overlay) overlay.remove();
                
                overlay = document.createElement('div');
                overlay.id = 'element-picker-overlay';
                overlay.style.cssText = `
                    position: absolute;
                    background: rgba(0, 123, 255, 0.3);
                    border: 2px solid #007bff;
                    pointer-events: none;
                    z-index: 999999;
                    display: none;
                `;
                document.body.appendChild(overlay);
                console.log('[PICKER] Overlay created and added to DOM');
                
                // Store listeners for removal
                window.pickerListeners = {
                    mouseover: function(e) {
                        if (!window.elementPickerActive) return;
                        console.log('[PICKER] Mouseover triggered on:', e.target.tagName);
                        const rect = e.target.getBoundingClientRect();
                        overlay.style.display = 'block';
                        overlay.style.left = rect.left + window.scrollX + 'px';
                        overlay.style.top = rect.top + window.scrollY + 'px';
                        overlay.style.width = rect.width + 'px';
                        overlay.style.height = rect.height + 'px';
                    },
                    mouseout: function(e) {
                        if (!window.elementPickerActive) return;
                        console.log('[PICKER] Mouseout triggered');
                        overlay.style.display = 'none';
                    },
                    click: function(e) {
                        if (!window.elementPickerActive) return;
                        console.log('[PICKER] Click triggered on:', e.target.tagName);
                        e.preventDefault();
                        e.stopPropagation();
                        window.clickedElement = e.target;
                        window.elementPickerActive = false;
                        console.log('[PICKER] Element captured, picker deactivated');
                    }
                };
                
                // Add listeners
                document.addEventListener('mouseover', window.pickerListeners.mouseover);
                document.addEventListener('mouseout', window.pickerListeners.mouseout);
                document.addEventListener('click', window.pickerListeners.click, true);
                console.log('[PICKER] Event listeners added successfully');
                console.log('[PICKER] Final elementPickerActive:', window.elementPickerActive);
            """)
            
            # 3. WAIT FOR USER CLICK
            await page.wait_for_function("window.clickedElement", timeout=30000)
            
            # 4. GET ELEMENT AND GENERATE XPATH
            element_handle = await page.evaluate_handle("window.clickedElement")
            smart_xpath = await self.generate_smart_xpath_from_handle(element_handle)
            
            # 5. COMPLETE CLEANUP - Remove everything
            await page.evaluate("""
                // Remove listeners
                if (window.pickerListeners) {
                    document.removeEventListener('mouseover', window.pickerListeners.mouseover);
                    document.removeEventListener('mouseout', window.pickerListeners.mouseout);
                    document.removeEventListener('click', window.pickerListeners.click, true);
                }
                
                // Remove overlay
                const overlay = document.getElementById('element-picker-overlay');
                if (overlay) overlay.remove();
                
                // Clear all variables
                delete window.elementPickerActive;
                delete window.clickedElement;
                delete window.lastHighlighted;
                delete window.pickerListeners;
            """)
            
            return {
                'success': True,
                'selector': smart_xpath,
                'method': 'xpath',
                'error': None
            }
            
        except Exception as e:
            # Emergency cleanup on error
            try:
                await page.evaluate("""
                    if (window.pickerListeners) {
                        document.removeEventListener('mouseover', window.pickerListeners.mouseover);
                        document.removeEventListener('mouseout', window.pickerListeners.mouseout);
                        document.removeEventListener('click', window.pickerListeners.click, true);
                    }
                    const overlay = document.getElementById('element-picker-overlay');
                    if (overlay) overlay.remove();
                    delete window.elementPickerActive;
                    delete window.clickedElement;
                    delete window.pickerListeners;
                """)
            except:
                pass
            
            return {
                'success': False,
                'selector': '',
                'method': 'xpath',
                'error': f"Error in element picking: {str(e)}"
            }
    
    async def generate_smart_xpath_from_handle(self, element_handle) -> str:
        """Generate smart XPath from element handle"""
        try:
            element_info = await element_handle.evaluate("""
                el => {
                    const getElementInfo = (element) => {
                        const attrs = {};
                        for (let attr of element.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        return {
                            tagName: element.tagName.toLowerCase(),
                            attributes: attrs,
                            textContent: element.textContent?.trim() || ''
                        };
                    };
                    
                    const elements = [];
                    let current = el;
                    while (current && current.nodeType === Node.ELEMENT_NODE) {
                        elements.push(getElementInfo(current));
                        current = current.parentElement;
                        if (current?.tagName?.toLowerCase() === 'body') break;
                    }
                    
                    return elements;
                }
            """)
            
            if not element_info:
                return "//body"
            
            target_element = element_info[0]
            ancestors = element_info[1:] if len(element_info) > 1 else []
            
            return self._build_unique_xpath(target_element, ancestors)
            
        except Exception as e:
            return "//body"
    
    def _build_unique_xpath(self, target_element, ancestors) -> str:
        """Build XPath with uniqueness verification"""
        tag_name = target_element['tagName']
        attributes = target_element['attributes']
        text_content = target_element['textContent']
        
        clean_attrs = self._get_clean_attributes(target_element)
        candidates = []
        
        # Priority 1: Clean ID
        if 'id' in clean_attrs:
            candidates.append(f'//[@id="{clean_attrs["id"]}"]')
        
        # Priority 2: Element type + clean name
        if 'name' in clean_attrs:
            candidates.append(f'//{tag_name}[@name="{clean_attrs["name"]}"]')
        
        # Priority 3: Element type + test attributes
        test_attrs = ['data-testid', 'data-cy', 'data-test', 'data-automation', 'data-qa']
        for attr in test_attrs:
            if attr in clean_attrs:
                candidates.append(f'//{tag_name}[@{attr}="{clean_attrs[attr]}"]')
        
        # Priority 4: Element type + stable text content
        if (text_content and len(text_content) < 50 and 
            tag_name in ['button', 'a', 'span', 'label'] and
            not self._is_random(text_content)):
            candidates.append(f'//{tag_name}[text()="{text_content}"]')
        
        # Priority 5: Element type + type attribute
        if 'type' in attributes:
            candidates.append(f'//{tag_name}[@type="{attributes["type"]}"]')
        
        # Priority 6: Just element type
        candidates.append(f'//{tag_name}')
        
        base_selector = candidates[0] if candidates else f'//{tag_name}'
        
        if len(candidates) > 1 or not ('id' in clean_attrs):
            return self._add_ancestor_context(base_selector, ancestors)
        
        return base_selector
    
    def _is_blacklisted(self, element_tag: str, attribute: str, value: str) -> bool:
        """Check if element+attribute combination is blacklisted"""
        for item in self.blacklist:
            if (item.get("element") == element_tag and 
                item.get("attribute") == attribute and 
                item.get("value") == value):
                return True
        return False
    
    def _get_clean_attributes(self, element_info: Dict) -> Dict[str, str]:
        """Get clean attributes, filtering out blacklisted and random values"""
        tag_name = element_info['tagName']
        attributes = element_info['attributes']
        clean_attrs = {}
        
        for attr_name, attr_value in attributes.items():
            if self._is_blacklisted(tag_name, attr_name, attr_value):
                continue
            if self._is_random(attr_value):
                continue
            clean_attrs[attr_name] = attr_value
        
        return clean_attrs
    
    def _is_random(self, value: str) -> bool:
        """Check if attribute value looks auto-generated"""
        if not value or len(value) < 2 or len(value) > 30:
            return True
        
        SEMANTIC_PATTERNS = [
            r'^[a-z]+$',
            r'^[a-z]+-[a-z]+(-[a-z]+)*$',
            r'^[a-z]+[A-Z][a-z]*([A-Z][a-z]*)*$',
            r'^[a-z]+_[a-z]+(_[a-z]+)*$',
            r'^[A-Z][a-z]+([A-Z][a-z]*)*$',
        ]
        
        return not any(re.match(pattern + '$', value) for pattern in SEMANTIC_PATTERNS)
    
    def _add_ancestor_context(self, base_selector, ancestors):
        """Add ancestor context to improve specificity"""
        if not ancestors:
            return base_selector
        
        for ancestor in ancestors:
            ancestor_context = self._get_clean_ancestor_selector(ancestor)
            if ancestor_context:
                return f"{ancestor_context}{base_selector}"
        
        return base_selector
    
    def _get_clean_ancestor_selector(self, ancestor_info):
        """Get clean selector for ancestor element"""
        tag_name = ancestor_info['tagName']
        clean_attrs = self._get_clean_attributes(ancestor_info)
        
        if tag_name in ['form', 'nav', 'main', 'section', 'article', 'header', 'footer']:
            return f"//{tag_name}"
        
        if 'id' in clean_attrs:
            return f'//[@id="{clean_attrs["id"]}"]'
        
        if 'class' in clean_attrs:
            classes = clean_attrs['class'].split()
            for cls in classes:
                if not self._is_blacklisted(tag_name, 'class', cls) and not self._is_random(cls):
                    return f'//{tag_name}[contains(@class, "{cls}")]'
        
        return None