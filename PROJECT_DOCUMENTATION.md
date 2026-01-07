# Web Automation Tool - Project Documentation

## Project Overview

**Purpose:** Desktop application that allows non-technical users to automate repetitive browser tasks without requiring development skills.

**Target Users:** General consumers with no development insight who need to automate web browser tasks they cannot handle on their own.

**Core Use Case:** Users need to iterate through 30-150 rows of data and enter them into web forms - manual overhead that becomes a lifesaver when automated.

## Technical Stack - FINAL DECISIONS

**Core Technologies:**
- **Language:** Python 3.11+
- **UI Framework:** PyQt6 (modern, professional interface)
- **Browser Automation:** Playwright (multi-browser support, dev tools integration)
- **Data Processing:** Pandas (format-agnostic data handling)
- **Packaging:** PyInstaller (standalone executable)
- **Distribution:** Small downloader → Full application bundle

**Deployment Strategy:**
- Users download small launcher (~5-10MB)
- Launcher downloads main application bundle (~150-200MB)
- Playwright browsers downloaded/managed automatically
- Zero Python installation required from users
- Only requirement: At least one supported browser (Chrome, Firefox, Edge)

## Application Architecture

```
WebAutomationTool/
├── src/
│   ├── core/
│   │   ├── automation_engine.py      # Processes JSON configs
│   │   ├── browser_controller.py     # Playwright wrapper
│   │   ├── element_selector.py       # Dev tools-like element picker
│   │   └── data_handler.py          # Excel/CSV processing
│   ├── ui/
│   │   ├── main_window.py           # Primary application window
│   │   ├── automation_builder.py    # Visual automation creator
│   │   ├── element_picker.py        # UI for element selection
│   │   └── data_import.py           # Data source configuration
│   ├── models/
│   │   ├── automation_config.py     # JSON schema validation
│   │   └── step_types.py           # Step definitions (click, input, wait, etc.)
│   ├── utils/
│   │   ├── file_manager.py         # Save/load/export automations
│   │   └── browser_detector.py     # Detect installed browsers
│   └── main.py                     # Application entry point
├── automations/                    # User's saved automation JSONs
├── data/                          # Imported CSV/Excel files
└── config/                        # App settings
```

## Core Concepts

### Tasks (Automation Templates)
- **Tasks are reusable templates** that define a sequence of actions
- Users create tasks once and reuse them with different data files
- Tasks are stored as JSON configuration files
- Tasks define WHAT to do, not WHICH data to use

### Data Sources (Runtime Input)
- Users load different data files each time they execute a task
- Supported formats: CSV, Excel (.xlsx), JSON, YAML
- Data is processed through Pandas for format-agnostic handling
- Each execution can use different data with the same task template

## JSON Automation Schema

```json
{
  "name": "Contact Form Entry",
  "version": "1.0",
  "description": "Enters contact information into web form",
  "initialization": [
    {
      "type": "open_browser",
      "alias": "main",
      "browser": "chrome",
      "description": "Open primary browser for data entry"
    },
    {
      "type": "navigate",
      "browser": "main",
      "url": "https://example.com/login"
    },
    {
      "type": "pause",
      "message": "Please log in and click Continue when ready"
    }
  ],
  "pre_loop_actions": [
    {
      "type": "click",
      "browser": "main",
      "selector": "#start-button",
      "description": "Click start button before processing data"
    }
  ],
  "loop_actions": [
    {
      "type": "set_value",
      "browser": "main",
      "selector": "input[name='name']",
      "value": "{{row.name.Name}}",
      "description": "Enter contact name from data"
    },
    {
      "type": "set_value",
      "browser": "main",
      "selector": "input[name='email']", 
      "value": "{{row.name.Email}}",
      "default": "no-email@example.com",
      "description": "Enter email from data with fallback"
    },
    {
      "type": "click",
      "browser": "main",
      "selector": "#submit-btn",
      "description": "Submit the form"
    }
  ],
  "post_loop_actions": [
    {
      "type": "click",
      "browser": "main",
      "selector": "#finish-button",
      "description": "Click finish after all data processed"
    }
  ]
}
```

### Multi-Browser Example (Future)

```json
{
  "name": "Cross-Browser Data Processing",
  "initialization": [
    {
      "type": "open_browser",
      "alias": "scraper",
      "browser": "chrome",
      "description": "Browser for data extraction"
    },
    {
      "type": "open_browser",
      "alias": "uploader",
      "browser": "firefox",
      "description": "Browser for data submission"
    },
    {
      "type": "pause",
      "message": "Please authenticate in both browsers, then continue"
    }
  ],
  "loop_actions": [
    {
      "browser": "scraper",
      "type": "navigate",
      "url": "{{row.name.source_url}}"
    },
    {
      "browser": "scraper",
      "type": "extract",
      "selector": ".price-value",
      "save_as": "extracted_price"
    },
    {
      "browser": "uploader",
      "type": "navigate",
      "url": "{{row.name.target_url}}"
    },
    {
      "browser": "uploader",
      "type": "set_value",
      "selector": "#price-field",
      "value": "{{extracted.extracted_price}}"
    }
  ]
}
```

## Template Variable System

### Template Syntax
**Template Detection:** Any value containing `{{...}}` is treated as a template expression
**Static Values:** Plain text without `{{...}}` is used as-is
**Hybrid Values:** Mix of static text and templates: `"user-{{row_name('Email')}}-2024"`

### Data Access Methods
**Column by Name:**
- Template: `{{row_name('Email')}}`
- Usage: Most common, readable, self-documenting
- Example: `{{row_name('FirstName')}}`, `{{row_name('user.contact.email')}}` (flattened JSON)

**Column by Index:**
- Template: `{{row_index(0)}}`
- Usage: When column names change or are unreliable
- Example: `{{row_index(0)}}` (first column), `{{row_index(3)}}` (fourth column)
- Note: Uses 0-based indexing matching pandas DataFrame structure

### Template Implementation
**Regex-based Processing:**
```python
import re
TEMPLATE_PATTERN = re.compile(r'\{\{([^}]+)\}\}')

def is_template(value):
    return bool(TEMPLATE_PATTERN.search(str(value)))

def evaluate_template(value, df, row_index):
    if not is_template(value):
        return value  # Static value, return as-is
    
    def replace_template(match):
        template = match.group(1).strip()
        return str(resolve_template_expression(template, df, row_index))
    
    return TEMPLATE_PATTERN.sub(replace_template, str(value))
```

**Direct Pandas Integration:**
```python
def resolve_template_expression(template, df, row_index):
    if template.startswith("row_name('") and template.endswith("')"):
        column_name = template[10:-2]  # Extract column name
        return df.at[row_index, column_name]
    
    elif template.startswith('row_index(') and template.endswith(')'):
        col_index = int(template[10:-1])  # Extract index
        return df.iloc[row_index, col_index]
```

### Template Examples
**Simple Data References:**
```json
{
  "type": "set_value",
  "selector": "#email",
  "value": "{{row_name('Email')}}",
  "default": "no-email@example.com"
}
```

**Hybrid Templates:**
```json
{
  "type": "set_value",
  "selector": "#user-id",
  "value": "user-{{row_name('Email')}}-{{row_index(0)}}"
}
```

**Complex Nested Data:**
```json
{
  "type": "set_value",
  "selector": "#contact",
  "value": "{{row_name('user.contact.email')}}"
}
```

## Application Pages Structure

**Two-page application with shared template:**

### 1. Task Execution Page (Landing)
- Task selector dropdown (remembers last selected between sessions)
- Data loading area with multiple input methods:
  - File upload button
  - Drag and drop support
  - Copy/paste functionality
- Data preview table (first 5-10 rows)
- Execute button
- Progress/status display during execution

### 2. Task Manager Page (Combined List + Builder)
**Dynamic Layout:**
- **Default State:** Task list takes 100% of vertical space
- **Edit/Create State:** Task list (20%) + Task builder (80%)
- **Auto-scroll:** When builder opens, selected task remains visible in list area

**Task List Section (Top):**
- Table/grid view showing:
  - Task name
  - Description (truncated)
  - Last modified date
  - Last execution status/row count
- Action buttons: Create New, Edit, Delete, Duplicate
- Import/Export functionality in toolbar
- Search/filter capabilities

**Task Builder Section (Bottom - Collapsible):**
- **Opens when:** Click "New Task", "Edit", or "Duplicate"
- **Closes when:** Save task, Cancel, Close button/icon, ESC key
- **Stays open when:** Validation errors (for user correction)
- Action sequence builder with drag-and-drop reordering
- Visual element selector integration
- Data column mapping with sample data support
- Preview/test functionality
- Save/cancel options

## User Experience Flows

## User Experience Flows

### Task Creation Flow
1. User navigates to Task Manager
2. Clicks "Create New Task" (task builder opens in bottom 80%)
3. Enters task name and description
4. Configures setup:
   - **Simple Setup:** Browser selection + URL
   - **Advanced Setup:** Multiple browser sessions with aliases + manual steps
5. Adds actions using progressive disclosure:
   - **Simple Mode:** Dropdown selection for data columns, visual element picker
   - **Advanced Mode:** Full template syntax with hybrid value support
6. Optionally flags task as "does not use data" for single-execution tasks
7. Saves task (builder closes, new task appears in list)

### Action Creation Flow (Simple Mode)
1. User clicks "➕ Add Action" button in task builder
2. **Action Creation Form** opens with fields:
   - **Action Type:** Dropdown (Set Value, Click, Navigate, Wait)
   - **Target Element:** Text field with 🎯 Pick Element button
   - **Value:** Text field (for Set Value actions) or data column dropdown (future)
   - **Description:** Optional description field
3. **Element Selection Process:**
   - User clicks 🎯 Pick Element button → launches browser element picker
   - User hovers and clicks desired element → returns to form
   - Target Element field automatically populated with generated XPath
4. **Form Completion:**
   - User selects action type from dropdown
   - User fills value field (for Set Value actions)
   - User clicks "Add Action" → action added to task actions list
5. **Actions List Display:**
   - Shows numbered list of actions: "1. Click element (high reliability)"
   - Actions can be reordered, edited, or deleted

### Action Creation Form Layout
```
┌─ Add Action ─────────────────────────────────────────────┐
│ Action Type: [Set Value ▼]                              │
│                                                         │
│ Target Element: [//input[@name='email']____] [🎯]      │
│                                                         │
│ Value: [john@example.com________________] [📊]          │
│                                                         │
│ Description: [Enter email address_______] (optional)    │
│                                                         │
│                        [Add Action] [Cancel]            │
└─────────────────────────────────────────────────────────┘
```

### Progressive Disclosure for Actions
**Simple Mode (Default):**
- Action type dropdown with common options
- Target element field with picker button
- Value field with static text input
- Automatic description generation

**Advanced Mode (Future):**
- Full template syntax support in value field
- Data column selection dropdown
- Hybrid value creation (static + template)
- Manual selector editing

### Action Types Implementation
**Set Value Actions:**
- Target Element: Required (XPath selector)
- Value: Required (static text or future template)
- Used for: Input fields, textareas, dropdowns

**Click Actions:**
- Target Element: Required (XPath selector)
- Value: Not used
- Used for: Buttons, links, checkboxes

**Navigate Actions:**
- Target Element: Not used
- Value: Required (URL)
- Used for: Page navigation

**Wait Actions:**
- Target Element: Not used
- Value: Required (duration in seconds)
- Used for: Delays between actions

### Task Execution Flow
1. User selects existing task from dropdown (Task Execution page)
2. **Data Loading (if task requires data):**
   - Unified data area with centered "Load Data" button
   - Drag & drop support
   - Ctrl+V paste support
   - Shows "(X rows loaded, showing first 10)" with real-time processing status
3. **Data-less tasks:** No data loading area shown
4. Clicks Execute → Two-phase execution:
   - **Get Ready:** Launch browser, navigate to URL, wait for user authentication
   - **Run Automation:** Loop through data with real-time progress and color-coded status
5. **Progress Tracking:** Rolling window showing current row ±5 with status colors:
   - ✅ Green: Success
   - ❌ Red: Error  
   - 🔄 Yellow: Processing
   - Default: Pending

## Action Creation UX Details

### Progressive Disclosure Design
**Simple Mode (Default):** Non-technical users get streamlined interface
**Advanced Mode (Optional):** Power users get full template syntax control

### Simple Mode Interface
```
┌─ Action ───────────────────────────────────────────────────────────┐
│ Action Type: [Set Value ▼]                              │
│                                                         │
│ Target Element: [#email-field____________] [🎯]         │
│                                                         │
│ Value: [📊 Select Data Column ▼]                      │
│        Displays as: [📧 Email]  ← Pill/chip display    │
│                                                         │
│ Default Value: [no-email@example.com____] (optional)    │
│                                                         │
│                                    [⚙️ Advanced Mode]   │
└───────────────────────────────────────────────────────────┘
```

### Advanced Mode Interface
```
┌─ Action ───────────────────────────────────────────────────────────┐
│ Action Type: [Set Value ▼]                              │
│                                                         │
│ Target Element: [#email-field____________] [🎯]         │
│                                                         │
│ Value: [user-{{row_name('Email')}}-2024___] [📊]        │
│                                                         │
│ Default Value: [no-email@example.com____] (optional)    │
│                                                         │
│                                    [📝 Simple Mode]     │
└───────────────────────────────────────────────────────────┘
```

### Data Column Selection
**Searchable Dropdown with Filter:**
- **Primary action:** Data column selection (most common use case)
- **Real-time filtering:** Type "emai" to filter columns containing "emai"
- **Fuzzy matching:** Matches partial strings in column names
- **Two access methods:** By name (readable) and by index (reliable)
- **Static value option:** Available at bottom of dropdown
- **0-based indexing:** Consistent with pandas, no conversion needed

### Element Selection
**Target Element Field:**
- **Manual entry:** Users can type CSS selectors, XPath, or other selector formats
- **Visual picker:** 🎯 icon launches browser overlay for point-and-click selection
- **Auto-generated selectors:** Always XPath with reliability prioritization

**XPath Generation Strategy (Visual Picker):**
**Priority Order for Maximum Reliability:**
1. **Testing attributes:** `data-testid`, `data-cy`, `data-test`, `data-automation`, `data-qa`
2. **Semantic attributes:** `name`, `type`, `role`, `aria-label`
3. **Clean IDs/classes:** Only if they don't match auto-generated patterns
4. **Text content:** For buttons/links with stable text
5. **Position-based:** Last resort with user warning

**Auto-Generated Pattern Detection:**
```python
AUTO_GENERATED_PATTERNS = [
    r'.*-\d{4,}$',           # ending with 4+ digits: button-1234
    r'.*_\d{4,}$',           # ending with underscore + digits: field_5678
    r'^[a-f0-9]{8,}$',       # hex strings: a1b2c3d4e5f6
    r'.*-[a-f0-9]{6,}$',     # ending with hex: btn-a1b2c3
    r'.*\d{10,}$',           # long numbers: timestamp-based IDs
    r'^(ember|react|vue)\d+$' # framework-generated: ember123, react456
]
```

**XPath Generation Examples:**
```python
# Priority 1: Testing attributes (most reliable)
"//[@data-testid='submit-form-btn']"
"//[@data-cy='email-input']"

# Priority 2: Semantic attributes
"//input[@name='email']"
"//button[@type='submit']"

# Priority 3: Clean, non-auto-generated IDs
"//[@id='login-form']"  # Good: semantic ID
# Skip: id='ember1234'   # Bad: auto-generated

# Priority 4: Text content (buttons/links)
"//button[text()='Submit Form']"
"//a[text()='Login']"

# Priority 5: Position-based (with warning)
"//div[2]/form[1]/button[1]"  # Shows warning to user
```

**Manual Selector Support:**
- **CSS Selectors:** `#email-field`, `.btn-primary`, `input[name='email']`
- **XPath:** `//input[@name='email']`, `//button[text()='Submit']`
- **Other formats:** Any valid Playwright selector syntax
- **Auto-detection:** System detects selector type and uses appropriate Playwright method

**Selector Validation:**
```python
def detect_selector_type(selector):
    if selector.startswith('//'):
        return 'xpath'
    elif any(char in selector for char in ['#', '.', '[', ':']):
        return 'css'
    else:
        return 'text'  # Fallback for plain text selectors
```

**User Experience:**
- **Visual picker:** Always generates XPath with reliability warning if position-based
- **Manual entry:** Supports any selector format for power users
- **Validation:** Real-time validation shows if selector is valid
- **Reliability indicator:** Visual cue showing selector reliability level

### Default Value Logic
**Dynamic Field Visibility:**
- **Template values:** Default value field visible (for fallback when template fails)
- **Static values:** Default value field hidden (not needed)
- **Real-time toggle:** Field appears/disappears based on template detection
- **Template detection:** Any value containing `{{...}}` triggers default value field

### Task Setup Configuration
**Simple Setup (Default):**
```
Setup:
Browser: [Chrome ▼]  URL: [https://example.com/form______]
```

**Advanced Setup (Optional):**
```
Setup:                                    [⚙️ Advanced Setup]
┌─────────────────────────────────────────────────────────────┐
│ Browser Sessions:                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Alias: main     Browser: Chrome    URL: example.com/form │ │
│ │ Alias: scraper  Browser: Firefox   URL: data-source.com  │ │
│ │ [➕ Add Browser Session]                                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## MVP Features (Current Scope)

**Included:**
- Desktop app with PyQt6 interface
- Multi-browser support (Chrome, Firefox, Edge)
- Visual element selector (dev tools style)
- Task save/load/share functionality
- Data input from CSV/Excel/JSON files
- Template variable system for data mapping
- Local processing only (privacy-first)
- Single automation execution
- Pre/post loop actions

**Excluded (YAGNI for MVP):**
- Conditional logic in tasks
- Detailed reporting and logs
- Background/scheduled execution
- Parallel task execution
- Browser extension integration
- Cloud/server components
- Complex error handling UI

## Technical Decisions Rationale

**Why PyQt6 over Tkinter:** Modern, professional UI components and better styling capabilities

**Why Playwright over Selenium:** Better dev tools integration, modern browser automation, multi-browser support

**Why JSON configs:** Human-readable, easily shareable, version-controllable, language-agnostic

**Why local processing:** Privacy concerns, authentication handling, accessibility without security constraints

**Why standalone executable:** Zero installation friction, works on any Windows machine

## Task Processor Design

### Core Components
1. **TaskProcessor** - Main orchestrator that manages task execution flow
2. **ActionExecutor** - Handles individual action execution
3. **DataIterator** - Manages row-by-row data processing
4. **TemplateResolver** - Resolves `{{row.name.Email}}` template variables
5. **BrowserController** - Playwright wrapper for browser automation

### Execution Flow
```python
def execute_task(task_config, data_df, stop_on_error=True):
    1. Pre-execution validation (check required columns exist)
    2. Execute prerequisites (navigate, wait for user)
    3. Execute pre_loop_actions
    4. For each row in data:
        - Resolve template variables for current row
        - Execute loop_actions with resolved values
        - Handle errors based on stop_on_error setting
        - Update progress tracking
    5. Execute post_loop_actions
    6. Return execution results
```

### Template Variable Resolution
**Strategy:** Row-by-row resolution during execution (not pre-resolved)

**Benefits:**
- Memory efficient for large datasets
- Supports dynamic values (timestamps, counters)
- Better error handling per row
- Future-ready for conditional logic

**Default Value Handling:**
```json
{
  "type": "set_value",
  "selector": "#email",
  "value": "{{row.name.Email}}",
  "default": "no-email@example.com",
  "description": "Enter email with fallback"
}
```

**Resolution Process:**
1. **Pre-validation:** Check all template columns exist in loaded data
2. **Runtime resolution:** Replace templates with actual row values
3. **Default application:** Use default value if cell is empty/null
4. **Error handling:** Fail gracefully with clear error messages

### Error Handling Strategy
- **Missing columns:** Pre-validation failure (task won't start)
- **Missing data cells:** Use default values or empty string
- **Browser element not found:** User choice per task (stop vs. continue)
- **General errors:** User choice per task (stop vs. continue)
- **Default behavior:** Stop on first error

### Browser State Management
- **Flexible browser instances:** Users define browser instances in initialization section
- **User-defined aliases:** "main", "scraper", "uploader" - any meaningful names
- **Single browser default:** If no browser specified in action, uses default instance
- **Multi-browser support:** Unlimited browser instances for complex workflows
- **Manual intervention support:** Pause actions allow users to handle any manual steps (authentication, validation, dynamic content, verification)
- **Browser persistence:** All instances persist throughout task execution

### Future Extensibility Architecture

**Browser Instance Management:**
- **Initialization phase:** Users define required browser instances with custom aliases
- **Action-level browser selection:** Each action can specify target browser instance
- **Default behavior:** Single browser tasks work without browser specification
- **Scalable design:** Architecture supports 1 to N browser instances seamlessly

**Extensible Action System:**
- **Browser-agnostic actions:** All actions work on any browser context
- **Optional browser field:** Actions default to primary browser if not specified
- **Data extraction support:** Actions can save extracted data for cross-browser workflows
- **Template variable expansion:** Support for both row data and extracted data references

**Manual Intervention Points:**
- **Authentication:** User login when automation cannot handle it
- **Validation:** "Check data looks correct before proceeding"
- **Dynamic content:** Steps too complex or variable to automate
- **Verification:** "Confirm results before continuing to next batch"
- **Troubleshooting:** Pause when unexpected conditions arise

**Future Workflow Patterns:**
- **Cross-browser data flow:** Extract from one browser, input to another
- **Multi-step validation:** Pause actions for user verification at key points
- **Conditional browser selection:** Future support for dynamic browser routing
- **Data-driven navigation:** URLs and actions driven by row data across multiple browsers

### Progress Tracking
- Real-time progress callbacks to UI
- Row-by-row status tracking (success/error/processing)
- Future: Color-coded data table showing processing status
- Future: Pause/resume functionality
- Execution results logged for review

## Data Loading Pipeline Design

### Supported Formats
- **CSV** - Direct pandas loading with auto-delimiter detection
- **Excel (.xlsx)** - Direct pandas loading
- **JSON** - Simple arrays or nested objects (auto-flattened)
- **YAML** - Converted to dict then processed as JSON

### Data Loader Architecture
```python
class DataLoader:
    def load_from_file(self, file_path):
        # Auto-detect format from extension and content
        
    def load_from_text(self, text_content, format_hint=None):
        # Handle copy-paste scenarios
        
    def flatten_json_data(self, df):
        # Use pd.json_normalize() for nested structures
        
    def get_preview(self, df, rows=10):
        # Return preview for UI display
```

### JSON Flattening Strategy
- **Nested objects:** Automatic flattening using `pd.json_normalize()`
- **Dot notation:** `user.contact.email` for nested field access
- **Template reference:** `{{row.name.user.contact.email}}`
- **Depth:** Flatten all levels automatically

### Data Loading Methods
1. **File Upload:** Traditional file browser dialog
2. **Drag & Drop:** Drop files directly onto data loading area
3. **Copy/Paste:** Paste CSV/JSON text directly into interface
4. **Format Detection:** Auto-detect with user override option

### UI Integration
**Data Loading Widget Components:**
- File browser button
- Drag-drop zone with visual feedback
- Paste text area
- Format selector dropdown (auto-detected)
- Data preview table (first 10 rows)
- Column mapping validation display
- Load status and error messages

### Error Handling
- **Malformed files:** Clear error messages with suggestions
- **Unsupported formats:** Graceful fallback with format hints
- **Large files:** Progress indication and memory management
- **Empty data:** Validation before allowing task execution

## Action Types Architecture

### Core Action Philosophy
**User-Intent Focused:** Users think in terms of "what they want to achieve" rather than "how to implement it". The tool handles implementation complexity automatically.

### Primary Action Types

#### 1. Set Value
**Purpose:** Set any form field to a specific value
**Scope:** All form elements - text inputs, dropdowns, radio buttons, checkboxes, toggles, sliders, date pickers
**User Experience:** User specifies element + desired value, tool figures out implementation

**Implementation Strategy:**
1. **Direct Value Setting:** Try `element.value = "desired_value"` first
2. **Framework Event Triggering:** Dispatch input/change events for React/Vue/Angular
   ```javascript
   element.dispatchEvent(new Event('input', { bubbles: true }))
   element.dispatchEvent(new Event('change', { bubbles: true }))
   ```
3. **Multi-Level Verification:**
   - Check `element.value` matches
   - **Framework State Verification:**
     ```javascript
     // React - check component state
     element._reactInternalFiber?.memoizedProps?.value
     
     // Vue - check reactive data
     element.__vue__?.$data
     
     // Angular - check form control value
     element.ng-reflect-model || element.formControl?.value
     ```
   - **Behavioral Verification:**
     - Form validation changes (error messages appear/disappear)
     - Dependent fields update (other fields react to the change)
     - Submit button state changes (enabled/disabled)
     - Visual feedback updates (CSS classes for valid/invalid states)
   - **Event-driven Verification:**
     - Wait for framework-specific events to fire
     - Monitor DOM mutations after state updates
     - Verify change handlers were triggered
   - Wait for loading states to resolve
4. **Automatic Fallback:** If direct setting fails, fall back to click sequence
   - Click dropdown → click option
   - Click radio button with matching value
   - Toggle checkbox to desired state

**JSON Schema:**
```json
{
  "type": "set_value",
  "browser": "main",
  "selector": "#email-field",
  "value": "{{row.name.Email}}",
  "default": "no-email@example.com",
  "description": "Enter email address"
}
```

**Robustness Expectations:**
- Standard form elements: 90% success rate
- Popular UI libraries (Material-UI, Ant Design): 80% success rate
- Custom corporate components: 60% success rate
- Legacy/complex implementations: 40% success rate with manual fallback

#### 2. Click
**Purpose:** Trigger actions on clickable elements
**Scope:** Buttons, links, tabs, menu items, action triggers
**User Experience:** Simple click action for elements that trigger behavior

**JSON Schema:**
```json
{
  "type": "click",
  "browser": "main",
  "selector": "#submit-button",
  "description": "Submit the form"
}
```

#### 3. Navigate
**Purpose:** Browser navigation and URL changes
**Scope:** Page navigation, URL changes
**Note:** Could be merged with Click for simplicity

**JSON Schema:**
```json
{
  "type": "navigate",
  "browser": "main",
  "url": "https://example.com/form",
  "description": "Navigate to form page"
}
```

### Fallback Mechanisms

#### Automatic Fallback (Tool Responsibility)
**When Set Value fails:**
1. Tool automatically attempts click-based interaction
2. For dropdowns: Click dropdown → Click matching option
3. For radio buttons: Click radio button with matching value
4. For checkboxes: Click to achieve desired state (checked/unchecked)
5. User remains unaware of implementation details

#### Manual Override (Edge Cases Only)
**For truly complex scenarios that can't be automated:**
- Multi-step wizards with dynamic content
- Drag-and-drop interactions
- Canvas-based UI components
- Custom interactions that break standard patterns

**JSON Schema for Manual Sequences:**
```json
{
  "type": "manual_sequence",
  "browser": "main",
  "steps": [
    {"action": "click", "selector": "#custom-dropdown"},
    {"action": "wait", "duration": 500},
    {"action": "click", "selector": ".option[data-value='{{row.name.Category}}']"},
    {"action": "click", "selector": "#confirm-selection"}
  ],
  "description": "Handle complex custom dropdown"
}
```

### Implementation Priority
1. **Set Value** - Covers 80% of form automation needs
2. **Click** - Covers remaining action triggers
3. **Navigate** - Basic browser navigation
4. **Manual Sequence** - Edge case fallback (future enhancement)

### Framework-Specific Handling
**React Applications:**
- Trigger synthetic events after value setting
- Handle controlled components properly
- Wait for state updates and re-renders

**Vue Applications:**
- Trigger reactivity system updates
- Handle v-model bindings
- Wait for DOM updates

**Angular Applications:**
- Trigger change detection cycles
- Handle form control updates
- Wait for digest cycles

**Legacy jQuery/Vanilla JS:**
- Trigger standard DOM events
- Handle custom event listeners
- Fall back to click sequences more frequently

### Error Handling Strategy
**Transparent to User:** Tool handles all implementation failures automatically
**Fallback Chain:** Direct setting → Event triggering → Click sequence → Manual override
**User Notification:** Only notify user if all automatic methods fail
**Debugging Mode:** Optional verbose logging for troubleshooting complex sites

## Monetization and Licensing System

### Pricing Strategy
**Monthly Subscription:** $0.49/month with 30-day free trial

**Rationale:**
- **Low barrier to entry:** $0.49 feels like "pocket change" vs $15-20 upfront risk
- **Try-before-commit:** Users can test for a month, cancel if it doesn't work
- **Side-project friendly:** Easy to discontinue without major customer obligations
- **Value proposition:** Incredible value compared to hours saved on manual data entry
- **Easy refunds:** One month refund vs angry customers who paid $20 two years ago

### Trial and Conversion System

**30-Day Free Trial (Anonymous):**
- ✅ Full functionality for 30 days
- ✅ Create unlimited tasks
- ✅ Execute automations
- ❌ **Import/Export disabled** (prevents workaround via export → reinstall → import)
- **No registration required** - completely anonymous usage

**After Trial Expires:**
- ❌ **App completely stops working**
- Shows single option: "Subscribe for $0.49/month to continue using your tasks"
- One button: "Subscribe Now"
- Small text: "Your tasks and settings will be preserved"
- **No reinstall guidance** - users must figure out workaround themselves

**Conversion Psychology:**
- Users invest 30 days building tasks
- Face choice: $0.49 vs losing all work and rebuilding
- No "comfortable free tier" to settle into
- Reinstall workaround possible but requires losing all tasks

### License Key System

**Payment Flow:**
1. User pays via Stripe/PayPal → provides email address
2. System generates unique license key
3. License key sent to email
4. User enters key in app → validates against server
5. Full functionality unlocked including import/export

**Multi-Device Support:**
- **Machine binding:** License keys tied to hardware fingerprint (CPU + motherboard)
- **Device limit:** 2-3 machines per license (reasonable for personal use)
- **Self-service management:** Users can view and remove active devices
- **Auto-cleanup:** Inactive devices (30+ days) automatically removed

**Device Management UI:**
```
Active Devices (2/3 slots used):
[Desktop-ABC4] Last used: Today        [Remove]
[Laptop-XYZ9] Last used: 3 days ago   [Remove]

+ Add this device
```

### Security and Anti-Piracy

**Trial Protection:**
- **Encrypted storage:** Trial dates encrypted with machine-specific key
- **Multiple locations:** Trial info stored in registry + app data + temp files
- **Integrity validation:** Checksums verify data hasn't been tampered with
- **Server validation:** Periodic check-ins with machine fingerprint

**License Key Protection:**
- **Server-side validation:** All keys validated against server (can't be faked locally)
- **Machine fingerprinting:** Keys tied to specific hardware configuration
- **No obvious patterns:** VIP keys look like regular keys, server determines privileges
- **Code obfuscation:** PyInstaller with obfuscation, no hardcoded secrets

**Key Renewal System (Anti-Compromise):**
- **User-initiated renewal:** "Renew License Key" button in app
- **Email-based process:** New key sent to registered email address
- **Safe activation:** Old key remains active until new key is used
- **Rate limiting:** 1 renewal per hour per email address
- **IP protection:** Max 5 renewal requests per IP per day

**Key Renewal Flow:**
1. User notices suspicious activity (getting kicked off frequently)
2. Clicks "Renew License Key" → enters email
3. New key sent to email (old key still works)
4. User enters new key → old key immediately deactivated
5. Compromised key holders lose access permanently

**VIP Users (Internal):**
- Special license keys for team members (free forever)
- Server-side privilege determination (not obvious in client code)
- Normal-looking keys with backend VIP status

### Technical Implementation

**Server Infrastructure:**
- Simple web server (Flask/FastAPI)
- Database: email ↔ license key mapping
- Email service (SendGrid/Mailgun) for key delivery
- License validation API endpoint
- **Global subscription toggle:** Server-side kill switch for enabling/disabling subscriptions

**Database Schema:**
```sql
licenses:
- email (primary key)
- license_key (unique)
- created_date
- status (active/cancelled)
- last_renewal_time

devices:
- license_key
- machine_fingerprint
- last_active
- device_name

settings:
- key (e.g., 'subscription_required')
- value (true/false)
```

**App Startup Flow:**
1. **Load local data:** Decrypt trial date and license key (if exists)
2. **API validation:** Send license key + machine fingerprint to server
3. **Server response:** License validity + global subscription requirement status
4. **App behavior:** Respect server's subscription toggle setting

**Local Data Storage (Encrypted):**
- **Trial start date:** Encrypted with machine-specific key
- **License key:** Encrypted with machine-specific key (prevents easy extraction/sharing)
- **Last validation cache:** For offline operation
- **Machine fingerprint:** CPU + motherboard hash for encryption key

**Encryption Implementation:**
```python
# Generate machine-specific encryption key
machine_key = hash(cpu_id + motherboard_id)

# Encrypt sensitive data
encrypted_license = encrypt(license_key, machine_key)
encrypted_trial = encrypt(trial_start_date, machine_key)

# Store encrypted data locally
store_local_data(encrypted_license, encrypted_trial)
```

**Subscription Toggle System:**
```python
def validate_license_request(license_key, machine_id):
    # Check global subscription requirement
    if not get_setting('subscription_required'):
        return {"valid": True, "subscription_required": False}
    
    # Normal license validation when subscriptions enabled
    if license_exists(license_key):
        return {"valid": True, "subscription_required": True}
    
    # Check trial status
    return check_trial_status(machine_id)
```

**Launch Strategy Flexibility:**
- **Free launch:** Set `subscription_required = False` on server
- **Enable subscriptions:** Flip to `True` at any time
- **Emergency disable:** Revert to `False` if issues arise
- **Gradual rollout:** Enable for percentage of users
- **A/B testing:** Different subscription models for different user groups

**Client-Server Communication:**
- License validation on app startup
- Periodic validation during usage
- Device registration/management
- Key renewal requests

### Revenue Protection Strategy

**Prevents Common Workarounds:**
- **Export/Import during trial:** Disabled throughout trial period
- **Date manipulation:** Encrypted, multi-location storage with integrity checks
- **Key sharing:** Machine limits + device management
- **Key compromise:** User-controlled renewal system
- **Mass piracy:** Server-side validation prevents fake keys

**Acceptable Losses:**
- **Determined hackers:** 1% will reverse engineer anyway (acceptable loss)
- **Serial reinstallers:** Some users will reinstall every 30 days (minimal impact)
- **Price point justification:** $0.49 makes hacking effort > subscription cost

**Security Philosophy:**
- Stop casual tampering and obvious workarounds
- Don't over-engineer for determined attackers
- Focus on conversion rather than perfect security
- Make legitimate use easier than piracy

## Smart XPath Generation & Self-Healing System

### **Ultra-Strict Randomness Filtering**

**Philosophy:** Better to reject questionable selectors and use powerful fallbacks than risk unreliable automation.

**Single Universal Filter:**
```python
def _is_random(value: str) -> bool:
    """Ultra-strict filter for ANY attribute value"""
    if not value or len(value) < 2 or len(value) > 30:
        return True
    
    # Only accept proper naming conventions
    SEMANTIC_PATTERNS = [
        r'^[a-z]+$',                           # Simple: header, modal
        r'^[a-z]+-[a-z]+(-[a-z]+)*$',         # kebab-case: login-form
        r'^[a-z]+[A-Z][a-z]*([A-Z][a-z]*)*$', # camelCase: loginForm
        r'^[a-z]+_[a-z]+(_[a-z]+)*$',         # snake_case: login_form
        r'^[A-Z][a-z]+([A-Z][a-z]*)*$',       # PascalCase: LoginForm
    ]
    
    return not any(re.match(pattern + '$', value) for pattern in SEMANTIC_PATTERNS)
```

### **Self-Healing Locator System**

**When XPath Execution Fails:**
1. **Parse Failed XPath:** Break down into component parts
2. **Test Each Component:** Verify which specific attributes still exist
3. **Granular Blacklisting:** Identify exact element+attribute combinations that failed
4. **User-Guided Recovery:** Launch element picker with learned constraints

**In-Execution Healing Flow:**
1. Task execution fails → Analyze failure → User prompt → In-context picker → Seamless recovery
2. **Same Browser Context:** User sees exact failure state
3. **Learning System:** Avoids same mistakes immediately
4. **Surgical Precision:** Only blacklists specific failing combinations

### XPath Generation Algorithm

**Priority Hierarchy (Most to Least Reliable):**

1. **Testing Attributes (Highest Reliability)**
   - `data-testid`, `data-cy`, `data-test`, `data-automation`, `data-qa`
   - These are specifically added by developers for testing stability
   - Example: `//[@data-testid='submit-form-btn']`

2. **Semantic Attributes (High Reliability)**
   - `name`, `type`, `role`, `aria-label`, `aria-describedby`
   - Meaningful attributes that describe element purpose
   - Example: `//input[@name='email']`, `//button[@type='submit']`

3. **Clean IDs and Classes (Medium Reliability)**
   - Only use if they don't match auto-generated patterns
   - Semantic, human-readable identifiers
   - Example: `//[@id='login-form']` ✅, Skip `//[@id='ember1234']` ❌

4. **Text Content (Medium Reliability)**
   - For buttons, links, and elements with stable text
   - Only use if text is unlikely to change (avoid dynamic content)
   - Example: `//button[text()='Submit Form']`, `//a[text()='Login']`

5. **Position-Based (Lowest Reliability - Warning Required)**
   - Structural position in DOM hierarchy
   - Most fragile, breaks when layout changes
   - Example: `//div[2]/form[1]/button[1]`
   - **User Warning:** "This selector may break if page layout changes"

### Auto-Generated Pattern Detection

**Patterns to Avoid:**
```python
AUTO_GENERATED_PATTERNS = [
    r'.*-\d{4,}$',           # Suffix with 4+ digits: button-1234, field-5678
    r'.*_\d{4,}$',           # Underscore + digits: input_9876, form_1234
    r'^[a-f0-9]{8,}$',       # Pure hex strings: a1b2c3d4, f7e8d9c0
    r'.*-[a-f0-9]{6,}$',     # Suffix with hex: btn-a1b2c3, div-f7e8d9
    r'.*\d{10,}$',           # Long numbers (timestamps): element-1640995200000
    r'^(ember|react|vue)\d+$', # Framework IDs: ember123, react456, vue789
    r'^\w+-\w+-\w+$',        # UUID-like: abc-def-ghi, x1y-z2a-b3c
    r'.*-auto-\d+$',         # Auto-suffixed: field-auto-1, btn-auto-99
]

def is_auto_generated(value):
    """Check if an ID/class appears to be auto-generated"""
    if not value or len(value) < 3:
        return True  # Too short to be meaningful
    
    return any(re.match(pattern, value, re.IGNORECASE) 
              for pattern in AUTO_GENERATED_PATTERNS)
```

## Browser Detection and Management System

### Supported Browsers
**Primary Support:** Chrome, Firefox, Edge
**Coverage Strategy:** Maximum compatibility with minimal complexity

**Browser Support Matrix:**
```python
SUPPORTED_BROWSERS = {
    'chrome': {
        'name': 'Google Chrome',
        'engine': 'chromium',
        'platforms': ['windows', 'macos', 'linux'],
        'market_share': '65%'
    },
    'firefox': {
        'name': 'Mozilla Firefox', 
        'engine': 'gecko',
        'platforms': ['windows', 'macos', 'linux'],
        'market_share': '3%'
    },
    'edge': {
        'name': 'Microsoft Edge',
        'engine': 'chromium', 
        'platforms': ['windows'],
        'market_share': '5%',
        'note': 'Chrome-compatible (same Chromium engine)'
    }
}
```

### Browser Detection Implementation

**Multi-Method Detection Strategy:**
1. **File System Check:** Primary method using known installation paths
2. **Registry Check:** Windows registry lookup for installed applications
3. **Command Line Check:** PATH availability as fallback

**Platform-Specific Paths:**
```python
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
```

**Detection Algorithm:**
```python
def detect_installed_browsers():
    """Detect all installed supported browsers"""
    browsers = {}
    platform = get_current_platform()
    
    for browser_id, config in SUPPORTED_BROWSERS.items():
        if platform in config['platforms']:
            path = find_browser_executable(browser_id, platform)
            if path:
                browsers[browser_id] = {
                    'name': config['name'],
                    'path': path,
                    'engine': config['engine']
                }
    
    return browsers

def find_browser_executable(browser_id, platform):
    """Find executable path using multiple detection methods"""
    paths = BROWSER_PATHS.get(browser_id, {}).get(platform, [])
    
    # Method 1: File system check
    for path in paths:
        if os.path.exists(path):
            return path
    
    # Method 2: Registry check (Windows only)
    if platform == 'windows':
        registry_path = check_windows_registry(browser_id)
        if registry_path:
            return registry_path
    
    # Method 3: Command line check
    command_path = check_command_availability(browser_id)
    if command_path:
        return command_path
    
    return None
```

### Browser Configuration in Tasks

**Task Setup Options:**
- **Default Browser:** Uses user's preferred browser setting
- **Specific Browser:** Requires specific browser for task execution

**JSON Schema:**
```json
{
  "name": "Contact Form Entry",
  "setup": {
    "browser": "default",  // "default", "chrome", "firefox", "edge"
    "url": "https://example.com/form"
  }
}
```

**Advanced Setup (Multi-Browser):**
```json
{
  "name": "Cross-Browser Data Processing",
  "setup": {
    "sessions": [
      {"alias": "main", "browser": "chrome", "url": "https://app.com"},
      {"alias": "scraper", "browser": "firefox", "url": "https://data.com"}
    ]
  }
}
```

### User Experience Integration

**App-Level Default Browser:**
- User sets preferred browser in settings
- All new tasks default to this browser
- Can be overridden per task

**Browser Selection UI:**
```
Browser: [Default (Chrome) ▼]
         ┌─────────────────────────┐
         │ Default (Chrome)        │ ← Uses app default
         │ Google Chrome           │ ← Specific browser
         │ Microsoft Edge          │
         │ Mozilla Firefox         │
         └─────────────────────────┘
```

**Task Sharing Validation:**
- **Default browser tasks:** Always portable (uses recipient's default)
- **Specific browser tasks:** Validate recipient has required browser
- **Warning system:** "This task requires Firefox. Install Firefox to run."

### Playwright Integration

**Browser Launch Configuration:**
```python
def launch_browser(browser_config):
    """Launch browser using detected executable path"""
    browser_type = browser_config['type']
    executable_path = browser_config['path']
    
    if browser_type in ['chrome', 'edge']:  # Both use Chromium
        return playwright.chromium.launch(executable_path=executable_path)
    elif browser_type == 'firefox':
        return playwright.firefox.launch(executable_path=executable_path)
```

**Benefits of Using Installed Browsers:**
- **Smaller app size:** ~50MB vs ~500MB with bundled browsers
- **Familiar environment:** User's bookmarks, extensions, settings
- **Always updated:** Users maintain browser updates
- **No licensing issues:** No browser redistribution concerns

### Compatibility and Testing Strategy

**Engine Compatibility:**
- **Chrome + Edge:** Same Chromium engine = 99.9% compatibility
- **Firefox:** Different Gecko engine = requires separate testing
- **Cross-platform:** Chrome/Firefox work identically across platforms

**Testing Approach:**
- **Tier 1:** Chrome + Firefox (full feature testing)
- **Tier 2:** Edge (compatibility validation with Chrome)
- **Platform testing:** Windows (all 3), macOS/Linux (Chrome + Firefox)

**Minimum Requirements:**
- At least one supported browser must be installed
- App validates on startup and guides installation if needed
- Graceful degradation if preferred browser unavailable

## Development Progress

### Phase 1: Basic PyQt6 App Structure ✅ COMPLETE
- ✅ Main window with navigation between 3 pages
- ✅ Task Execution page with data loading area and progress tracking
- ✅ Task Manager page with collapsible builder (100% → 20/80 split)
- ✅ Subscription page with license key management
- ✅ Clean Poetry environment with minimal dependencies
- ✅ Working PyQt6 application with basic navigation

### Phase 2: Browser Detection System ✅ COMPLETE
- ✅ Multi-method browser detection (file paths, registry, command line)
- ✅ Support for Chrome, Firefox, Edge across Windows/macOS/Linux
- ✅ Platform-specific path detection
- ✅ Tested and working on Windows (Chrome + Edge detected)

### Phase 3: Basic Browser Integration ✅ COMPLETE
- ✅ Sync Playwright integration with detected browsers
- ✅ Browser controller for launching and managing browser instances
- ✅ Navigation to URLs using user's installed browsers
- ✅ Sync browser management with proper cleanup
- ✅ Tested browser launching and navigation to Google
- ✅ **FIXED:** Browser connection persistence issues resolved by switching to sync Playwright

**Browser Connection Fix:**
- **Issue:** `'NoneType' object has no attribute 'send'` errors due to async/sync conflicts
- **Root Cause:** Async Playwright WebSocket connections unstable in PyQt6 synchronous environment
- **Solution:** Converted entire codebase from async to sync Playwright API
- **Result:** Stable browser connections, no more connection loss during element picking
- **Benefits:** Simpler code, better error handling, matches proven desktop automation patterns

**Browser Architecture Decision:**
- **Separate Browser Per Thread:** Each component manages its own browser lifecycle
- **Task Manager:** Own browser for element picking, cleanup on page exit
- **Execution Worker:** Own browser for task execution, cleanup on completion
- **Benefits:** Clean ownership, no cross-thread issues, simple cleanup, thread isolation
- **Trade-off:** User re-authentication between config and execution (acceptable for workflow)

**Playwright Architecture Decision:**
- **Sync Playwright API:** Uses `sync_playwright()` for stable PyQt6 integration
- **Connection Stability:** Eliminates WebSocket connection issues in GUI environment
- **Simple State Management:** Direct method calls without async/await complexity
- **Proven Pattern:** Matches working implementations in similar desktop automation tools

**Playwright Capabilities vs Requirements:**
- **Playwright provides:** Programmatic element location, interaction, and automation
- **Playwright does NOT provide:** Interactive element picker for end users
- **Our solution:** Custom JavaScript injection for interactive element selection
- **Industry standard:** All automation tools (Selenium IDE, Cypress Studio) use this approach
- **Architecture:** Sync Playwright API for stable PyQt6 integration

### Phase 3.5: Element Picker & Task Execution ✅ COMPLETE
**Element Picker Implementation:** ✅ COMPLETE
- ✅ **JavaScript Injection:** Custom hover highlighting with blue overlay
- ✅ **Click Capture:** Prevents default click behavior and captures element
- ✅ **Smart XPath Generation:** Recursive context building with ultra-strict randomness filtering
- ✅ **Semantic Validation:** Only accepts proper naming conventions (camelCase, kebab-case, snake_case, PascalCase)
- ✅ **Universal Filtering:** All attributes filtered for auto-generated values using single `is_random()` function
- ✅ **Uniqueness-Focused:** No reliability flags - builds selectors until unique or adds ancestor context
- ✅ **QThread Integration:** Proper sync handling without PyQt6 event loop conflicts
- ✅ **Browser Persistence:** Browser stays open between element picks (no re-authentication needed)
- ✅ **Page Lifecycle Management:** Browser cleanup when leaving Task Manager page
- **Hybrid Workflow Support:** User can manually navigate, authenticate, then continue automation
- **Connection Loss Handling:** User-prompted recovery instead of automatic restarts
- **Smart Validation:** Tests connection validity before reuse, clean restart when needed

**Task Execution System:** ✅ COMPLETE
- ✅ **Worker Thread Execution:** Tasks run in separate thread with own browser lifecycle
- ✅ **Cancel/Progress Support:** Real-time progress updates and cancellation capability
- ✅ **Browser Isolation:** Execution thread manages own browser, cleanup on completion
- ✅ **UI Responsiveness:** Main thread stays responsive during task execution
- ✅ **Error Handling:** Comprehensive error reporting and recovery
- ✅ **Thread Safety:** Clean separation between Task Manager and Execution browsers

**Why Custom JavaScript Element Picker:**
Playwright does NOT provide built-in interactive element picking capabilities. Playwright's design is for programmatic automation, not user interaction:
- `page.locator()` - finds elements programmatically (requires knowing selector)
- `page.highlight()` - highlights specific elements you already know
- **No picker mode** - no interactive "hover and click to select" functionality

Every automation tool uses custom JavaScript for element picking:
- Selenium IDE, Cypress Studio, Puppeteer Recorder all inject custom JS
- Browser dev tools inspector is separate from automation frameworks
- Interactive element selection requires custom hover/click event handling

Our sync approach provides the exact UX needed: hover highlighting + click capture + reliable selector generation.

**Action Creation System:** ✅ COMPLETE
- ✅ **Form-based UI:** Proper action creation form with fields (not dialog-based)
- ✅ **Progressive disclosure:** Action Type dropdown shows/hides relevant fields
- ✅ **Element picker integration:** 🎯 button populates Target Element field
- ✅ **Form validation:** Ensures required fields are filled
- ✅ **Actions list:** Shows numbered actions with descriptions

**Task Storage & Management:** ✅ COMPLETE
- ✅ **Task storage:** JSON-based task saving and loading
- ✅ **Task list refresh:** Real tasks appear in Task Manager and Execution pages
- ✅ **Edit/Delete:** Full CRUD operations for tasks with single-click editing
- ✅ **Browser persistence:** Element picker reuses browser session (no re-authentication)
- ✅ **Connection recovery:** User-controlled browser restart on connection loss
- ✅ **Page lifecycle:** Browser cleanup when switching between pages

**Task Execution Engine:** ✅ COMPLETE
- ✅ **Worker thread architecture:** Execution runs in separate thread with own browser
- ✅ **Cancel/Progress UI:** Real-time progress bar and cancel button
- ✅ **Action execution:** Handles click, set_value, navigate, wait actions
- ✅ **Error handling:** Configurable stop/continue behavior with detailed error reporting
- ✅ **Browser lifecycle:** Fresh browser per execution, automatic cleanup
- ✅ **Thread isolation:** No cross-thread browser access issues
- ✅ **Self-Healing Locators:** Intelligent XPath failure analysis and in-execution repair
- ✅ **Granular Blacklisting:** Learns which specific element+attribute combinations are unreliable
- ✅ **In-Context Healing:** Element picker launches in execution browser for seamless recovery

### Phase 4: Data Integration & Execution Recovery (NEXT)
- Data loading (CSV, Excel, JSON) with pandas
- Template evaluation system (`{{row_name('Email')}}`)
- Data preview with real-time processing status
- Integration with UI data loading section
- **Execution Worker Thread:** Separate thread for task execution with cancel/progress support
- **Browser Per Thread:** Task Manager and Execution Worker each manage own browser lifecycle
- **Execution State Management:** Persistent row-level status tracking
- **Advanced Execution Options:** Status-based row selection for execution
- **Connection Loss Handling:** User-controlled recovery with clear messaging
- **Self-Healing Locators:** Intelligent XPath failure analysis and in-execution repair
- **Smart XPath Generation:** Ultra-strict randomness filtering with recursive context building

**Execution State System:**
- **Dynamic Status Selection:** Checkboxes for available statuses (Failed, Unprocessed, Completed, etc.)
- **Persistent State:** Per-task execution state storage (`task_name_execution_state.json`)
- **Flexible Recovery:** Execute subsets based on row status
- **Future-Proof:** New statuses automatically available in UI

**Connection Loss Strategy:**
- **Task Creation Mode:** Prompt user "Connection lost. Restart browser?" (Cancel/Restart options)
- **Task Execution Mode:** Always cancel with message "Connection lost. Use 'Execute Unprocessed Only' to resume."
- **No Auto-Restart:** User always in control, no surprise re-authentication
- **Clean Recovery:** Return to main screen, use advanced execution options to resume
- **Browser Persistence:** Only restart browser if process actually crashes, not on page errors

**Error Handling During Execution:**
- **Default Strategy:** Stop on first error (simple, predictable)
- **Future-Proof Design:** Backend supports configurable error handling (hidden from UI)
- **Extensible Options:** Ready for "skip and continue", "pause and ask", etc.
- **User Control:** Runtime options for manual intervention (pause to login, then resume)
- **Error Types:** Distinguish global errors (logout) vs row-specific errors (validation)

**Browser Reuse for Hybrid Workflow:**
- **Persistent Browser:** Stays open between element picks and user interactions
- **Authentication Preservation:** Maintains login sessions during task creation
- **Manual Navigation Support:** User can authenticate, navigate, then continue picking elements
- **Browser as Persistent Window:** Never restart browser based on page content or auth state
- **Simple Connection Logic:** Only restart if browser process actually crashes (rare)
- **Element Picker Reliability:** Works on any page state (login pages, error pages, etc.)
- **User-Controlled Navigation:** Browser stays persistent regardless of page content

### Phase 5: Subscription System (PLANNED)
- Trial system with local tracking
- License key validation
- Payment integration
- Multi-device management

**Future considerations:**
- Advanced error recovery mechanisms
- Task validation and testing features
- Performance optimization for large datasets
- Pause/resume functionality
- Real-time progress visualization

## Current Status
- Requirements gathering: ✅ Complete
- Technical stack selection: ✅ Complete  
- Application architecture: ✅ Complete
- UX flow design: ✅ Complete
- JSON schema design: ✅ Complete
- Task processor design: ✅ Complete
- Data loading pipeline design: ✅ Complete
- Implementation: ⏳ Ready to begin

---

*Last Updated: [Current Date]*
*Status: Ready for implementation phase*