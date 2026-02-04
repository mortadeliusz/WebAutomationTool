"""
Element Picker - Toggle-based implementation (inject once, reuse)
"""

import re
from typing import Dict, Tuple, Optional, List
from playwright.async_api import Page
from src.utils.debug import is_debug

class ElementPicker:
    """Toggle-based element picker - inject once, enable/disable as needed"""
    
    # Class-level injection tracking
    _picker_injected_pages = set()
    
    def __init__(self):
        pass
    
    async def pick_element(self, page: Page) -> Dict[str, any]:
        """
        Toggle-based element picker - inject once, then just enable/disable
        """
        
        try:
            # 1. INJECT PICKER ONCE (if not already injected for this page)
            page_id = id(page)
            if page_id not in ElementPicker._picker_injected_pages:
                await self._inject_picker(page)
                ElementPicker._picker_injected_pages.add(page_id)
            
            # 2. ENABLE PICKER
            await page.evaluate("""
                console.log('[PICKER] Enabling picker mode');
                if (window.elementPicker) {
                    window.elementPicker.enable();
                } else {
                    console.error('[PICKER] Picker not found - injection failed');
                }
            """)
            
            # 3. WAIT FOR USER CLICK
            await page.wait_for_function("window.elementPicker && window.elementPicker.clickedElement", timeout=30000)
            
            # 4. GET ELEMENT AND GENERATE SELECTOR
            element_handle = await page.evaluate_handle("window.elementPicker.clickedElement")
            result = await self.generate_smart_selector(element_handle, page)
            
            # 5. DISABLE PICKER (keep injection for reuse)
            await page.evaluate("""
                console.log('[PICKER] Disabling picker mode');
                if (window.elementPicker) {
                    window.elementPicker.disable();
                }
            """)
            
            return {
                'success': True,
                'selector': result['selector'],
                'method': result['method'],
                'error': None
            }
            
        except Exception as e:
            # Disable picker on error
            try:
                await page.evaluate("window.elementPicker && window.elementPicker.disable();")
            except:
                pass
            
            return {
                'success': False,
                'selector': '',
                'method': 'css',
                'error': f"Error in element picking: {str(e)}"
            }
    
    async def _inject_picker(self, page: Page):
        """Inject picker once - creates reusable picker object"""
        await page.add_script_tag(content="""
            console.log('[PICKER] Injecting reusable picker');
            
            window.elementPicker = {
                active: false,
                clickedElement: null,
                overlay: null,
                listeners: {},
                
                enable: function() {
                    console.log('[PICKER] Enabling picker');
                    this.active = true;
                    this.clickedElement = null;
                    
                    // Create overlay if not exists
                    if (!this.overlay) {
                        this.overlay = document.createElement('div');
                        this.overlay.id = 'element-picker-overlay';
                        this.overlay.style.cssText = `
                            position: absolute;
                            background: rgba(0, 123, 255, 0.3);
                            border: 2px solid #007bff;
                            pointer-events: none;
                            z-index: 999999;
                            display: none;
                        `;
                        document.body.appendChild(this.overlay);
                    }
                    
                    // Define listeners
                    this.listeners.mouseover = (e) => {
                        if (!this.active) return;
                        console.log('[PICKER] Mouseover:', e.target.tagName);
                        const rect = e.target.getBoundingClientRect();
                        this.overlay.style.display = 'block';
                        this.overlay.style.left = rect.left + window.scrollX + 'px';
                        this.overlay.style.top = rect.top + window.scrollY + 'px';
                        this.overlay.style.width = rect.width + 'px';
                        this.overlay.style.height = rect.height + 'px';
                    };
                    
                    this.listeners.mouseout = (e) => {
                        if (!this.active) return;
                        this.overlay.style.display = 'none';
                    };
                    
                    this.listeners.click = (e) => {
                        if (!this.active) return;
                        console.log('[PICKER] Click captured:', e.target.tagName);
                        e.preventDefault();
                        e.stopPropagation();
                        this.clickedElement = e.target;
                        this.disable();
                    };
                    
                    // Add listeners
                    document.addEventListener('mouseover', this.listeners.mouseover);
                    document.addEventListener('mouseout', this.listeners.mouseout);
                    document.addEventListener('click', this.listeners.click, true);
                    
                    console.log('[PICKER] Picker enabled successfully');
                },
                
                disable: function() {
                    console.log('[PICKER] Disabling picker');
                    this.active = false;
                    
                    // Hide overlay
                    if (this.overlay) {
                        this.overlay.style.display = 'none';
                    }
                    
                    // Remove listeners
                    if (this.listeners.mouseover) {
                        document.removeEventListener('mouseover', this.listeners.mouseover);
                        document.removeEventListener('mouseout', this.listeners.mouseout);
                        document.removeEventListener('click', this.listeners.click, true);
                    }
                    
                    console.log('[PICKER] Picker disabled successfully');
                },
                
                cleanup: function() {
                    console.log('[PICKER] Full cleanup');
                    this.disable();
                    if (this.overlay) {
                        this.overlay.remove();
                        this.overlay = null;
                    }
                    this.clickedElement = null;
                }
            };
            
            console.log('[PICKER] Reusable picker injected successfully');
        """)
    
    async def generate_smart_selector(self, element_handle, page: Page) -> Dict[str, str]:
        """Generate selector with uniqueness verification"""
        try:
            element_info = await element_handle.evaluate("""
                el => {
                    const info = {
                        tag: el.tagName.toLowerCase(),
                        id: el.id,
                        name: el.name,
                        type: el.type,
                        role: el.getAttribute('role'),
                        ariaLabel: el.getAttribute('aria-label'),
                        placeholder: el.placeholder,
                        text: el.innerText?.trim(),
                        testId: el.getAttribute('data-testid'),
                        href: el.href,
                        alt: el.alt
                    };
                    return info;
                }
            """)
            
            candidates = []
            
            # Priority 1: Test ID (most stable)
            if element_info.get('testId') and not self._is_generated(element_info['testId'], 'testid'):
                candidates.append(f"[data-testid='{element_info['testId']}']")
            
            # Priority 2: ARIA label (accessibility-first)
            if element_info.get('ariaLabel') and not self._is_generated(element_info['ariaLabel'], 'aria-label'):
                candidates.append(f"[aria-label='{element_info['ariaLabel']}']")
            
            # Priority 3: Alt text (images)
            if element_info['tag'] == 'img' and element_info.get('alt') and not self._is_generated(element_info['alt'], 'alt'):
                candidates.append(f"img[alt='{element_info['alt']}']")
            
            # Priority 4: Stable ID
            if element_info.get('id') and not self._is_generated(element_info['id'], 'id'):
                candidates.append(f"#{element_info['id']}")
            
            # Priority 5: Name attribute
            if element_info.get('name') and not self._is_generated(element_info['name'], 'name'):
                candidates.append(f"[name='{element_info['name']}']")
            
            # Priority 6: Href (links, path only)
            if element_info['tag'] == 'a' and element_info.get('href'):
                href = element_info['href']
                # Strip query params and hash
                href = href.split('?')[0].split('#')[0]
                # Extract path if full URL
                if href.startswith('http'):
                    from urllib.parse import urlparse
                    href = urlparse(href).path
                if href and not self._is_generated(href, 'href'):
                    candidates.append(f"a[href='{href}']")
            
            # Priority 7: Placeholder (for inputs)
            if element_info.get('placeholder') and not self._is_generated(element_info['placeholder'], 'placeholder'):
                candidates.append(f"[placeholder='{element_info['placeholder']}']")
            
            # Priority 8: Role + text (partial match)
            tag = element_info['tag']
            if element_info.get('role') and element_info.get('text'):
                text_escaped = self._escape_xpath_string(element_info['text'])
                candidates.append(f"//*[@role='{element_info['role']}' and contains(., {text_escaped})]")
            
            # Priority 9: Partial text match
            if element_info.get('text'):
                if tag in ['button', 'a', 'span', 'label']:
                    text_escaped = self._escape_xpath_string(element_info['text'])
                    candidates.append(f"//{tag}[contains(., {text_escaped})]")
            
            # Test each candidate for uniqueness
            for selector in candidates:
                try:
                    count = await page.locator(selector).count()
                    
                    if count == 1:
                        return {
                            'selector': selector,
                            'method': 'css' if not selector.startswith('//') else 'xpath'
                        }
                    
                    elif count > 1:
                        # Try adding parent context to make it unique
                        refined = await self._try_parent_context(selector, element_handle, page)
                        if refined:
                            return {
                                'selector': refined,
                                'method': 'css' if not refined.startswith('//') else 'xpath'
                            }
                    
                except Exception:
                    continue
            
            # Fallback: position-based XPath
            xpath = await self._generate_xpath_fallback(element_handle)
            return {'selector': xpath, 'method': 'xpath'}
            
        except Exception:
            return {'selector': f"//{element_info.get('tag', 'body')}", 'method': 'xpath'}
    
    # Parent selector builder functions
    def _build_parent_testid(self, parent: Dict, value: str, as_xpath: bool) -> str:
        """Build testid parent selector"""
        if as_xpath:
            value_esc = self._escape_xpath_string(value)
            return f"//*[@data-testid={value_esc}]"
        else:
            value_esc = self._escape_css_string(value)
            return f"[data-testid={value_esc}]"
    
    def _build_parent_id(self, parent: Dict, value: str, as_xpath: bool) -> str:
        """Build id parent selector"""
        if as_xpath:
            value_esc = self._escape_xpath_string(value)
            return f"//*[@id={value_esc}]"
        else:
            value_esc = self._escape_css_string(value)
            # CSS ID selector: strip quotes from escaped value
            value_clean = value_esc.strip('"')
            return f"#{value_clean}"
    
    def _build_parent_aria_label(self, parent: Dict, value: str, as_xpath: bool) -> str:
        """Build aria-label parent selector"""
        if as_xpath:
            value_esc = self._escape_xpath_string(value)
            return f"//{parent['tag']}[@aria-label={value_esc}]"
        else:
            value_esc = self._escape_css_string(value)
            return f"{parent['tag']}[aria-label={value_esc}]"
    
    def _build_parent_name(self, parent: Dict, value: str, as_xpath: bool) -> str:
        """Build name parent selector"""
        if as_xpath:
            value_esc = self._escape_xpath_string(value)
            return f"//{parent['tag']}[@name={value_esc}]"
        else:
            value_esc = self._escape_css_string(value)
            return f"{parent['tag']}[name={value_esc}]"
    
    def _build_parent_tag(self, parent: Dict, value: str, as_xpath: bool) -> str:
        """Build tag-only parent selector (fallback)"""
        return f"//{parent['tag']}" if as_xpath else parent['tag']
    
    # Parent selector registry: (attr_key, attr_name, builder_function)
    _PARENT_SELECTOR_REGISTRY = [
        ('testId', 'data-testid', _build_parent_testid),
        ('id', 'id', _build_parent_id),
        ('ariaLabel', 'aria-label', _build_parent_aria_label),
        ('name', 'name', _build_parent_name),
        ('tag', 'tag', _build_parent_tag),
    ]
    
    def _build_parent_selectors(self, parent: Dict, as_xpath: bool) -> List[str]:
        """
        Build parent selectors using registry pattern.
        
        To add new attribute:
        1. Define builder function (copy existing pattern)
        2. Add to _PARENT_SELECTOR_REGISTRY
        """
        selectors = []
        
        for attr_key, attr_name, builder_fn in self._PARENT_SELECTOR_REGISTRY:
            # Tag is always added as fallback
            if attr_key == 'tag':
                selectors.append(builder_fn(self, parent, None, as_xpath))
                continue
            
            # Check attribute exists and not generated
            value = parent.get(attr_key)
            if not value or self._is_generated(value, attr_name):
                continue
            
            # Build selector using registered function
            selector = builder_fn(self, parent, value, as_xpath)
            selectors.append(selector)
        
        return selectors
    
    async def _try_parent_context(self, base_selector, element_handle, page: Page) -> Optional[str]:
        """Try adding parent context to make selector unique"""
        try:
            # Get parent chain up to body/html
            parents = await element_handle.evaluate("""
                el => {
                    const parents = [];
                    let current = el.parentElement;
                    let iterations = 0;
                    
                    while (current && iterations < 100) {
                        // Stop at document root
                        if (current.tagName === 'BODY' || current.tagName === 'HTML') {
                            break;
                        }
                        
                        parents.push({
                            tag: current.tagName.toLowerCase(),
                            id: current.id,
                            testId: current.getAttribute('data-testid'),
                            ariaLabel: current.getAttribute('aria-label'),
                            name: current.name
                        });
                        
                        current = current.parentElement;
                        iterations++;
                    }
                    
                    return parents;
                }
            """)
            
            if len(parents) == 0:
                return None
            
            # Determine if base selector is XPath
            is_xpath = base_selector.startswith('//')
            
            # Try each parent level (closest to furthest)
            for parent in parents:
                # Build parent selectors in priority order
                parent_selectors = self._build_parent_selectors(parent, is_xpath)
                
                # Test each parent selector
                for parent_sel in parent_selectors:
                    # Combine parent + base selector
                    if is_xpath:
                        selector = f"{parent_sel}{base_selector}"  # XPath: no space
                    else:
                        selector = f"{parent_sel} {base_selector}"  # CSS: space separator
                    
                    try:
                        count = await page.locator(selector).count()
                        if count == 1:
                            return selector
                    except Exception as e:
                        if is_debug():
                            print(f"[DEBUG] Parent selector failed: '{selector}' - {type(e).__name__}: {e}")
                        continue
            
            return None
            
        except Exception:
            return None
    
    async def _generate_xpath_fallback(self, element_handle) -> str:
        """Generate position-based XPath as fallback"""
        return await element_handle.evaluate("""
            el => {
                const getPath = (element) => {
                    if (element.id && !/^[0-9]/.test(element.id))
                        return `//*[@id="${element.id}"]`;
                    
                    const parts = [];
                    while (element && element.nodeType === Node.ELEMENT_NODE) {
                        let index = 1;
                        let sibling = element.previousSibling;
                        while (sibling) {
                            if (sibling.nodeType === Node.ELEMENT_NODE && 
                                sibling.tagName === element.tagName) index++;
                            sibling = sibling.previousSibling;
                        }
                        
                        const tagName = element.tagName.toLowerCase();
                        const part = index > 1 ? `${tagName}[${index}]` : tagName;
                        parts.unshift(part);
                        
                        element = element.parentElement;
                        if (element?.tagName === 'BODY') break;
                    }
                    return '//' + parts.join('/');
                };
                return getPath(el);
            }
        """)
    
    def _escape_xpath_string(self, text: str) -> str:
        """Escape quotes in XPath strings"""
        if not text:
            return '""'
        
        # No quotes - use double quotes
        if '"' not in text and "'" not in text:
            return f'"{text}"'
        
        # Only double quotes - use single quotes
        if '"' in text and "'" not in text:
            return f"'{text}'"
        
        # Only single quotes - use double quotes
        if "'" in text and '"' not in text:
            return f'"{text}"'
        
        # Both quotes - use concat
        parts = []
        current = []
        for char in text:
            if char == '"':
                if current:
                    parts.append(f'"{{"".join(current)}}"')
                    current = []
                parts.append("'\"'")
            else:
                current.append(char)
        if current:
            parts.append(f'"{{"".join(current)}}"')
        
        return f"concat({', '.join(parts)})"
    
    def _escape_css_string(self, text: str) -> str:
        """Escape quotes in CSS attribute selectors"""
        if not text:
            return '""'
        # Escape backslashes and quotes
        text = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{text}"'
    
    def _is_generated(self, value: str, context: str = 'generic') -> bool:
        """
        Check if attribute value looks dynamically generated.
        
        Args:
            value: The attribute value to check (assumed non-empty)
            context: Type of attribute being checked
        
        Returns:
            True if value appears to be auto-generated, False otherwise
        """
        # Pass-through contexts (never consider generated)
        if context in ['href', 'text', 'aria-label', 'alt', 'placeholder']:
            return False
        
        # For id, name, testid, and generic: check against code identifier patterns
        SEMANTIC_PATTERNS = [
            r'^[a-z]+$',                              # lowercase: "header"
            r'^[A-Z]+$',                              # UPPERCASE: "OK"
            r'^[a-z]+-[a-z]+(-[a-z]+)*$',            # kebab-case: "user-profile"
            r'^[a-z]+[A-Z][a-z]*([A-Z][a-z]*)*$',    # camelCase: "userName"
            r'^[a-z]+_[a-z]+(_[a-z]+)*$',            # snake_case: "user_name"
            r'^[A-Z][a-z]+([A-Z][a-z]*)*$',          # PascalCase: "UserName"
            r'^\d+$',                                 # Numbers: "1", "123"
        ]
        
        return not any(re.match(pattern + '$', value) for pattern in SEMANTIC_PATTERNS)
    
