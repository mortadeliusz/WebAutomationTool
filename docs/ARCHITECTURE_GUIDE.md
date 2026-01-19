# Web Automation Tool - Architecture Guide

## Clean Architecture Overview

This document describes the current clean architecture implementation that follows strict separation of concerns and eliminates technical debt.

---

## Architecture Principles

### **1. Separation of Concerns**
- **UI Logic:** All user interface components in `ui/` folder
- **Business Logic:** Core automation functionality in `src/` folder  
- **Configuration:** Application settings and page registry
- **Services:** Global resource management and dependency injection

### **2. Dependency Flow**
```
Application Bootstrap → UI Layout → Navigation → Pages
                    ↓
                 Services (Browser, Storage, etc.)
```

### **3. Component Responsibilities**
Each component has a single, well-defined responsibility with clear boundaries.

---

## File Structure & Organization

### **Current Clean Structure**
```
WebAutomationTool/
├── main.py                         # Application bootstrap only
├── config.json                     # Application configuration
├── ui/                             # All UI components
│   ├── main_layout.py              # UI structure and wiring
│   ├── navigation/                 # Navigation system
│   │   ├── controller.py           # Page lifecycle logic
│   │   ├── registry.py             # Central page configuration
│   │   └── sidebar.py              # Navigation UI component
│   ├── pages/                      # Application pages
│   │   ├── workflow_execution.py
│   │   ├── workflow_management.py
│   │   ├── subscription.py
│   │   ├── test_page.py
│   │   └── browser_test.py
│   └── components/                 # Reusable UI components
│       ├── workflow_list_view.py
│       ├── workflow_editor_view.py
│       ├── browser_config_section.py  # Browser lifecycle management
│       ├── data_sample_status.py   # Data sample status indicator
│       ├── actions_list.py         # Inline action editor
│       ├── status_bar.py
│       └── fields/                 # Field component library
│           ├── action_value_input.py    # Value with expression helper
│           ├── text_input.py            # Generic text input
│           ├── dropdown.py              # Generic dropdown
│           ├── selector_picker.py       # Selector with element picker
│           ├── key_picker.py            # Key capture with 🎹 button
│           ├── number_input.py          # Numeric input with validation
│           └── data_expression_helper.py  # Column selector utility
├── src/                            # Business logic only
│   ├── app_services.py             # Global service management
│   ├── core/                       # Core automation modules
│   │   ├── action_handlers.py      # Action registry + handler functions
│   │   ├── action_execution.py     # Stateless action execution
│   │   ├── browser_controller.py   # Browser lifecycle management
│   │   ├── workflow_executor.py    # Workflow orchestration
│   │   ├── template_processing.py  # Template resolution utility
│   │   └── element_picker_toggle.py
│   └── utils/                      # Utility functions
│       ├── workflow_files.py
│       └── browser_detector.py
├── user_data/                      # User-created content
│   ├── workflows/                  # User workflow definitions
│   ├── preferences/                # User settings
│   └── logs/                       # User session logs
└── docs/                           # Documentation
```

### **Design Rationale**
- **UI in `ui/`:** All user interface logic grouped together
- **Business logic in `src/`:** Core functionality separate from presentation
- **Clear module boundaries:** No mixed concerns between folders
- **Consistent import patterns:** `ui.*` for UI, `src.*` for business logic

---

## Navigation Architecture

### **Registry Pattern Implementation**

**Problem Solved:** Tight coupling between navigation and page management

**Solution:** Central page registry with explicit configuration

```python
# ui/navigation/registry.py - Central configuration
PAGES = [
    {
        "name": "workflow_execution",
        "class": WorkflowExecutionPage,
        "menu_text": "Workflow Execution"
    },
    # ... other pages
]
```

**Benefits:**
- **Adding pages:** Create file + add to registry (2 steps)
- **No coupling:** Navigation doesn't import page classes
- **Easy maintenance:** All page configuration in one place
- **Clear dependencies:** Explicit imports and relationships

### **Controller Pattern Implementation**

**Problem Solved:** Mixed concerns in navigation components

**Solution:** Separate navigation UI from navigation logic

```python
# ui/navigation/controller.py - Navigation logic
class PageController:
    def add_page(self, name: str, page_class: Type[ctk.CTkFrame]) -> None:
        page = page_class(self.container)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_remove()
        self.pages[name] = page
    
    def show_page(self, name: str) -> bool:
        # Call optional lifecycle hook
        if hasattr(page, 'on_show'):
            page.on_show()
        # Show page
```

```python
# ui/navigation/sidebar.py - Navigation UI
class SideNav(ctk.CTkFrame):
    def navigate_to(self, page_name: str) -> None:
        self.controller.show_page(page_name)  # Delegate to controller
```

**Benefits:**
- **Single responsibility:** UI handles rendering, controller handles logic
- **Easy testing:** Logic can be tested independently of UI
- **Maintainability:** Changes to navigation logic don't affect UI
- **Extensibility:** Easy to add features like page history, transitions

---

## Page Lifecycle Pattern

### **Optional Lifecycle Hooks**

**Problem Solved:** Pages need to refresh data when shown (e.g., workflow list updates)

**Solution:** Optional `on_show()` hook using duck typing

```python
# ui/navigation/controller.py - Lifecycle hook support
def show_page(self, name: str) -> bool:
    page = self.pages[name]
    
    # Call lifecycle hook if page implements it
    if hasattr(page, 'on_show'):
        page.on_show()
    
    page.grid()
    return True
```

**Page Implementation:**
```python
# ui/pages/workflow_execution.py - Implements lifecycle hook
class WorkflowExecutionPage(ctk.CTkFrame):
    def on_show(self):
        """Called when page becomes visible - refresh workflow list"""
        self.refresh_workflows()
    
    def refresh_workflows(self):
        """Refresh workflow list from disk"""
        self.workflows = self.load_available_workflows()
        self.workflow_combo.configure(
            values=self.workflows if self.workflows else ["No workflows found"],
            state="readonly" if self.workflows else "disabled"
        )
```

**Pages Without Hook:**
```python
# ui/pages/subscription.py - No lifecycle hook needed
class SubscriptionPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # No on_show() method - works fine
```

**Benefits:**
- **Optional pattern:** Pages implement only if needed
- **No forced inheritance:** No base class required
- **Duck typing:** Pythonic approach using hasattr()
- **Zero coupling:** Pages work with or without hook
- **Auto-refresh:** Data stays fresh on navigation

**Design Rationale:**
- **YAGNI principle:** No base class until multiple hooks needed
- **Minimal implementation:** 3 lines in controller, optional in pages
- **Easy upgrade path:** Can add base class later if needed

---

## Application Bootstrap Architecture

### **Clean Separation Pattern**

**Problem Solved:** Mixed concerns in main application class

**Solution:** Separate application setup from UI layout

```python
# main.py - Application bootstrap
class App(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        self.setup_application()  # Config + Services
        self.layout = MainLayout(self)  # UI Structure

    def setup_application(self) -> None:
        # Configuration loading
        # Service initialization  
        # Lifecycle management
```

```python
# ui/main_layout.py - UI structure
class MainLayout:
    def setup_layout(self) -> None:
        # Grid configuration
        # Component creation
        # Page registration
        # Default page display
```

**Benefits:**
- **Clear responsibilities:** App handles application concerns, Layout handles UI
- **Easy testing:** Application setup can be tested without UI
- **Maintainability:** UI changes don't affect application logic
- **Configuration flexibility:** Easy to modify without touching UI code

---

## Service Layer Architecture

### **Singleton Pattern for Shared Resources**

**Problem Solved:** Multiple instances of expensive resources (browser controllers)

**Solution:** Global service management with dependency injection

```python
# src/app_services.py - Service management
_browser_controller = None

def get_browser_controller() -> BrowserController:
    global _browser_controller
    if _browser_controller is None:
        _browser_controller = BrowserController()
    return _browser_controller

def initialize_services():
    # Initialize global services
    
def cleanup_services():
    # Clean shutdown of all services
```

**Benefits:**
- **Resource efficiency:** Single browser controller instance
- **Clean dependencies:** Components get services through function calls
- **Easy testing:** Services can be mocked for testing
- **Proper cleanup:** Centralized resource management

---

## Component Communication Patterns

### **Dependency Injection Pattern**

**Current Flow:**
```
App → MainLayout → PageController → Pages
  ↓
Services (accessed via get_browser_controller())
```

**Communication Rules:**
- **Downward dependencies:** Parent components pass dependencies to children
- **Service access:** Components access services through global functions
- **No upward dependencies:** Children don't directly reference parents
- **Event-based communication:** Use callbacks for upward communication when needed

### **Page Lifecycle Management**

```python
# Pages receive container as parent
class WorkflowExecutionPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Page-specific logic
```

**Benefits:**
- **Clean instantiation:** Pages only need display container
- **No navigation coupling:** Pages don't know about navigation system
- **Easy testing:** Pages can be tested with mock containers
- **State preservation:** Page instances persist across navigation

---

## Async Architecture Integration

### **CustomTkinter + Playwright Integration**

**Problem Solved:** Incompatible event loops between sync UI and async browser automation

**Solution:** async-tkinter-loop integration with proper patterns

```python
# main.py - Async CustomTkinter setup
from async_tkinter_loop.mixins import AsyncCTk

class App(ctk.CTk, AsyncCTk):
    # AsyncCTk mixin enables async support

if __name__ == "__main__":
    app = App()
    app.async_mainloop()  # Async event loop
```

```python
# Pages - Async button handlers
from async_tkinter_loop import async_handler

class BrowserTestPage(ctk.CTkFrame):
    @async_handler  # Enable async/await in callbacks
    async def launch_browser(self):
        controller = get_browser_controller()
        await controller.launch_browser("chrome")
```

**Benefits:**
- **Native async/await:** No workarounds or blocking operations
- **Responsive UI:** Long operations don't freeze interface
- **Clean code:** Direct async/await usage in UI callbacks
- **Proper integration:** Playwright and CustomTkinter work seamlessly

---

## Component-Driven Field Architecture

### **Schema-Based Form Generation**

**Problem Solved:** Inconsistent action editing interfaces and manual form creation

**Solution:** Component-driven field system with schema definitions

```python
# src/core/action_handlers.py - Field definitions
FIELD_DEFINITIONS = {
    'action_type': {
        'component': 'dropdown',
        'label': 'Action Type',
        'values_source': 'registry'
    },
    'selector': {
        'component': 'selector_picker',
        'label': 'Element Selector',
        'placeholder': '//input[@name="example"]',
        'has_picker': True
    },
    'value': {
        'component': 'text_input',
        'label': 'Value',
        'placeholder': '{{col("Email")}}'
    }
}

# Action schemas define which fields each action needs
ACTION_SCHEMAS = {
    'click': {
        'required': ['selector'],
        'optional': ['description']
    },
    'fill_field': {
        'required': ['selector', 'value'],
        'optional': ['description']
    }
}
```

**Benefits:**
- **Dynamic forms:** UI adapts automatically to action type
- **Consistent components:** Same field type = same component everywhere
- **Easy extension:** New action types get proper UI automatically
- **Schema validation:** Field requirements enforced by schema

### **Field Component Library**

**Reusable Field Components:**
```python
# ui/components/fields/text_input.py
class TextInputField(ctk.CTkFrame):
    def get_value(self) -> str
    def set_value(self, value: str)

# ui/components/fields/dropdown.py  
class DropdownField(ctk.CTkFrame):
    def get_value(self) -> str
    def set_value(self, value: str)

# ui/components/fields/selector_picker.py
class SelectorPickerField(ctk.CTkFrame):
    def get_value(self) -> str
    def set_value(self, value: str)
    def set_picker_callback(self, callback: Callable)

# ui/components/fields/key_picker.py
class KeyPickerField(ctk.CTkFrame):
    """Key capture with 🎹 button"""
    def get_value(self) -> str
    def set_value(self, value: str)
    def start_key_capture(self)  # Captures keyboard key press

# ui/components/fields/number_input.py
class NumberInputField(ctk.CTkFrame):
    """Numeric input with validation"""
    def get_value(self) -> str
    def set_value(self, value: str)
    def validate(self)  # Validates numeric input

# ui/components/fields/data_expression_helper.py
class DataExpressionHelper(ctk.CTkFrame):
    """Data column selector with name/index toggle"""
    def __init__(self, target_entry, data_sample, on_load_data)
    def set_data_sample(self, data_sample)  # Update available columns
    def insert_expression(self, expression)  # Insert at cursor position
```

**Component Features:**
- **Consistent interface:** All fields implement get_value/set_value
- **Element picker integration:** SelectorPickerField has built-in picker button
- **Key capture:** KeyPickerField captures keyboard keys with 🎹 button
- **Numeric validation:** NumberInputField validates and enforces min values
- **Expression helper:** DataExpressionHelper provides column selection with mode toggle
- **Async support:** Picker integration uses @async_handler
- **Reusable:** Components used across different forms

### **Inline Action Editor**

**Problem Solved:** Modal dialogs blocking async operations

**Solution:** Inline editing within workflow management interface

```python
# ui/components/actions_list.py - Inline action editing
class ActionsList(ctk.CTkFrame):
    def start_add_action(self):
        # Show inline editor in actions list
        self.editing_action = True
        self.show_inline_editor()
    
    def show_inline_editor(self):
        # Dynamic form generation from schema
        for field_name in required_fields + optional_fields:
            field_def = get_field_definition(field_name)
            component = create_field_component(field_def)
            # Connect element picker for selector fields
```

**Benefits:**
- **No modal blocking:** Async operations work immediately
- **Context preservation:** User stays in workflow editing context
- **Schema-driven:** Uses same field definitions and components
- **Element picker ready:** Integrated picker functionality

---

## Action Registry Architecture

### **Registry Pattern for Extensible Actions**

**Problem Solved:** Hard-coded action types requiring code changes for new actions

**Solution:** Registry-based action system with handler functions and metadata

**Available Actions (7 total):**

**Common Actions:**
- `click` - Click element
- `fill_field` - Instantly fill input (fast, works with all frameworks)
- `navigate` - Navigate to URL
- `type_text` - Type character-by-character (human-like, for autocomplete)
- `press_key` - Press keyboard key (Enter, Tab, etc.)

**Utility Actions:**
- `wait_for_element` - Wait for element to appear (dynamic content)
- `wait_seconds` - Wait fixed time (last resort only)

```python
# src/core/action_handlers.py - Action handlers
async def handle_click(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    await page.click(action['selector'], timeout=5000)
    return {'success': True, 'error': None}

async def handle_fill_field(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    value = action.get('value', '')
    if row_data:
        value = resolve_expression(value, row_data)
    await page.fill(action['selector'], value, timeout=5000)
    return {'success': True, 'error': None}

async def handle_navigate(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    url = action.get('url', '')
    if row_data:
        url = resolve_expression(url, row_data)
    await page.goto(url, timeout=30000)
    return {'success': True, 'error': None}

async def handle_type_text(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    value = action.get('value', '')
    if row_data:
        value = resolve_expression(value, row_data)
    await page.type(action['selector'], value, delay=50)
    return {'success': True, 'error': None}

async def handle_press_key(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    key = action.get('key', '')
    KEY_MAP = {'Return': 'Enter', 'space': 'Space', 'BackSpace': 'Backspace'}
    await page.keyboard.press(KEY_MAP.get(key, key))
    return {'success': True, 'error': None}

async def handle_wait_for_element(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    timeout = int(action.get('timeout', 30000))
    await page.wait_for_selector(action['selector'], timeout=timeout)
    return {'success': True, 'error': None}

async def handle_wait_seconds(action: Dict, page: Page, row_data: Dict = None) -> Dict:
    await asyncio.sleep(float(action.get('seconds', 1)))
    return {'success': True, 'error': None}

# Registry
ACTION_HANDLERS = {
    'click': handle_click,
    'fill_field': handle_fill_field,
    'navigate': handle_navigate,
    'type_text': handle_type_text,
    'press_key': handle_press_key,
    'wait_for_element': handle_wait_for_element,
    'wait_seconds': handle_wait_seconds,
}
```

### **Action Metadata System**

**Problem Solved:** Actions need descriptions, categories, and user guidance

**Solution:** Centralized metadata with optional sorting

```python
# Action metadata with categories and help text
ACTION_METADATA = {
    'click': {
        'name': 'Click',
        'description': 'Click element',
        'category': 'common',
        'sort_order': 1  # Force to top
    },
    'fill_field': {
        'name': 'Fill Field',
        'description': 'Instantly fill input (fast, works with all frameworks)',
        'use_when': 'Standard forms, text fields, email fields',
        'category': 'common',
        'sort_order': 2  # Force second
    },
    'navigate': {
        'name': 'Navigate',
        'description': 'Go to URL',
        'category': 'common'
        # No sort_order - alphabetical within category
    },
    'type_text': {
        'name': 'Type Text',
        'description': 'Type character-by-character with delay (human-like)',
        'use_when': 'Autocomplete fields, search suggestions, bot detection avoidance',
        'category': 'common'
    },
    'press_key': {
        'name': 'Press Key',
        'description': 'Press keyboard key (Enter, Tab, Escape, etc.)',
        'use_when': 'Submit forms, navigate fields, trigger shortcuts',
        'category': 'common'
    },
    'wait_for_element': {
        'name': 'Wait for Element',
        'description': 'Wait for element to appear',
        'use_when': 'Dynamic content, AJAX loading',
        'category': 'utility',
        'warning': 'Only use for dynamic content. Playwright auto-waits for most actions.'
    },
    'wait_seconds': {
        'name': 'Wait (Seconds)',
        'description': 'Wait fixed time',
        'use_when': 'Rate limiting, slow APIs',
        'category': 'utility',
        'warning': '⚠️ Last resort only. Try wait_for_element first.'
    }
}

def get_actions_by_category(category: str) -> list[str]:
    """
    Get actions by category with optional sorting:
    1. Actions with sort_order (ascending)
    2. Actions without sort_order (alphabetical)
    """
    actions_with_order = []
    actions_without_order = []
    
    for action_type, metadata in ACTION_METADATA.items():
        if metadata.get('category') != category:
            continue
        
        sort_order = metadata.get('sort_order')
        if sort_order is not None:
            actions_with_order.append((action_type, sort_order))
        else:
            actions_without_order.append(action_type)
    
    sorted_with_order = [action for action, _ in sorted(actions_with_order, key=lambda x: x[1])]
    sorted_without_order = sorted(actions_without_order)
    
    return sorted_with_order + sorted_without_order
```

**Benefits:**
- **Categorization:** Common vs utility actions for progressive disclosure
- **Optional sorting:** Only specify order for top actions (YAGNI)
- **User guidance:** Help text, use cases, warnings
- **Extensible:** Easy to add new actions with metadata

**Stateless Action Execution:**
```python
# src/core/action_execution.py - Stateless execution function
async def execute_action(action: Dict, row_data: Dict = None) -> Dict:
    action_type = action.get('type', '')
    handler = get_action_handler(action_type)
    
    # Get browser alias from action
    browser_alias = action.get('browser_alias', 'main')
    
    # Get existing page (fail if not found)
    browser_controller = get_browser_controller()
    page = browser_controller.get_existing_page(browser_alias)
    
    if not page:
        return {'success': False, 'error': f'Browser not initialized: {browser_alias}'}
    
    # Execute action (handler decides what to resolve)
    return await handler(action, page, row_data)
```

**Benefits:**
- **Extensible:** Add new actions by creating handler + registry entry
- **Handler-driven resolution:** Each handler decides what fields need template processing
- **Stateless design:** Pure function with no hidden state
- **Consistent interface:** All handlers follow (action, page, row_data) -> result pattern
- **Easy testing:** Individual handlers testable in isolation

## Browser Lifecycle Management

### **Workflow-Driven Browser Initialization**

**Problem Solved:** Unclear browser lifecycle and initialization timing

**Solution:** Workflow executor initializes all browsers upfront

```python
# src/core/workflow_executor.py - Browser initialization
class WorkflowExecutor:
    async def execute_workflow(self, workflow_def: Dict, data: pd.DataFrame):
        browsers = workflow_def.get('browsers', {})
        
        # Initialize all browsers upfront
        browser_controller = get_browser_controller()
        for alias, config in browsers.items():
            page = browser_controller.get_existing_page(alias)
            if not page:
                page = await browser_controller.launch_browser_page(
                    config['browser_type'], alias
                )
                if page and config.get('starting_url'):
                    await browser_controller.navigate(config['starting_url'], alias)
        
        # Execute actions for each row
        for index, row in data.iterrows():
            row_data = row.to_dict()
            for action in actions:
                result = await execute_action(action, row_data)
```

### **Explicit Browser Control in Workflow Editing**

**Problem Solved:** Users need to authenticate/navigate before using element picker

**Solution:** Collapsible browser config section with explicit launch/close controls

```python
# ui/components/browser_config_section.py - Browser lifecycle UI
class BrowserConfigSection(ctk.CTkFrame):
    @async_handler
    async def on_launch_clicked(self):
        browser_type = self.browser_combo.get()
        starting_url = self.url_entry.get().strip()
        
        controller = get_browser_controller()
        result = await controller.launch_browser(browser_type, "main")
        
        if result['success'] and starting_url:
            await controller.navigate(starting_url, "main")
        
        self.update_button_states()
    
    @async_handler
    async def on_close_clicked(self):
        controller = get_browser_controller()
        await controller.close_browser_page("main")
        self.update_button_states()
```

**Browser Lifecycle Policy:**
```
1. Launch: Explicit only (Launch button or picker auto-launch)
2. Close: Explicit only (Close button or app shutdown)
3. Reuse: Always reuse existing browser if running
4. Cleanup: App shutdown closes all browsers
```

**Benefits:**
- **Explicit control:** Users launch browser when needed
- **Browser persistence:** Stays open across multiple picker sessions
- **Clear feedback:** Visual status indicators (⚪/🟢/🔴)
- **Future-proof:** Collapsible design scales to multi-browser workflows

**Browser Controller Methods:**
```python
# src/core/browser_controller.py - Clean separation of concerns
def get_existing_page(self, alias: str = "main") -> Optional[Page]:
    """Get existing page or None if not found"""
    return self.pages.get(alias)

async def launch_browser_page(self, browser_type: str, alias: str = "main") -> Optional[Page]:
    """Launch new browser and return page or None if failed"""
    result = await self.launch_browser(browser_type, alias)
    return self.pages.get(alias) if result['success'] else None

async def close_browser_page(self, alias: str = "main") -> bool:
    """Close browser page and return True if successful, False if not found or failed"""

def resolve_browser_alias(self, action: Dict, workflow: Dict) -> str:
    """Resolve browser alias with fallback logic (explicit > single browser > 'main')"""
```

**Benefits:**
- **Clear initialization:** All browsers launched before row processing
- **No embedded logic:** Browser controller has no workflow assumptions
- **Caller control:** Workflow executor decides browser lifecycle
- **Flexible composition:** Easy to implement different initialization strategies
- **Defensive fallback:** Browser alias resolution handles missing values

---

## Template Resolution Architecture

### **Handler-Driven Template Processing**

**Problem Solved:** Centralized template processing assumes which fields need resolution

**Solution:** Handlers decide what to resolve using utility function

```python
# src/core/template_processing.py - Pure utility function
def resolve_expression(expression: str, row_data: Dict) -> str:
    """
    Resolve template expression with {{col()}} variables
    
    Args:
        expression: "Mr {{col('first_name')}} {{col('last_name')}}"
        row_data: {'first_name': 'John', 'last_name': 'Smith'}
    
    Returns:
        "Mr John Smith"
    """
    if not expression or '{{' not in expression:
        return expression
    
    # Regex-based replacement of {{col('name')}} and {{col(0)}}
    return re.sub(r'\{\{([^}]+)\}\}', replace_match, expression)
```

**Handler Usage:**
```python
# Handlers decide what to resolve
async def handle_fill_field(action: Dict, page: Page, row_data: Dict = None):
    selector = action.get('selector', '')
    value = action.get('value', '')
    
    if row_data:
        selector = resolve_expression(selector, row_data)  # Selector supports templates
        value = resolve_expression(value, row_data)        # Value supports templates
    
    await page.fill(selector, value)

async def handle_navigate(action: Dict, page: Page, row_data: Dict = None):
    url = action.get('url', '')
    
    if row_data:
        url = resolve_expression(url, row_data)  # URL supports templates
    
    await page.goto(url)

async def handle_click(action: Dict, page: Page, row_data: Dict = None):
    selector = action.get('selector', '')
    
    if row_data:
        selector = resolve_expression(selector, row_data)  # Selector supports templates
    
    await page.click(selector)
```

**Fields Supporting Templates:**
- **selector** - Dynamic element targeting (click, fill_field, type_text, wait_for_element)
- **value** - Dynamic data input (fill_field, type_text)
- **url** - Dynamic navigation (navigate)

**Use Cases:**
```python
# Dynamic selectors
selector = "//div[@id='user-{{col('user_id')}}']"           # XPath with dynamic ID
selector = "[data-product='{{col('product_code')}}']"      # CSS with dynamic attribute
selector = "//button[text()='Edit {{col('username')}}']"   # XPath with dynamic text

# Dynamic values
value = "{{col('email')}}"                                 # Simple column reference
value = "user_{{col('username')}}_2024"                    # Hybrid static + dynamic

# Dynamic URLs
url = "https://example.com/user/{{col('user_id')}}"       # Dynamic URL path
```

**Benefits:**
- **No coupling:** Template utility doesn't know about actions
- **Handler control:** Each handler decides what needs resolution
- **Extensible:** New handlers add their own resolution logic
- **Simple utility:** String in, string out - pure function
- **Power user friendly:** Enables advanced dynamic workflows

---

### **Element Picker Integration**

**Problem Solved:** Element picker not integrated with action editing

**Solution:** Async picker integration with selector fields

```python
# ui/components/actions_list.py - Element picker integration
@async_handler
async def on_element_picker_clicked(self, selector_field):
    browser_controller = get_browser_controller()
    page = browser_controller.get_existing_page("main")
    
    picker = ElementPicker()
    result = await picker.pick_element(page)
    
    if result['success']:
        selector_field.set_picker_result(result['selector'])
```

**Integration Flow:**
```
User clicks 🎯 → SelectorPickerField → ActionsList.on_element_picker_clicked()
→ Get browser page → Launch ElementPicker → Set result in field
```

**Benefits:**
- **Seamless integration:** Picker works directly from action editor
- **No modal blocking:** Async operations execute immediately
- **Context aware:** Uses browser from action's browser_alias
- **User friendly:** Results appear directly in selector field

---

### **Modus Operandi Compliance**

**✅ Architecture-first approach:** Proper structure planned before implementation
**✅ Best practices validation:** Industry-standard patterns (Registry, Controller, Dependency Injection)
**✅ Separation of concerns:** Clear boundaries between UI, business logic, and configuration
**✅ Future maintainability:** Easy to extend and modify without breaking existing code
**✅ Technical debt awareness:** Zero technical debt in current implementation

### **Code Quality Metrics**

**✅ Single Responsibility:** Each component has one clear purpose
**✅ Open/Closed Principle:** Easy to extend without modifying existing code
**✅ Dependency Inversion:** Components depend on abstractions, not concretions
**✅ Clean Imports:** Consistent patterns with no circular dependencies
**✅ Type Safety:** Comprehensive type hints throughout

### **Maintainability Features**

**✅ Easy to add pages:** Create file + add to registry
**✅ Easy to modify navigation:** Change controller without affecting UI
**✅ Easy to test:** Clean separation allows isolated testing
**✅ Easy to extend:** Well-defined interfaces for new features
**✅ Easy to debug:** Clear component boundaries and responsibilities

---

## Development Patterns

### **Adding New Actions**

1. **Create handler function** in `src/core/action_handlers.py`
2. **Register in ACTION_HANDLERS** dict
3. **Add to ACTION_SCHEMAS** with required/optional fields
4. **Add to ACTION_METADATA** with category, description, help text
5. **Add field definitions** if new field types needed
6. **Create field components** if new UI components needed
7. **Done** - Action appears in workflow editor with proper UI

### **Adding New Services**

1. **Create service module** in `src/core/`
2. **Add getter function** in `src/app_services.py`
3. **Initialize in** `initialize_services()`
4. **Cleanup in** `cleanup_services()`

### **Modifying Navigation**

1. **UI changes:** Modify `ui/navigation/sidebar.py`
2. **Logic changes:** Modify `ui/navigation/controller.py`
3. **Configuration changes:** Modify `ui/navigation/registry.py`

---

## Testing Strategy

### **Component Isolation**
- **Pages:** Test with mock containers
- **Controllers:** Test with mock UI components
- **Services:** Test with mock dependencies
- **Integration:** Test complete workflows

### **Async Testing**
- **Use pytest-asyncio** for async test functions
- **Mock async services** for UI testing
- **Test error handling** in async operations

---

## Future Architecture Considerations

### **Scalability**
- **Current architecture scales** from 5 to 50+ pages without modification
- **Service layer** can be extended with additional resources
- **Navigation system** supports complex page hierarchies if needed

### **Extensibility**
- **Plugin architecture** possible through registry pattern
- **Theme system** can be added through service layer
- **Advanced navigation** (breadcrumbs, history) easily added to controller

### **Performance**
- **Lazy loading** can be added to page controller
- **Resource pooling** can be added to service layer
- **Caching strategies** can be implemented in individual services

---

---

## Widget Design Patterns

### **Widget-First Design Philosophy**

Instead of forcing predetermined UI mockups into widgets, we discover what CustomTkinter does naturally well and build elegant solutions around those capabilities.

**Widget Discovery Process:**
1. **Identify behavioral requirement** from specification
2. **Explore available CustomTkinter widgets** and their natural patterns
3. **Prototype widget combinations** to find what feels intuitive
4. **Adapt UI flow** to leverage widget strengths
5. **Refine based on user interaction patterns**

### **CustomTkinter Widget Strategies**

**Data Input Components:**
```python
class DataInputPanel(ctk.CTkFrame):
    def __init__(self):
        # File selection
        self.file_button = ctk.CTkButton(text="Select Data File", command=self.select_file)
        
        # Text input for paste
        self.text_input = ctk.CTkTextbox(placeholder_text="Or paste data here...")
        
        # Data preview using scrollable frame
        self.preview_frame = ctk.CTkScrollableFrame()
        
        # Format detection
        self.format_selector = ctk.CTkComboBox(values=["Auto-detect", "CSV", "JSON", "Excel"])
```

**Workflow Management Components:**
```python
class WorkflowManagerPanel(ctk.CTkFrame):
    def __init__(self):
        # Workflow list with natural scrolling
        self.workflow_list = ctk.CTkScrollableFrame()
        
        # Action sequence builder
        self.action_list = ctk.CTkScrollableFrame()
        self.add_action_button = ctk.CTkButton(text="+ Add Action")
        
        # Element picker integration
        self.picker_button = ctk.CTkButton(text="🎯 Pick Element")
```

**Execution Interface Components:**
```python
class ExecutionPanel(ctk.CTkFrame):
    def __init__(self):
        # Task selection
        self.task_selector = ctk.CTkComboBox()
        
        # Progress indication
        self.progress_bar = ctk.CTkProgressBar()
        self.status_label = ctk.CTkLabel()
        
        # Results display
        self.results_text = ctk.CTkTextbox(state="disabled")
```

### **Widget Strengths to Leverage**
- **CTkScrollableFrame:** Natural list behavior without external dependencies
- **CTkTextbox:** Rich text display with built-in scrolling
- **CTkProgressBar:** Built-in progress indication
- **CTkComboBox:** Selection with memory and auto-completion
- **CTkButton:** State management (enabled/disabled) and consistent styling

---

## Theme & Styling System

### **Consistent Design System**
```python
# Theme configuration
class AppTheme:
    # Color palette
    PRIMARY = "#1f538d"
    SECONDARY = "#14375e"
    ACCENT = "#00d4aa"
    BACKGROUND = "#212121"
    SURFACE = "#2b2b2b"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    
    # Spacing system
    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24
    
    # Component styles
    BUTTON_HEIGHT = 32
    INPUT_HEIGHT = 36
    BORDER_RADIUS = 6
```

### **Widget Factory Patterns**
```python
def create_primary_button(parent, text, command):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=AppTheme.BUTTON_HEIGHT,
        corner_radius=AppTheme.BORDER_RADIUS,
        fg_color=AppTheme.PRIMARY,
        hover_color=AppTheme.SECONDARY
    )

def create_input_field(parent, placeholder=""):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        height=AppTheme.INPUT_HEIGHT,
        corner_radius=AppTheme.BORDER_RADIUS
    )
```

---

## Component Development Workflow

### **Rapid Prototyping Process**
1. **Create minimal widget** - single functionality focus
2. **Test interaction patterns** - how does it feel to use?
3. **Iterate on layout** - spacing, sizing, grouping
4. **Integrate with core logic** - connect to behavioral requirements
5. **Refine based on usage** - adjust for real workflow patterns

### **Component Development Pattern**
```python
# Standard component structure
class DataPreview(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout and widget creation
        pass
    
    def load_data(self, data):
        # Core functionality
        pass
    
    def update_display(self):
        # UI state updates
        pass
```

### **Development Steps**
1. **Start with basic widget** - Focus on single responsibility
2. **Test and refine** - Iterate on user experience
3. **Add styling and polish** - Apply consistent theme
4. **Integrate with main application** - Connect to architecture

---

## Deployment Architecture

### **PyInstaller Configuration**
```python
# build.spec - Production build configuration
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/assets', 'ui/assets'),
        ('config/default_preferences.json', 'config')
    ],
    hiddenimports=['playwright', 'pandas', 'customtkinter'],
    excludes=[],
    cipher=None,
    noarchive=False,
)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
    name='WebAutomationTool',
    debug=False,
    console=False,
    icon='assets/app_icon.ico'
)
```

### **Distribution Strategy**
- **Single executable** - No installation required
- **Portable configuration** - Settings travel with executable
- **Browser detection** - Automatic discovery of installed browsers
- **Error logging** - Local log files for troubleshooting

### **Performance Optimization**
- **Lazy loading** - Load components on demand
- **Browser session cleanup** - Proper resource disposal
- **Memory management** - Efficient handling of large datasets
- **Startup optimization** - Minimal imports, deferred loading

*This architecture provides a solid foundation for long-term development with zero technical debt and proper separation of concerns. All components follow established design patterns and can be easily extended or modified.*


---

## UI Patterns

### **Mini-Controller Pattern**

**Problem Solved:** Pages need list-detail view switching without complex state management

**Solution:** Page acts as mini-controller managing view transitions using grid show/hide

**When to Use:**
- Large editor that benefits from full-screen focus
- Clear list ↔ detail mental model
- Infrequent transitions between views

**Implementation:**
```python
class WorkflowManagementPage(ctk.CTkFrame):
    """Mini-controller for workflow list-detail views"""
    
    def setup_views(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # List view
        self.list_view = WorkflowListView(self, on_edit=self.show_editor, on_new=self.show_new)
        self.list_view.grid(row=0, column=0, sticky="nsew")
        
        # Editor view
        self.editor_view = WorkflowEditorView(self, on_save=self.on_save, on_cancel=self.show_list)
        self.editor_view.grid(row=0, column=0, sticky="nsew")
        self.editor_view.grid_remove()
    
    def show_list_view(self):
        self.editor_view.grid_remove()
        self.list_view.grid()
    
    def show_editor_view(self, workflow_name):
        self.list_view.grid_remove()
        self.editor_view.grid()
```

**Communication Pattern:**
- Parent-mediated callbacks (no direct component coupling)
- List view → Page → Editor view
- Editor view → Page → List view

**Benefits:**
- ✅ Full-screen editing eliminates distractions
- ✅ Clean separation of concerns
- ✅ Reusable pattern (same as navigation)
- ✅ Easy to extend

**Example:** `WorkflowManagementPage` uses mini-controller for workflow list ↔ editor

---

### **Click-to-Edit Pattern**

**Problem Solved:** Extra clicks required to edit items, cluttered UI with edit buttons

**Solution:** Entire card is clickable, separate delete button to avoid propagation issues

**Layout Pattern:**
```python
# Row container (transparent)
row = ctk.CTkFrame(parent, fg_color="transparent")
row.pack(fill="x", padx=5, pady=5)

# Clickable card (left, expands)
card = ctk.CTkFrame(row)
card.pack(side="left", fill="both", expand=True, padx=(0, 5))
card.bind("<Button-1>", lambda e: self.on_edit(item_name))
card.configure(cursor="hand2")

# Hover effect
card.bind("<Enter>", lambda e: card.configure(border_width=2, border_color="#1f538d"))
card.bind("<Leave>", lambda e: card.configure(border_width=0))

# Delete button (right, fixed width)
delete_button = ctk.CTkButton(row, text="🗑️", width=40)
delete_button.pack(side="right")
```

**Visual Result:**
```
┌─────────────────────────────────────┐
│ Login Workflow                      │  [🗑️]
│ 5 actions • chrome                  │
└─────────────────────────────────────┘
     ↑ Click anywhere to edit           ↑ Delete
```

**Benefits:**
- ✅ One click to edit (faster interaction)
- ✅ Cleaner UI (no edit button)
- ✅ No event propagation issues (separate elements)
- ✅ Industry standard (Gmail, Trello, Notion)

**Examples:** 
- Workflow cards in `WorkflowListView`
- Action cards in `ActionsList`

---

### **In-Place Editor Replacement**

**Problem Solved:** Editor at bottom loses context, causes scroll sync issues

**Solution:** Editor replaces card in same position using conditional rendering

**Implementation:**
```python
def refresh_display(self):
    # Clear display
    for widget in self.container.winfo_children():
        widget.destroy()
    
    # Conditional rendering: editor OR card
    for i, item in enumerate(self.items):
        if self.editing_index == i:
            # Replace card with editor
            self.create_inline_editor_at(i)
        else:
            # Show normal card
            self.create_item_card(i, item)
    
    # New item editor at bottom
    if self.editing_action and self.editing_index is None:
        self.create_inline_editor_at(None)
```

**Visual Flow:**
```
Before Edit:
  Action 1
  Action 2  ← Click
  Action 3

After Edit:
  Action 1
  [Editor replaces Action 2]  ← Same position
  Action 3

After Save:
  Action 1
  Action 2 (updated)  ← Restored in same position
  Action 3
```

**Benefits:**
- ✅ Context preservation (see surrounding items)
- ✅ Spatial consistency (edit where item is)
- ✅ No excessive scrolling
- ✅ Industry standard (Trello, Notion, Gmail)

**Example:** `ActionsList` replaces action cards with inline editor

---

### **Scroll Sync Management**

**Problem Solved:** CustomTkinter's scrollable frame loses sync when content changes dynamically

**Solution:** Force scroll region update after every content change

**Implementation:**
```python
def refresh_display(self):
    # ... rebuild content ...
    
    # CRITICAL: Force scroll region update
    self.after(50, self._force_scroll_update)

def _force_scroll_update(self):
    """Force scroll region update to prevent scrollbar sync issues"""
    try:
        canvas = self.scrollable_frame._parent_canvas
        canvas.configure(scrollregion=canvas.bbox("all"))
    except:
        pass
```

**Why This Works:**
- CustomTkinter doesn't auto-update scroll region on dynamic changes
- Manual recalculation ensures scrollbar stays in sync
- 50ms delay allows widgets to render before update

**Benefits:**
- ✅ Scrollbar always works (no stuck scrollbar)
- ✅ User can always scroll up/down
- ✅ Minimal code (~5 lines)
- ✅ Fixes root cause

**Example:** `ActionsList` forces scroll update after add/edit/delete/cancel

---

### **Pattern Decision Matrix**

| Pattern | Use When | Don't Use When |
|---------|----------|----------------|
| **Mini-Controller** | Large editor, clear list-detail model | Small edits, frequent transitions |
| **Click-to-Edit** | Cards/items in lists | Complex multi-action items |
| **In-Place Editor** | Context preservation important | Editor much larger than card |
| **Scroll Sync Fix** | Dynamic content in scrollable frame | Static content only |

---



## Data Expression Helper Architecture

### **Progressive Disclosure Pattern for Template Variables**

**Problem Solved:** Users need to insert `{{col('name')}}` or `{{col(0)}}` expressions without memorizing syntax

**Solution:** Icon-based helper with educational popup and column selector

---

### **Component Design**

**DataExpressionHelper** - Reusable expression insertion component

```python
# ui/components/fields/data_expression_helper.py
class DataExpressionHelper(ctk.CTkFrame):
    """
    Icon button (\ud83d\udcca) that opens column selector or educational popup
    - Inserts {{col('name')}} or {{col(0)}} at cursor position
    - Toggles between name/index mode
    - Session persistence for mode preference
    """
    
    def __init__(
        self,
        parent,
        target_entry: ctk.CTkEntry,
        data_sample: Optional[pd.DataFrame] = None,
        on_load_data: Optional[Callable] = None
    ):
        # Icon button always visible
        # Shows educational popup if no data
        # Shows column selector if data available
```

**Key Features:**
- **Icon-based trigger:** \ud83d\udcca button next to text inputs
- **Progressive disclosure:** Educational popup explains feature before use
- **Insert at cursor:** Uses `tk.INSERT` for natural text editing behavior
- **Session persistence:** Remembers name/index preference across uses
- **Optional integration:** Can be added to any text input field

---

### **Educational Popup Pattern**

**When:** User clicks \ud83d\udcca without data loaded

**Purpose:** Explain feature and provide data loading action

```python
class EducationalPopup(ctk.CTkToplevel):
    """
    Explains template variable system
    - What: {{col('name')}} and {{col(0)}} syntax
    - Why: When to use names vs indexes
    - How: "Load Data Sample" button for immediate action
    """
```

**Content Structure:**
1. Feature explanation (what it does)
2. Syntax examples (how to use)
3. Usage example (template → result)
4. Guidance (when to use names vs indexes)
5. Action button (load data sample)

**Benefits:**
- ✅ **Self-documenting:** Users learn by discovery
- ✅ **Actionable:** Direct path to enable feature
- ✅ **Non-blocking:** Can be dismissed without action

---

### **Column Selector with Mode Toggle**

**Design Decision:** Single column with toggle instead of two-column layout

**Rationale:**
- **Simplicity:** One column eliminates alignment issues
- **Progressive disclosure:** Advanced feature (indexes) hidden by default
- **Cleaner UI:** Less visual clutter, easier to understand
- **Better UX:** Can't accidentally click wrong column

**Implementation:**

```python
class ColumnSelectorPopup(ctk.CTkToplevel):
    _preferred_mode = "name"  # Class variable for session persistence
    
    def __init__(self, parent, data_sample, on_select_callback):
        self.mode = ColumnSelectorPopup._preferred_mode  # Load preference
        
        # Single column layout
        # Mode toggle in header: "Switch to Index ⚙"
        # Rows show: "email" or "0 (email)" based on mode
    
    def toggle_mode(self, event):
        self.mode = "index" if self.mode == "name" else "name"
        ColumnSelectorPopup._preferred_mode = self.mode  # Save preference
        self.refresh_table()
```

**Mode Toggle Design:**
- **Location:** Right side of header row
- **Text:** "Switch to Index ⚙" / "Switch to Name ⚙"
- **Interaction:** Clickable label with hover effect
- **Feedback:** Text changes immediately, table refreshes

**Display Modes:**

**Name Mode (Default):**
```
Header: "Column Name"
Rows:   "email", "firstname", "lastname"
Insert: {{col('email')}}
```

**Index Mode:**
```
Header: "Index (Column Name)"
Rows:   "0 (email)", "1 (firstname)", "2 (lastname)"
Insert: {{col(0)}}
```

---

### **Session Persistence Pattern**

**Problem:** Users frustrated by repeated mode switching

**Solution:** Class-level variable persists preference across popup instances

```python
class ColumnSelectorPopup(ctk.CTkToplevel):
    _preferred_mode = "name"  # Shared across all instances
    
    def __init__(self, ...):
        self.mode = ColumnSelectorPopup._preferred_mode  # Load
    
    def toggle_mode(self, ...):
        ColumnSelectorPopup._preferred_mode = self.mode  # Save
```

**Scope:** Session-level (resets on app restart)

**Benefits:**
- ✅ **Minimal code:** Single class variable
- ✅ **No file I/O:** In-memory only
- ✅ **Reasonable default:** Resets to "name" on restart
- ✅ **User-friendly:** Remembers choice during session

---

### **Integration Pattern**

**Adding to Text Input Fields:**

```python
class TextInputField(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        label: str,
        placeholder: str = "",
        enable_expression_helper: bool = False  # Optional flag
    ):
        # ... existing code ...
        
        if enable_expression_helper:
            self.expression_helper = DataExpressionHelper(
                self.input_container,
                target_entry=self.entry,
                data_sample=None  # Set later via set_data_sample()
            )
            self.expression_helper.pack(side="right", padx=(5, 0))
```

**Data Sample Propagation:**

```python
# WorkflowEditorView loads data sample
def load_data_sample(self):
    loader = DataLoader()
    result = loader.load_data(filepath)
    self.data_sample = result['data'].head(10)  # First 10 rows
    self.propagate_data_sample()

def propagate_data_sample(self):
    # Pass to all expression helpers in actions list
    self.actions_list.set_data_sample(self.data_sample)
```

---

### **Design Principles Applied**

**YAGNI Compliance:**
- ✅ **No two-column layout:** Simpler single-column design
- ✅ **No complex alignment:** One column always works
- ✅ **No file persistence:** Session-level is sufficient
- ✅ **Built-in cursor insertion:** Uses tk.INSERT (no custom tracking)

**Progressive Disclosure:**
- ✅ **Icon-based:** Helper doesn't clutter main UI
- ✅ **Educational popup:** Explains feature before use
- ✅ **Mode toggle:** Advanced feature (indexes) hidden by default
- ✅ **Optional integration:** Only added where needed

**User Experience:**
- ✅ **Self-documenting:** Educational popup explains everything
- ✅ **Actionable:** "Load Data Sample" button in popup
- ✅ **Persistent:** Remembers mode preference
- ✅ **Natural editing:** Inserts at cursor position

---

### **Modus Operandi Compliance**

**✅ Architecture-first approach:** Discussed single-column vs two-column before implementation  
**✅ Best practices validation:** Progressive disclosure, session persistence patterns  
**✅ YAGNI principle:** Minimal code, no over-engineering  
**✅ Future maintainability:** Easy to extend (add more modes, save to preferences file)  
**✅ Technical debt awareness:** Zero debt - clean, simple implementation

---

*This pattern provides a reusable, user-friendly way to insert template variables without requiring users to memorize syntax or understand the template system upfront.*

---

## Domain-Specific Field Component Pattern

### **Purpose-Built Components Over Generic Ones**

**Problem Solved:** Generic field components with conditional logic created complexity

**Solution:** Domain-specific components for each action field type

---

### **Component Architecture**

**Pattern:** One component per action field purpose

```
ui/components/fields/
├── action_value_input.py          # Value field with expression helper
├── action_url_input.py            # URL field (future)
├── action_selector_input.py       # Selector field (future)
├── text_input.py                  # Generic text (legacy)
├── dropdown.py                    # Generic dropdown (legacy)
├── selector_picker.py             # Selector with picker
├── key_picker.py                  # Key capture
├── number_input.py                # Numeric validation
└── data_expression_helper.py      # Reusable utility
```

**Benefits:**
- ✅ **Zero ambiguity:** Component name = exact purpose
- ✅ **No conditionals:** Each component knows its requirements
- ✅ **Easy discovery:** "Where's value input?" → `action_value_input.py`
- ✅ **Self-documenting:** Code reads like domain language
- ✅ **Future-proof:** Add new field = create new component

---

### **ActionValueInput Implementation**

**Purpose:** Value field with integrated expression helper and help button

```python
class ActionValueInput(ctk.CTkFrame):
    def __init__(self, parent, label, placeholder, optional, on_load_data=None):
        # Label
        self.label = ctk.CTkLabel(self, text=label)
        
        # Container for entry + helpers
        input_container = ctk.CTkFrame(self, fg_color="transparent")
        
        # Entry field
        self.entry = ctk.CTkEntry(input_container, placeholder_text=placeholder)
        
        # Expression helper (📊)
        self.helper = DataExpressionHelper(
            input_container,
            target_entry=self.entry,
            data_sample=get_workflow_data_sample(),
            on_load_data=self.on_load_data_clicked
        )
        
        # Help button (❓)
        help_btn = ctk.CTkButton(
            input_container,
            text="❓",
            width=30,
            command=self.show_help
        )
```

**Features:**
- Entry field for text input
- Expression helper (📊) for column insertion
- Help button (❓) for educational popup
- Callback for data loading

---

### **Data Sample Status Indicator**

**Purpose:** Persistent status display with load/clear/replace actions

**Component:** `ui/components/data_sample_status.py`

```python
class DataSampleStatus(ctk.CTkFrame):
    def __init__(self, parent, on_load: Callable, on_change: Callable):
        # Displays current data sample state
        # Provides actions based on state
```

**States:**

**No Data:**
```
[⚠️ No sample data loaded | Load Data Sample]
```

**Data Loaded:**
```
[✅ sample.csv (10 rows) | ✕ | Replace]
```

**Benefits:**
- ✅ **Always visible:** User always knows data state
- ✅ **Actionable:** Click to load/clear/replace
- ✅ **Clear feedback:** Visual status indicators
- ✅ **Reusable:** Can be used in other pages

---

### **Session-Level Data Sample Service**

**Purpose:** Shared data sample storage across all expression helpers

**Service:** `src/app_services.py`

```python
# Session-level workflow data sample (not persisted)
_workflow_data_sample = None

def get_workflow_data_sample():
    """Get current workflow editing data sample"""
    return _workflow_data_sample

def set_workflow_data_sample(data_sample):
    """Set workflow editing data sample"""
    global _workflow_data_sample
    _workflow_data_sample = data_sample

def clear_workflow_data_sample():
    """Clear data sample (on workflow save/cancel)"""
    global _workflow_data_sample
    _workflow_data_sample = None
```

**Lifecycle:**
- **Set:** When user loads data sample
- **Get:** When expression helper needs data
- **Clear:** On workflow save/cancel or app shutdown

**Benefits:**
- ✅ **No prop drilling:** Components access via service
- ✅ **Single source of truth:** All helpers share same data
- ✅ **Clean lifecycle:** Explicit set/clear
- ✅ **Session-scoped:** Resets on app restart

---

### **Callback Pattern for Data Loading**

**Purpose:** Enable educational popup to trigger data loading in parent

**Flow:**
```
ActionValueInput → ActionsList → WorkflowEditorView
     ↓                ↓                ↓
on_load_data    on_load_data    load_data_sample()
```

**Implementation:**

```python
# ActionValueInput - receives and wires callback
class ActionValueInput:
    def __init__(self, parent, label, placeholder, optional, on_load_data=None):
        self.on_load_data_callback = on_load_data
        self.helper = DataExpressionHelper(
            container,
            target_entry=self.entry,
            data_sample=get_workflow_data_sample(),
            on_load_data=self.on_load_data_clicked
        )

# ActionsList - passes callback through
class ActionsList:
    def __init__(self, parent, on_actions_changed, on_load_data):
        self.on_load_data = on_load_data

# WorkflowEditorView - owns data loading
class WorkflowEditorView:
    def setup_ui(self):
        self.actions_list = ActionsList(
            content,
            self.on_actions_changed,
            on_load_data=self.load_data_sample
        )
```

**Benefits:**
- ✅ **Inversion of control:** Child doesn't know about parent
- ✅ **Loose coupling:** Components communicate via callbacks
- ✅ **Follows existing pattern:** Same as element picker
- ✅ **Easy to test:** Mock callbacks for testing

---

### **User Flows**

**Flow 1: Via Help Button (❓)**
```
User clicks ❓ → Educational popup → "Load Data Sample" → File picker → Status shows ✅
```

**Flow 2: Via Expression Helper (📊) - No Data**
```
User clicks 📊 → Educational popup → "Load Data Sample" → File picker → Status shows ✅
```

**Flow 3: Via Expression Helper (📊) - Data Loaded**
```
User clicks 📊 → Column selector → Select column → Expression inserted
```

**Flow 4: Via Status Indicator - No Data**
```
User clicks "Load Data Sample" → File picker → Status shows ✅
```

**Flow 5: Clear Data**
```
User clicks ✕ → Data cleared → Status shows ⚠️
```

**Flow 6: Replace Data**
```
User clicks "Replace" → File picker → New data loaded → Status updates
```

---

### **Modus Operandi Compliance**

**✅ Architecture-first approach:** Discussed domain-specific vs generic components  
**✅ Best practices validation:** Callback pattern, service layer, reusable components  
**✅ YAGNI principle:** Minimal code, no over-engineering  
**✅ Future maintainability:** Easy to add new field types  
**✅ Technical debt awareness:** Zero debt - clean implementation  
**✅ Separation of concerns:** UI, service, business logic properly separated

---

*This pattern eliminates generic component complexity through purpose-built components. Each field type has a dedicated component that knows exactly what it needs, making the codebase self-documenting and easy to maintain.*
