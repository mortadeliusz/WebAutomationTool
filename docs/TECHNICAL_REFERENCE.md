# Technical Reference - Implementation Details

> **Modus Operandi Compliance:** This document contains technical implementation details only, following "Separation of concerns" from [MODUS_OPERANDI.md](./MODUS_OPERANDI.md).

## Technology Stack

### **Core Technologies:**
- **Python 3.11+** - Language choice for cross-platform compatibility
- **CustomTkinter 5.2.2+** - UI framework (see [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md#adr-001))
- **async-tkinter-loop 0.10.3+** - Async integration for CustomTkinter
- **Playwright 1.57.0+** - Browser automation framework
- **Pandas 2.3.3+** - Data processing and manipulation

### **Supporting Libraries:**
- **openpyxl 3.1.5+** - Excel file support
- **PyYAML 6.0.3+** - YAML configuration support
- **Poetry** - Dependency management (per modus operandi rules)

---

## File Structure

```
WebAutomationTool/
├── main.py                         # Application bootstrap
├── config.json                     # Application configuration
├── pyproject.toml                  # Dependencies (managed by Poetry only)
├── ui/                             # User interface layer
│   ├── main_layout.py              # Main application layout
│   ├── navigation/                 # Navigation system
│   │   ├── controller.py           # Page lifecycle management
│   │   ├── registry.py             # Page configuration
│   │   └── sidebar.py              # Navigation UI
│   ├── pages/                      # Application pages
│   │   ├── workflow_execution.py
│   │   ├── workflow_management.py
│   │   └── subscription.py
│   └── components/                 # Reusable UI components
│       ├── workflow_list_view.py
│       ├── actions_list.py
│       ├── data_table.py
│       └── fields/                 # Form field components
├── src/                            # Business logic layer
│   ├── app_services.py             # Global service management
│   ├── core/                       # Core business modules
│   │   ├── browser_controller.py
│   │   ├── workflow_executor.py
│   │   ├── action_handlers.py
│   │   ├── data_loader.py
│   │   ├── template_processing.py
│   │   ├── element_picker.py
│   │   ├── theme_manager.py
│   │   └── user_preferences.py
│   └── utils/                      # Utility modules
│       ├── state_manager.py
│       ├── browser_detector.py
│       └── workflow_files.py
├── config/                         # Configuration files
│   ├── custom_theme.json
│   └── user_preferences.json
├── user_data/                      # User-generated content
│   ├── workflows/
│   ├── preferences/
│   └── logs/
└── docs/                           # Documentation
```

---

## Architecture Patterns

### **Registry Pattern (Navigation)**
```python
# ui/navigation/registry.py
PAGES = [
    {
        "name": "workflow_management",
        "class": WorkflowManagementPage,
        "menu_text": "Workflow Management"
    }
]
```

### **Controller Pattern (Page Management)**
```python
# ui/navigation/controller.py
class PageController:
    def show_page(self, name: str) -> bool:
        page = self.pages[name]
        if hasattr(page, 'on_show'):
            page.on_show()
        page.grid()
        return True
```

### **Service Layer (Dependency Injection)**
```python
# src/app_services.py
_browser_controller = None

def get_browser_controller() -> BrowserController:
    global _browser_controller
    if _browser_controller is None:
        _browser_controller = BrowserController()
    return _browser_controller
```

---

## Async Integration

### **CustomTkinter + Playwright Integration**
```python
# main.py
from async_tkinter_loop.mixins import AsyncCTk

class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        # AsyncCTk enables async support

if __name__ == "__main__":
    app = App()
    app.async_mainloop()  # Async event loop
```

### **Async Button Handlers**
```python
from async_tkinter_loop import async_handler

class BrowserTestPage(ctk.CTkFrame):
    @async_handler
    async def launch_browser(self):
        controller = get_browser_controller()
        await controller.launch_browser("chrome")
```

---

## Component Architecture

### **Field Component System**
```python
# Schema-driven field generation
FIELD_DEFINITIONS = {
    'selector': {
        'component': 'selector_picker',
        'label': 'Element Selector',
        'has_picker': True
    }
}

ACTION_SCHEMAS = {
    'click': {'required': ['selector'], 'optional': ['description']}
}
```

### **Theme Management**
```python
# src/core/theme_manager.py
def get_component_colors(component_name: str) -> dict:
    return COMPONENT_COLORS.get(component_name, {})

# Component usage
class MenuItem(ctk.CTkLabel):
    def __init__(self, parent, text: str):
        self.colors = get_component_colors("MenuItemLabel")
        super().__init__(parent, text=text)
```

---

## Data Flow

### **Template Variable Processing**
```python
# src/core/template_processing.py
def resolve_expression(expression: str, row_data: Dict) -> str:
    """
    Resolve {{col('name')}} or {{col(0)}} expressions
    """
    if not expression or '{{' not in expression:
        return expression
    return re.sub(r'\\{\\{([^}]+)\\}\\}', replace_match, expression)
```

### **Action Execution Pipeline**
```python
# src/core/action_execution.py
async def execute_action(action: Dict, row_data: Dict = None) -> Dict:
    action_type = action.get('type', '')
    handler = get_action_handler(action_type)
    page = browser_controller.get_existing_page(action.get('browser_alias'))
    return await handler(action, page, row_data)
```

---

## State Management

### **Hybrid Persistence Strategy**
```python
# src/utils/state_manager.py
def set_last_visited_page(page_name: str) -> bool:
    """Immediate persistence for critical state"""
    try:
        set_user_preference("last_visited_page", page_name)
        return True
    except Exception:
        return False

# Session state for high-frequency updates
_session_state = {}

def set_session_state(key: str, value):
    """Session batching for performance"""
    _session_state[key] = value
```

---

## Browser Integration

### **Playwright Controller**
```python
# src/core/browser_controller.py
class BrowserController:
    async def launch_browser_page(self, browser_type: str, alias: str) -> Optional[Page]:
        """Launch browser and return page"""
        
    def get_existing_page(self, alias: str) -> Optional[Page]:
        """Get existing page or None"""
        
    async def close_browser_page(self, alias: str) -> bool:
        """Close browser page"""
```

### **Element Picker Integration**
```python
# src/core/element_picker.py
class ElementPicker:
    async def pick_element(self, page: Page) -> Dict:
        """Toggle-based JavaScript injection for element selection"""
        if not self.is_injected(page):
            await self.inject_picker_script(page)
        return await self.enable_picker(page)
```

---

## Testing Strategy

### **Component Testing**
- **Pages:** Test with mock containers
- **Controllers:** Test with mock UI components  
- **Services:** Test with mock dependencies
- **Integration:** Test complete workflows

### **Async Testing**
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_browser_controller():
    controller = BrowserController()
    result = await controller.launch_browser("chrome")
    assert result['success'] == True
```

---

## Build and Deployment

### **PyInstaller Configuration**
```python
# build.spec
a = Analysis(
    ['main.py'],
    datas=[
        ('ui/assets', 'ui/assets'),
        ('config/custom_theme.json', 'config')
    ],
    hiddenimports=['playwright', 'pandas', 'customtkinter']
)
```

### **Distribution Strategy**
- **Single executable** - No installation required
- **Portable configuration** - Settings travel with executable
- **Browser detection** - Automatic discovery of installed browsers

---

## Performance Considerations

### **Optimization Strategies**
- **Lazy loading** - Load components on demand
- **Browser session cleanup** - Proper resource disposal
- **Memory management** - Efficient handling of large datasets
- **Theme caching** - Class-level theme application tracking

### **Performance Targets**
- **Application startup:** < 3 seconds
- **Page switching:** < 100ms
- **Browser launch:** < 5 seconds
- **Data processing:** 100+ rows per minute

---

## Error Handling

### **Graceful Degradation**
```python
def get_last_visited_page() -> str:
    try:
        return get_user_preference("last_visited_page", "workflow_management")
    except Exception:
        return "workflow_management"  # Safe fallback
```

### **Error Categories**
- **User Errors:** Invalid data, missing files
- **System Errors:** Browser crashes, network issues
- **Application Errors:** Component failures, state corruption

---

## Security Considerations

### **Local Processing**
- All automation logic executed locally
- No data transmission to external servers
- User authentication handled through existing browser sessions

### **Data Privacy**
- No telemetry or usage tracking
- User data stays on local machine
- Browser sessions isolated per user

---

*This technical reference follows the implementation patterns established in [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) and adheres to principles in [MODUS_OPERANDI.md](./MODUS_OPERANDI.md).*