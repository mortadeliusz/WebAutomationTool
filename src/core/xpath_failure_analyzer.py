"""
XPath Failure Analyzer - Intelligent analysis of failed selectors for self-healing
"""

import re
from typing import List, Dict, Any
from playwright.sync_api import Page

class XPathFailureAnalyzer:
    """Analyze failed XPath selectors to identify problematic attributes"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def analyze_failure(self, failed_xpath: str) -> List[Dict[str, str]]:
        """
        Analyze failed XPath and return blacklist of problematic attributes
        Returns: [{"element": "div", "attribute": "class", "value": "GzLjMd"}, ...]
        """
        try:
            # Parse XPath components
            components = self._parse_xpath_components(failed_xpath)
            blacklist = []
            
            # Test each component
            for component in components:
                if not self._test_component_exists(component):
                    blacklist.append({
                        "element": component.get("element", ""),
                        "attribute": component.get("attribute", ""),
                        "value": component.get("value", "")
                    })
            
            return blacklist
            
        except Exception as e:
            print(f"Error analyzing XPath failure: {e}")
            return []
    
    def _parse_xpath_components(self, xpath: str) -> List[Dict[str, str]]:
        """Parse XPath into testable components"""
        components = []
        
        # Pattern to match XPath parts like: //div[@class="value"] or //button[text()="text"]
        patterns = [
            # Element with attribute: //div[@class="value"]
            r'//(\w+)\[@(\w+)="([^"]+)"\]',
            # Element with contains: //div[contains(@class, "value")]
            r'//(\w+)\[contains\(@(\w+),\s*"([^"]+)"\)\]',
            # Element with text: //button[text()="value"]
            r'//(\w+)\[text\(\)="([^"]+)"\]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, xpath)
            for match in matches:
                if len(match) == 3:  # element, attribute, value
                    components.append({
                        "element": match[0],
                        "attribute": match[1],
                        "value": match[2]
                    })
                elif len(match) == 2:  # element, text
                    components.append({
                        "element": match[0],
                        "attribute": "text",
                        "value": match[1]
                    })
        
        return components
    
    def _test_component_exists(self, component: Dict[str, str]) -> bool:
        """Test if a specific component still exists on the page"""
        try:
            element = component.get("element", "")
            attribute = component.get("attribute", "")
            value = component.get("value", "")
            
            if not element or not attribute or not value:
                return False
            
            # Build test selector
            if attribute == "text":
                test_selector = f'//{element}[text()="{value}"]'
            elif attribute == "class":
                test_selector = f'//{element}[contains(@class, "{value}")]'
            else:
                test_selector = f'//{element}[@{attribute}="{value}"]'
            
            # Test if element exists
            elements = self.page.query_selector_all(test_selector)
            return len(elements) > 0
            
        except Exception:
            return False
    
    def get_failure_summary(self, blacklist: List[Dict[str, str]]) -> str:
        """Generate human-readable failure summary"""
        if not blacklist:
            return "No specific attribute failures detected"
        
        summaries = []
        for item in blacklist:
            element = item.get("element", "element")
            attribute = item.get("attribute", "attribute")
            value = item.get("value", "")
            summaries.append(f'{element} {attribute} "{value}" no longer exists')
        
        return "; ".join(summaries)