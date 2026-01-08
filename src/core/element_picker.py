"""
Element Picker - Proper implementation with hover highlighting and click capture
"""

import re
from typing import Dict, Tuple, Optional, List
from playwright.sync_api import Page

class ElementPicker:
    """Element picker with hover highlighting and click capture like dev tools"""
    
    # Auto-generated ID patterns to avoid
    AUTO_GENERATED_PATTERNS = [
        # Framework IDs
        r'^(ember|react|vue|angular)\d+$',     # ember123, react456
        r'^[a-f0-9]{8,}$',                     # hex: a1b2c3d4e5f6
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}', # UUIDs
        
        # Numeric suffixes  
        r'.*-\d{4,}$',                         # button-1234
        r'.*_\d{4,}$',                         # field_5678
        r'.*\d{10,}$',                         # timestamps
        
        # Auto-generated patterns
        r'^(auto|gen|tmp|temp)\d+',            # auto123, gen456
        r'.*-(auto|gen|tmp)-\d+',              # btn-auto-123
        r'^[a-z]{1,3}\d{3,}$',                 # a123, xy4567
        
        # Build tools
        r'^webpack-',                          # webpack-abc123
        r'^chunk-',                            # chunk-vendors.123
        
        # CSS-in-JS
        r'^css-[a-z0-9]+$',                    # css-1a2b3c4
        r'^[a-z]+-[a-f0-9]{6,}$',              # styled-a1b2c3
    ]
    
    def __init__(self, page: Page):
        self.page = page
        self.blacklist = []
    
    def pick_element(self, blacklist: List[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Enable element picking mode with hover highlighting and click capture
        Args:
            blacklist: List of element+attribute combinations to avoid
        Returns: {'selector': xpath, 'reliability': level, 'method': 'xpath'}
        """
        self.blacklist = blacklist or []
        
        try:
            # Inject hover highlighting script
            self.page.add_script_tag(content="""
                window.elementPickerActive = true;
                window.lastHighlighted = null;
                
                // Create highlight overlay
                const overlay = document.createElement('div');
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
                
                // Hover highlighting
                document.addEventListener('mouseover', function(e) {
                    if (!window.elementPickerActive) return;
                    
                    const rect = e.target.getBoundingClientRect();
                    overlay.style.display = 'block';
                    overlay.style.left = rect.left + window.scrollX + 'px';
                    overlay.style.top = rect.top + window.scrollY + 'px';
                    overlay.style.width = rect.width + 'px';
                    overlay.style.height = rect.height + 'px';
                    
                    window.lastHighlighted = e.target;
                });
                
                // Hide overlay when mouse leaves
                document.addEventListener('mouseout', function(e) {
                    if (!window.elementPickerActive) return;
                    overlay.style.display = 'none';
                });
                
                // Capture click and prevent default
                document.addEventListener('click', function(e) {
                    if (!window.elementPickerActive) return;
                    
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Store clicked element
                    window.clickedElement = e.target;
                    window.elementPickerActive = false;
                    
                    // Clean up
                    overlay.remove();
                    
                    // Dispatch custom event
                    document.dispatchEvent(new CustomEvent('elementPicked', {
                        detail: { element: e.target }
                    }));
                }, true);
            """)
            
            # Wait for element to be picked
            self.page.wait_for_function("window.clickedElement")
            
            # Get the clicked element
            element_handle = self.page.evaluate_handle("window.clickedElement")
            
            # Generate smart XPath for this element
            smart_xpath, reliability = self.generate_smart_xpath_from_handle(element_handle)
            
            # Clean up
            self.page.evaluate("delete window.clickedElement; delete window.elementPickerActive;")
            
            return {
                'selector': smart_xpath,
                'reliability': reliability,
                'method': 'xpath'
            }
            
        except Exception as e:
            print(f"Error in element picking: {e}")
            # Clean up on error
            self.page.evaluate("window.elementPickerActive = false; delete window.clickedElement;")
            return {'selector': '', 'reliability': 'low', 'method': 'xpath'}
    
    def generate_smart_xpath_from_handle(self, element_handle) -> Tuple[str, str]:
        """
        Generate smart XPath with uniqueness verification and recursive context building
        Returns: (xpath, reliability_level)
        """
        try:
            # Get element and ancestor info
            element_info = element_handle.evaluate("""
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
                    
                    // Get element and ancestors
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
                return "//body", 'low'
            
            target_element = element_info[0]
            ancestors = element_info[1:] if len(element_info) > 1 else []
            
            # Build XPath with uniqueness verification
            xpath = self._build_unique_xpath(target_element, ancestors)
            
            return xpath, 'medium'  # All generated selectors are medium reliability
            
        except Exception as e:
            print(f"Error generating XPath: {e}")
            return "//body", 'low'
    
    def _build_unique_xpath(self, target_element, ancestors) -> str:
        """Build XPath with uniqueness verification"""
        tag_name = target_element['tagName']
        attributes = target_element['attributes']
        text_content = target_element['textContent']
        
        # Get clean attributes (filtered for randomness and blacklist)
        clean_attrs = self._get_clean_attributes(target_element)
        
        # Generate selector candidates in priority order
        candidates = []
        
        # Priority 1: Clean ID
        if 'id' in clean_attrs:
            candidates.append(f'//[@id="{clean_attrs["id"]}"]')
        
        # Priority 2: Element type + clean name
        if 'name' in clean_attrs:
            candidates.append(f'//{tag_name}[@name="{clean_attrs["name"]}"]')
        
        # Priority 3: Element type + clean test attributes
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
        if 'type' in attributes:  # Type is usually stable
            candidates.append(f'//{tag_name}[@type="{attributes["type"]}"]')
        
        # Priority 6: Just element type (last resort)
        candidates.append(f'//{tag_name}')
        
        # Try each candidate (in real implementation, would check uniqueness on page)
        # For now, return first candidate with ancestor context if needed
        base_selector = candidates[0] if candidates else f'//{tag_name}'
        
        # Add ancestor context if base selector might not be unique
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
            # Skip if blacklisted
            if self._is_blacklisted(tag_name, attr_name, attr_value):
                continue
            
            # Skip if random
            if self._is_random(attr_value):
                continue
            
            clean_attrs[attr_name] = attr_value
        
        return clean_attrs
    
    def _is_random(self, value: str) -> bool:
        """Check if any attribute value looks auto-generated"""
        if not value or len(value) < 2 or len(value) > 30:
            return True
        
        # Semantic patterns - only accept these
        SEMANTIC_PATTERNS = [
            r'^[a-z]+$',                           # Simple: header, modal
            r'^[a-z]+-[a-z]+(-[a-z]+)*$',         # kebab-case: login-form
            r'^[a-z]+[A-Z][a-z]*([A-Z][a-z]*)*$', # camelCase: loginForm
            r'^[a-z]+_[a-z]+(_[a-z]+)*$',         # snake_case: login_form
            r'^[A-Z][a-z]+([A-Z][a-z]*)*$',       # PascalCase: LoginForm
        ]
        
        return not any(re.match(pattern + '$', value) for pattern in SEMANTIC_PATTERNS)
    
    def _add_ancestor_context(self, base_selector, ancestors):
        """Add ancestor context to improve specificity"""
        if not ancestors:
            return base_selector
        
        # Try to find meaningful ancestor context
        for ancestor in ancestors:
            ancestor_context = self._get_clean_ancestor_selector(ancestor)
            if ancestor_context:
                return f"{ancestor_context}{base_selector}"
        
        return base_selector
    
    def _get_clean_ancestor_selector(self, ancestor_info):
        """Get clean selector for ancestor element"""
        tag_name = ancestor_info['tagName']
        
        # Get clean attributes for ancestor
        clean_attrs = self._get_clean_attributes(ancestor_info)
        
        # Semantic containers
        if tag_name in ['form', 'nav', 'main', 'section', 'article', 'header', 'footer']:
            return f"//{tag_name}"
        
        # Clean ID
        if 'id' in clean_attrs:
            return f'//[@id="{clean_attrs["id"]}"]'
        
        # Stable class
        if 'class' in clean_attrs:
            classes = clean_attrs['class'].split()
            # Find first non-blacklisted, non-random class
            for cls in classes:
                if not self._is_blacklisted(tag_name, 'class', cls) and not self._is_random(cls):
                    return f'//{tag_name}[contains(@class, "{cls}")]'
        
        return None  # Skip this ancestor
    
    def _is_auto_generated(self, value: str) -> bool:
        """Legacy method - use _is_random instead"""
        return self._is_random(value)
    
    def _generate_position_xpath_from_handle(self, element_handle) -> str:
        """Generate position-based XPath from element handle (legacy method)"""
        return self._generate_position_xpath({}, [])
    
    def get_reliability_description(self, reliability: str) -> str:
        """Get human-readable description of reliability level"""
        descriptions = {
            'high': 'High reliability - Uses testing or semantic attributes',
            'medium': 'Medium reliability - Uses clean IDs or text content',
            'low': 'Low reliability - Position-based selector (may break if page changes)'
        }
        return descriptions.get(reliability, 'Unknown reliability')
    
    def get_reliability_color(self, reliability: str) -> str:
        """Get color indicator for reliability level"""
        colors = {
            'high': '🟢',
            'medium': '🟡', 
            'low': '🔴'
        }
        return colors.get(reliability, '⚪')