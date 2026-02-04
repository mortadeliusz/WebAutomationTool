# Browser Management Refactoring - Session Summary

## What We Did

### 1. File Selector Enhancement
**Problem:** File selector defaulted to CSV, forcing users to switch to Excel manually.

**Solution:** Show all supported formats in one filter using `DataLoader.SUPPORTED_EXTENSIONS`.

**Files Modified:**
- `ui/pages/workflow_execution.py` - Updated file dialog to show all supported formats

**Result:** Users see `.csv`, `.xlsx`, `.json`, `.yaml`, `.yml` files at once.

---

### 2. Browser Detection & Display
**Problem:** Hardcoded browser list, no detection of installed browsers.

**Solution:** Lazy singleton detection with enhanced display labels and runtime validation.

**Implementation:**
- Module-level lazy singleton: `get_browser_display_mapping()`
- Detects browsers once per session
- Shows installed browsers first, uninstalled with "(not installed)" suffix
- Warns user when uninstalled browser selected
- Runtime validation at launch with clear error messages

**Files Modified:**
- `ui/components/browser_config_section.py` - Added detection and display mapping

**Display Format:**
- Installed: "Google Chrome"
- Not installed: "Mozilla Firefox (not installed)"

**Mapping:**
- Config stores clean IDs: `"chrome"`, `"firefox"`, `"edge"`
- UI shows enhanced labels
- `id -> display` mapping with reverse lookup on selection

---

### 3. Accordion Integration
**Problem:** Custom collapse implementation inconsistent with rest of app.

**Solution:** Replace custom collapse with generic Accordion component.

**Files Modified:**
- `ui/components/browser_config_section.py` - Replaced custom collapse with Accordion

**Changes:**
- Removed: `toggle_collapse()`, `collapse_button`, `is_expanded`
- Added: Accordion component
- Moved: Status label from header to content (per-instance)

**Result:** Consistent collapse behavior, cleaner code (-12 lines).

---

### 4. BrowserInstance Component Extraction
**Problem:** Browser config logic mixed in container, not reusable for multi-browser.

**Solution:** Extract BrowserInstance component with alias and conditional display support.

**Files Created:**
- `ui/components/browser_instance.py` - Single browser instance widget

**Files Modified:**
- `ui/components/browser_config_section.py` - Simplified to container (200+ lines → 30 lines)

**BrowserInstance Features:**
- Accepts `alias` parameter (e.g., "main", "secondary")
- Accepts `show_alias` parameter (True/False for conditional display)
- Contains: Status, browser type, starting URL, launch/close buttons
- Subscribes to browser state observer per alias
- All browser config logic encapsulated

**BrowserConfigSection (Container):**
- Creates Accordion wrapper
- Creates BrowserInstance(s)
- Delegates get_config/set_config to instance(s)

**Current State (Phase 1):**
```python
self.instance = BrowserInstance(
    self.accordion.content_frame,
    alias="main",
    show_alias=False  # Hidden for single browser
)
```

**Future State (Phase 2 - Multi-Browser):**
```python
for alias, config in workflow['browsers'].items():
    instance = BrowserInstance(
        self.accordion.content_frame,
        alias=alias,
        show_alias=len(workflow['browsers']) > 1  # Show if multiple
    )
    instance.set_config(config)
```

---

## Multi-Browser Architecture (Designed, Not Implemented)

### Display Logic
**Conditional Visibility:**
- Single browser: Hide alias everywhere
- Multiple browsers: Show alias everywhere

```python
show_alias = len(workflow['browsers']) > 1
```

### Alias Validation Rules
**Restrictions:**
- Not empty or whitespace
- Unique (no duplicates)
- **Any characters allowed** (including spaces for better UX)

```python
def validate_alias(alias, current_alias, all_aliases):
    if not alias or not alias.strip():
        return False, "Alias cannot be empty"
    
    if alias != current_alias and alias in all_aliases:
        return False, "Browser alias already exists"
    
    return True, None
```

### Rename Logic
**Steps:**
1. Validate new alias (not empty, unique)
2. Update browser key in workflow
3. **Cascade update:** Update all actions using old alias
4. Show success message with count

### Delete Logic
**Steps:**
1. Check if last browser (block deletion)
2. Check if actions use this browser
3. If actions exist: Show confirmation dialog
4. If user proceeds: Delete browser + delete related actions
5. If user cancels: Do nothing

**Confirmation Dialog:**
```
"5 action(s) use this browser.

If you proceed, they will be deleted."

[Cancel] [Proceed]
```

### Add Browser Logic
**Steps:**
1. Validate alias (not empty, unique)
2. Add browser to workflow
3. Auto-generate alias if needed ("Browser 1", "Browser 2")

### Action Assignment Logic
**Single Browser:**
```python
browser_alias = list(workflow['browsers'].keys())[0]
action['browser_alias'] = browser_alias
```

**Multiple Browsers:**
```python
browser_alias = browser_selector.get_value()
action['browser_alias'] = browser_alias
```

---

## Current Hardcoding Locations

**1. Workflow Creation** (`src/utils/workflow_files.py`)
- Creates `browsers.main` structure

**2. Workflow Editor** (`workflow_single_page_editor.py`)
- Gets/sets `browsers['main']`

**3. Actions List** (`actions_list.py`)
- Sets `browser_alias: 'main'` on save (line 283)
- Uses `"main"` for element picker (line 327)

**4. Browser Config Section** (`browser_config_section.py`)
- Creates single instance with `alias="main"`

---

## Backend Multi-Browser Support (Already Exists)

**BrowserController:**
- All methods accept `alias` parameter
- Storage is per-alias: `self.browsers[alias]`, `self.pages[alias]`
- Methods: `launch_browser(type, alias)`, `is_browser_running(alias)`, etc.

**BrowserStateObserver:**
- Events include alias: `notify(event_type, alias)`
- Listeners receive alias: `callback(event_type, alias)`

**Conclusion:** Backend fully supports multi-browser. Only UI needs implementation.

---

## Next Steps (Phase 2 - Multi-Browser)

### UI Changes Needed:
1. **BrowserConfigSection:**
   - Loop through `workflow['browsers']` dict
   - Create BrowserInstance per browser
   - Add "Add Browser" button
   - Add rename/delete buttons per instance

2. **ActionsList:**
   - Show browser dropdown if `len(browsers) > 1`
   - Auto-assign if `len(browsers) == 1`
   - Get available browsers from parent

3. **WorkflowEditor:**
   - Support multiple browsers in get/set config
   - Pass browser count to components

### Validation Logic:
- Implement rename with cascade update
- Implement delete with confirmation
- Implement add with validation

### Estimated Effort:
- 2-3 hours for full multi-browser support

---

## Files Modified This Session

1. `ui/pages/workflow_execution.py` - File selector
2. `ui/components/browser_config_section.py` - Accordion + extraction
3. `ui/components/browser_instance.py` - **NEW** - Extracted component
4. `docs/ARCHITECTURE_DECISIONS.md` - Added ADR-012 (browser detection)

---

## Key Decisions

1. **Browser detection:** Lazy singleton, detect once per session
2. **Display format:** Show installation status, sort installed first
3. **Alias naming:** Allow spaces (e.g., "Main Browser")
4. **Conditional display:** Hide alias for single browser, show for multiple
5. **Delete behavior:** Confirmation dialog, delete related actions
6. **Rename behavior:** Cascade update to all actions
7. **Component extraction:** BrowserInstance for reusability

---

## Testing Checklist

- [ ] File selector shows all supported formats
- [ ] Browser detection shows correct installation status
- [ ] Installed browsers appear first in dropdown
- [ ] Warning shown when uninstalled browser selected
- [ ] Accordion collapse/expand works
- [ ] Browser launch/close works with "main" alias
- [ ] Browser state observer updates status correctly
- [ ] Workflow save/load preserves browser config

---

## Documentation TODO

- Update ARCHITECTURE_GUIDE.md with BrowserInstance component
- Document multi-browser validation logic when implemented
- Add testing procedures for multi-browser workflows
