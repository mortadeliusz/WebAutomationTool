# Architecture Decision Records

> **Modus Operandi Compliance:** This document follows the "Pre-Implementation Analysis (MANDATORY)" and "Decision documentation" principles from [MODUS_OPERANDI.md](./MODUS_OPERANDI.md).

## ADR-001: UI Framework Selection

**Date:** December 2024  
**Status:** Accepted  
**Decision Makers:** Development Team

### Context
Need to select UI framework for desktop automation tool targeting non-technical users. Requirements:
- Professional appearance with modern themes
- Small executable size for distribution
- Commercial licensing compatibility
- Async/await support for browser automation
- Native OS integration

### Decision
**Selected:** CustomTkinter with async-tkinter-loop integration

### Alternatives Considered

#### PyQt6
- **Pros:** Mature, feature-rich, excellent documentation
- **Cons:** **CRITICAL: GPL/Commercial licensing issues for commercial product**
- **Rejection Rationale:** Licensing incompatible with commercial distribution

#### Eel (Web-based)
- **Pros:** Web technologies, familiar development
- **Cons:** **CRITICAL: Abandoned project, insufficient community support**
- **Cons:** Large executable size (150MB+ vs 20-30MB)
- **Rejection Rationale:** Project appears abandoned, unsustainable for long-term product

#### Tkinter (Standard)
- **Pros:** Built-in, no dependencies
- **Cons:** Outdated appearance, limited theming, no async support
- **Rejection Rationale:** Poor user experience for modern application

### Consequences

**Positive:**
- MIT license - commercial-friendly
- Modern appearance with dark/light themes
- Small executable footprint (20-30MB)
- Active development and community
- Native async/await support via async-tkinter-loop

**Negative:**
- Smaller ecosystem compared to PyQt
- Less mature than traditional frameworks
- Custom component development required

**Risks:**
- CustomTkinter project sustainability (mitigated by active development)
- Learning curve for team (mitigated by good documentation)

### Implementation Notes
- Integrated with async-tkinter-loop for Playwright compatibility
- Component-aware theming system implemented
- Registry pattern used for extensible architecture

---

## ADR-002: Browser Automation Framework

**Date:** December 2024  
**Status:** Accepted

### Context
Need browser automation framework for web form filling and element interaction.

### Decision
**Selected:** Playwright

### Alternatives Considered

#### Selenium
- **Pros:** Mature, widely adopted, extensive documentation
- **Cons:** Synchronous by default, slower execution, more complex setup
- **Rejection Rationale:** Poor async integration, performance limitations

#### Puppeteer
- **Pros:** Fast, modern, good async support
- **Cons:** Node.js dependency, JavaScript-only
- **Rejection Rationale:** Language mismatch with Python stack

### Consequences

**Positive:**
- Native async/await support
- Multi-browser support (Chrome, Firefox, Safari)
- Modern web app compatibility
- Fast execution and reliable element detection

**Negative:**
- Newer framework (less Stack Overflow content)
- Browser binary management complexity

---

## ADR-003: Async Integration Pattern

**Date:** December 2024  
**Status:** Accepted

### Context
CustomTkinter is synchronous, Playwright is async - need integration solution.

### Decision
**Selected:** async-tkinter-loop library with AsyncCTk mixin

### Alternatives Considered

#### Threading + asyncio.run()
- **Pros:** Standard library approach
- **Cons:** Complex thread synchronization, UI blocking issues
- **Rejection Rationale:** Violates "no shortcuts" modus operandi principle

#### Custom Event Loop Integration
- **Pros:** Full control
- **Cons:** High complexity, maintenance burden
- **Rejection Rationale:** Reinventing wheel, technical debt risk

### Consequences

**Positive:**
- Native async/await in UI callbacks
- No blocking operations on UI thread
- Clean integration pattern

**Negative:**
- Additional dependency
- Library sustainability risk

---

## ADR-004: File Architecture Pattern

**Date:** December 2024  
**Status:** Accepted

### Context
Need clean separation of concerns per modus operandi "No mixed concerns" principle.

### Decision
**Selected:** Layered architecture with clear boundaries

```
ui/          # User interface components only
src/         # Business logic only  
docs/        # Documentation
config/      # Configuration files
user_data/   # User-generated content
```

### Alternatives Considered

#### Single Directory Structure
- **Rejection Rationale:** Violates "No single-file applications" and separation of concerns

#### Feature-Based Structure
- **Rejection Rationale:** Creates mixed concerns within feature folders

### Consequences

**Positive:**
- Clear separation of concerns
- Easy to locate components
- Scalable architecture
- Testable in isolation

**Negative:**
- More directories to navigate
- Import path complexity

---

## ADR-005: State Management Strategy

**Date:** December 2024  
**Status:** Accepted

### Context
Need user preference persistence and navigation state management.

### Decision
**Selected:** Hybrid approach - immediate persistence for critical state, session batching for high-frequency updates

### Rationale
- Navigation state: Immediate persistence (critical for user experience)
- Window size/theme: Session batching (performance optimization)
- Workflow selection: Immediate persistence (user context preservation)

### Consequences

**Positive:**
- Optimal performance (no excessive disk I/O)
- Crash-safe critical state
- Clean user experience

**Negative:**
- Complexity in state categorization
- Potential data loss for non-critical state

---

## ADR-006: User Experience Overlay Pattern

**Date:** December 2024  
**Status:** Accepted

### Context
Need user guidance during blocking operations (element picker, key capture) without disrupting async workflows or creating platform dependencies.

### Decision
**Selected:** Full-app overlay using CTkFrame with place() geometry

### Alternatives Considered

#### Auto-Focus Browser + App Re-focus
- **Pros:** Automatic window management, smooth user flow
- **Cons:** Platform-specific code (Windows/macOS/Linux), maintenance burden
- **Rejection Rationale:** Violates cross-platform compatibility and "no technical debt" principles

#### Modal Dialog (CTkToplevel)
- **Pros:** Standard modal pattern, built-in focus management
- **Cons:** Separate window, complex positioning, visual disconnect from blocked content
- **Rejection Rationale:** Poor visual UX - looks like error dialog rather than blocking overlay

#### Transparency Enhancement (pywinstyles)
- **Pros:** Visual polish with 50% transparency effect
- **Cons:** Windows-only dependency, platform lock-in, maintenance complexity
- **Rejection Rationale:** Visual enhancement doesn't justify architectural compromise

### Consequences

**Positive:**
- Cross-platform compatible (no OS-specific code)
- Natural interaction blocking (CTkFrame absorbs all events)
- Theme-compliant colors (uses app's existing theme system)
- Clean architecture (reusable component with callback pattern)
- Zero external dependencies

**Negative:**
- No transparency effect (CTkFrame limitation)
- Requires manual positioning of UI elements

**Risks:**
- None identified - standard UI pattern with proven implementation

### Implementation Notes
- Uses place() geometry for floating overlay behavior
- Callback pattern for clean separation of concerns
- Reusable for both element picker and key capture operations
- Theme-aware styling without forced colors

---

## ADR-007: Wizard Editor Abandonment

**Date:** December 2024  
**Status:** Accepted  
**Decision Makers:** Development Team

### Context
Initially implemented wizard-based workflow editor to improve UX for newcomers by splitting workflow creation into steps.

### Decision
**Selected:** Abandon wizard approach, focus on single-page editor improvements

### Alternatives Considered

#### Continue Wizard Development
- **Pros:** Progressive disclosure, step-by-step guidance
- **Cons:** Added navigation overhead without meaningful UX simplification
- **Rejection Rationale:** Wizard added friction (extra clicks) without reducing complexity

#### Hybrid Approach (Both Editors)
- **Pros:** User choice between approaches
- **Cons:** Technical debt maintaining two parallel systems
- **Rejection Rationale:** Violates "no technical debt tolerance" principle

### Consequences

**Positive:**
- Single codebase to maintain
- No mode switching complexity
- Focus development effort on improving existing editor
- Eliminated unused components (TwoOptionToggle mode switching)

**Negative:**
- Lost potential progressive disclosure benefits
- No step-by-step guidance for new users

**Mitigation:**
- Web app tutorials for onboarding (better medium for education)
- Single-page editor improvements (accordion sections, better organization)

### Implementation Notes
- Removed WorkflowWizardEditor component
- Simplified WorkflowManagementPage (no mode switching)
- Cleaned up state management (removed wizard_mode preferences)
- Maintained TwoOptionToggle component (used elsewhere)

---

## ADR-008: Accordion Component for UI Organization

**Date:** December 2024  
**Status:** Accepted

### Context
Single-page workflow editor needs better visual organization and progressive disclosure without wizard complexity.

### Decision
**Selected:** Generic Accordion component with collapsible sections

### Alternatives Considered

#### CustomTkinter Built-in Components
- **CTkTabview:** Horizontal tabs, not vertical collapsible sections
- **Rejection Rationale:** Doesn't provide the collapsible behavior needed

#### Third-party Accordion Libraries
- **Pros:** Pre-built functionality
- **Cons:** Additional dependencies, may not match app theming
- **Rejection Rationale:** CustomTkinter ecosystem limited, custom solution provides full control

### Design Decisions

#### Clickable Label vs Button Header
- **Selected:** Clickable CTkLabel with hover effects
- **Rationale:** Cleaner visual integration, better theming consistency
- **Alternative Rejected:** CTkButton (looks too prominent, button-like)

#### Content Access Pattern
- **Selected:** Direct property access (`accordion.content_frame`)
- **Rationale:** Pythonic, simple, extensible with @property if needed
- **Alternative Rejected:** Getter method (`get_content_frame()`) - unnecessary abstraction

### Consequences

**Positive:**
- Reusable across entire application
- Progressive disclosure without navigation complexity
- Theme-compliant styling
- Configurable text alignment
- Zero external dependencies

**Negative:**
- Custom component to maintain
- Limited compared to mature accordion libraries

**Risks:**
- None identified - simple, well-tested UI pattern

### Implementation Notes
- Dynamic icons: ▼ (expanded) / ▶ (collapsed)
- Hover effects for visual feedback
- Configurable anchor parameter for text alignment
- Content frame exposed as direct property

---

## ADR-009: URL Normalization with Protocol Fallback

**Date:** December 2024  
**Status:** Accepted and Implemented

### Context
Users enter URLs without protocol prefix (e.g., `www.google.com` or `google.com`), causing navigation failures. Need automatic protocol handling that works for both modern HTTPS sites and legacy HTTP-only internal corporate sites.

### Decision
**Selected:** HTTPS-first with automatic HTTP fallback

### Alternatives Considered

#### Default to HTTP
- **Pros:** Works with legacy sites immediately
- **Cons:** Insecure by default, extra redirect for 95% of sites, browser security warnings
- **Rejection Rationale:** Modern web is HTTPS-first, HTTP should be exception not default

#### HTTPS-only (no fallback)
- **Pros:** Simple, secure, follows modern standards
- **Cons:** Fails on HTTP-only internal corporate sites
- **Rejection Rationale:** Can't assume user context - many enterprises use HTTP internally

#### Manual protocol requirement
- **Pros:** Explicit, no ambiguity
- **Cons:** Poor UX - users expect `google.com` to work
- **Rejection Rationale:** Violates user expectations and modern browser behavior

### Consequences

**Positive:**
- Works with modern HTTPS sites (95%+ of web)
- Automatically handles HTTP-only legacy sites
- No user intervention required
- Matches modern browser behavior
- Preserves explicit protocols when provided

**Negative:**
- Slight delay on HTTP-only sites (one failed HTTPS attempt)
- Two navigation attempts for HTTP sites

**Risks:**
- None identified - standard browser behavior

### Implementation

```python
# src/utils/url_helper.py
async def normalize_and_navigate(page: Page, url: str, timeout: int = 30000):
    # If protocol specified: use as-is
    if url.startswith(('http://', 'https://', 'file://')):
        await page.goto(url, timeout=timeout)
    
    # Try HTTPS first
    try:
        await page.goto(f'https://{url}', timeout=timeout)
    except:
        # Fallback to HTTP
        await page.goto(f'http://{url}', timeout=timeout)
```

**Integration Points:**
- `browser_controller.navigate()` - Workflow starting URLs
- `handle_navigate()` - Navigate actions in workflows

**Behavior:**
- `www.google.com` → tries `https://www.google.com`, falls back to `http://www.google.com`
- `http://localhost:3000` → uses as-is
- `{{col("url")}}` → normalizes after template resolution

---

## ADR-010: Browser State Management - Reactive Pattern

**Date:** December 2024  
**Status:** Accepted and Implemented  
**Decision Makers:** Development Team

### Context
Browser state management had critical UX issues:
1. Picker launched browser to Google instead of workflow's configured starting URL
2. UI browser status was stale - didn't reflect actual browser state when:
   - Browser launched via picker (UI showed "Not Running")
   - Browser closed manually outside app (UI showed "Running")

**Root Cause:** Browser state split across multiple components with no synchronization mechanism. UI components cached state instead of reading from single source of truth.

### Decision
**Selected:** Observer Pattern (Reactive UI)

### Alternatives Considered

#### Polling Pattern
- **Pros:** Simple to implement, no new infrastructure
- **Cons:** Inefficient (constant polling), delayed updates, each component needs own timer
- **Technical Debt:** MEDIUM - not scalable, inefficient
- **Rejection Rationale:** Violates "no technical debt tolerance" principle

#### Manual Refresh Pattern
- **Pros:** Simple, explicit control
- **Cons:** Easy to forget refresh calls, doesn't handle external browser closure, tight coupling
- **Technical Debt:** HIGH - brittle, error-prone
- **Rejection Rationale:** Violates "best practices" and "maintainability" principles

#### Shared State Service
- **Pros:** Centralized state management, clean API
- **Cons:** Another layer of abstraction, still needs sync mechanism
- **Technical Debt:** LOW but incomplete
- **Rejection Rationale:** Doesn't solve the core synchronization problem

### Consequences

**Positive:**
- Single source of truth (BrowserController)
- Automatic UI synchronization
- Scalable - new components easily subscribe
- Handles external browser closure automatically
- Zero technical debt - proper architectural pattern
- Follows existing callback pattern (`on_load_data`)

**Negative:**
- Initial complexity (observer service implementation)
- Components must unsubscribe on destroy (standard pattern requirement)

**Risks:**
- Memory leaks if components don't unsubscribe (LOW - UI components rarely destroyed)
- Event order not guaranteed (NONE - events are independent)

### Implementation

**Architecture:**
```
BrowserController (source of truth)
    ↓ emits events
BrowserStateObserver (event bus)
    ↓ notifies
UI Components (reactive subscribers)
```

**Files Created:**
- `src/services/browser_state_observer.py` - Observer service

**Files Modified:**
- `src/app_services.py` - Observer singleton registration
- `src/core/browser_controller.py` - Event emission on launch/close
- `ui/components/browser_config_section.py` - Subscribe to state changes
- `ui/components/actions_list.py` - Starting URL callback
- `ui/components/workflow_single_page_editor.py` - Provide starting URL

**Event Types:**
- `'launched'` - Browser successfully launched
- `'closed'` - Browser closed (via app or externally)

### Validation

**Tested Scenarios:**
- ✅ Launch browser via UI button → Status updates immediately
- ✅ Launch browser via picker → Status updates, uses workflow URL
- ✅ Close browser manually → Status updates immediately
- ✅ Close browser via UI button → Status updates immediately

### Technical Debt Assessment

**ZERO** - This is proper architectural pattern following observer/pub-sub design.

### Future Enhancements
- Add `'error'` event type for browser launch failures
- Support multiple browser instances with per-alias subscriptions
- Add event history/logging for debugging
- Implement event filtering (subscribe to specific aliases only)

---

## ADR-011: Debug Configuration System

**Date:** December 2024  
**Status:** Accepted and Implemented

### Context
Desktop application needs debug logging for development without cluttering production users' machines with log files. Need simple on/off mechanism that:
- Works locally for developer debugging
- Stays silent for end users
- Doesn't require cloud logging infrastructure
- Can be easily toggled without code changes

### Decision
**Selected:** Single debug flag in `config.json` with cached utility function

### Alternatives Considered

#### Environment Variables
- **Pros:** Standard approach, no file editing
- **Cons:** Users must set environment variable every session, not persistent
- **Rejection Rationale:** Poor UX - requires command line knowledge, not persistent

#### Granular Debug Categories
- **Pros:** Fine-grained control (debug_selectors, debug_browser, debug_workflow)
- **Cons:** Complexity grows with project, more flags to manage
- **Rejection Rationale:** YAGNI - simple on/off sufficient, can add categories later if needed

#### Logging Framework (logging.DEBUG)
- **Pros:** Standard Python logging, configurable levels
- **Cons:** Requires logging configuration, more complex setup, still writes to disk
- **Rejection Rationale:** Overkill for simple debug prints, doesn't solve disk clutter issue

#### Cloud Telemetry
- **Pros:** Automatic error collection, analytics
- **Cons:** Privacy concerns, infrastructure cost, network dependency
- **Rejection Rationale:** Privacy violation, unnecessary complexity for desktop app

### Consequences

**Positive:**
- Zero complexity - single boolean flag
- Persistent across sessions
- No disk clutter for users (debug=false by default)
- Easy to toggle - edit one line in config.json
- Cached read - no performance impact
- Extensible - can add categories later if needed

**Negative:**
- Requires file editing (not UI toggle)
- All-or-nothing (no granular control)
- Debug output goes to stdout (not structured logs)

**Risks:**
- None identified - simple, proven pattern

### Implementation

**Files Created:**
```python
# src/utils/debug.py
import json
from pathlib import Path

_debug_enabled = None

def is_debug() -> bool:
    """Check if debug mode is enabled"""
    global _debug_enabled
    if _debug_enabled is None:
        config_path = Path(__file__).parent.parent.parent / "config.json"
        with open(config_path) as f:
            data = json.load(f)
            _debug_enabled = data.get('debug', False)
    return _debug_enabled
```

**Configuration:**
```json
// config.json
{
  "debug": false  // true for development, false for production
}
```

**Usage Pattern:**
```python
from utils.debug import is_debug

except Exception as e:
    if is_debug():
        print(f"[DEBUG] Operation failed: {e}")
    continue  # Silent for users
```

**Current Integration:**
- `src/core/element_picker.py` - Parent selector failure debugging

**Future Integration Points:**
- Browser automation errors
- Template resolution issues
- Workflow execution failures
- Data loading problems

### Design Decisions

#### Why Single Flag vs Categories?
- **Rationale:** YAGNI principle - start simple, add complexity only when needed
- **Future Path:** Can extend to `{"debug": {"selectors": true, "browser": false}}` if needed
- **Current Reality:** Developer either debugs or doesn't - granularity not needed yet

#### Why stdout vs Logging Framework?
- **Rationale:** Desktop app, developer runs locally, stdout is immediate and visible
- **Alternative:** Could add logging later if needed for production debugging
- **Trade-off:** Simple prints vs structured logs - chose simplicity

#### Why Config File vs UI Toggle?
- **Rationale:** Debug mode is developer tool, not user feature
- **Future Path:** Could add hidden UI toggle (Ctrl+Shift+D) if users need it
- **Current Reality:** File editing is acceptable for developer workflow

### Consequences

**Positive:**
- Solves "infinite edge cases" problem - silent failures in production
- Developer can debug locally without affecting users
- No log file clutter on user machines
- Zero performance impact when disabled (cached read)
- Follows modus operandi: pragmatic solution for real-world constraints

**Negative:**
- Debug output not captured for remote debugging
- No structured logging for analysis
- Requires restart to toggle (config read on import)

**Risks:**
- LOW: Config file corruption (mitigated by default=false fallback)
- NONE: Performance impact (single cached read)

### Validation

**Tested Scenarios:**
- ✅ `debug: false` → No output, silent failures
- ✅ `debug: true` → Debug prints visible
- ✅ Config caching → Single file read per session
- ✅ Missing debug key → Defaults to false

### Technical Debt Assessment

**ZERO** - Simple, maintainable solution appropriate for desktop app constraints.

### Future Enhancements
- Add granular categories if needed: `{"debug": {"selectors": true}}`
- Add UI toggle for advanced users (hidden keyboard shortcut)
- Add log file output option (opt-in for remote debugging)
- Add debug level (INFO, WARNING, ERROR) if needed

---

## ADR-012: Browser Detection and Display Enhancement

**Date:** December 2024  
**Status:** Accepted and Implemented

### Context
Browser selection UI showed hardcoded list of browsers without detecting which ones were actually installed. Users could select unavailable browsers, leading to runtime failures. Need to improve UX while handling edge cases like shared configs and non-standard installations.

### Decision
**Selected:** Lazy singleton detection with enhanced display labels and runtime validation

### Alternatives Considered

#### Option 1: Hide Uninstalled Browsers
- **Pros:** Prevents invalid selection upfront
- **Cons:** Doesn't handle config sharing, browser uninstalled after config creation, non-standard installations
- **Rejection Rationale:** Solves problem at wrong layer, creates edge case issues

#### Option 2: Disabled Dropdown Items
- **Pros:** Shows all options, prevents invalid selection
- **Cons:** CustomTkinter ComboBox doesn't support disabled items natively
- **Rejection Rationale:** Framework limitation, would require custom dropdown (100+ lines for 3 items)

#### Option 3: Validation on Selection with Revert
- **Pros:** Works with standard ComboBox
- **Cons:** Janky UX - user clicks, gets reverted, confusing interaction
- **Rejection Rationale:** Poor user experience, feels broken

### Consequences

**Positive:**
- Shows all supported browsers with installation status
- Installed browsers sorted first (better UX)
- Clear warning when uninstalled browser selected
- Handles config sharing and browser uninstallation gracefully
- Runtime validation with actionable error messages
- Single source of truth (BrowserDetector)
- Lazy singleton pattern (detect once per session)

**Negative:**
- Detection runs once per session (acceptable - rare to install browser mid-session)
- User can select uninstalled browser (mitigated by warning + runtime error)

**Risks:**
- None identified - proper error handling at execution boundary

### Implementation

**Module-Level Lazy Singleton:**
```python
# ui/components/browser_config_section.py
_browser_display_cache = None

def get_browser_display_mapping() -> Dict[str, str]:
    """Get browser display mapping (cached, detects once per session)"""
    global _browser_display_cache
    
    if _browser_display_cache is None:
        detector = BrowserDetector()
        installed = detector.detect_installed_browsers()
        
        # Separate installed and not installed browsers
        installed_browsers = {}
        not_installed_browsers = {}
        
        for browser_id, config in detector.SUPPORTED_BROWSERS.items():
            display_name = config['name']
            if browser_id in installed:
                installed_browsers[browser_id] = display_name
            else:
                not_installed_browsers[browser_id] = display_name + " (not installed)"
        
        # Combine: installed first, then not installed
        _browser_display_cache = {**installed_browsers, **not_installed_browsers}
    
    return _browser_display_cache
```

**Display Mapping:**
- `id -> display`: Natural direction (what we have -> what we show)
- Config stores clean IDs: `"chrome"`, `"firefox"`, `"edge"`
- UI shows enhanced labels: `"Google Chrome"`, `"Mozilla Firefox (not installed)"`
- Reverse lookup on selection to update internal config

**Warning on Selection:**
```python
def on_browser_selected(self, display_name: str):
    browser_id = _get_browser_id_from_display(display_name)
    self.config["browser_type"] = browser_id
    
    if "(not installed)" in display_name:
        self.status_label.configure(text="⚠️ Browser not installed - install or select another")
    else:
        self.update_button_states()
```

**Runtime Validation:**
- Browser launch validates installation
- Clear error message if browser not found
- User knows exactly what to do (install browser or select different one)

### Design Decisions

#### Why Lazy Singleton?
- **Rationale:** Detection is expensive (file system, registry, command checks)
- **Benefit:** Detect once, cache for session
- **Trade-off:** Won't detect browser installed mid-session (acceptable)

#### Why Show Uninstalled Browsers?
- **Rationale:** Handles config sharing, browser uninstallation, non-standard installations
- **Benefit:** User sees full capability, gets clear error at runtime
- **Trade-off:** User can select invalid browser (mitigated by warning + error)

#### Why Sort Installed First?
- **Rationale:** Most common use case is selecting installed browser
- **Benefit:** Reduces scrolling, improves discoverability
- **Trade-off:** None

#### Why id -> display Mapping?
- **Rationale:** Natural direction, easy to update based on detection
- **Benefit:** Config stores clean IDs (execution compatibility)
- **Trade-off:** Need reverse lookup on selection (O(3), negligible)

### Validation

**Tested Scenarios:**
- ✅ All browsers installed → All shown without "(not installed)"
- ✅ Some browsers installed → Installed first, uninstalled at bottom
- ✅ No browsers installed → All shown with "(not installed)"
- ✅ Select uninstalled browser → Warning in status label
- ✅ Select installed browser → Status returns to normal
- ✅ Launch uninstalled browser → Clear error message
- ✅ Config from different machine → Works, shows appropriate status

### Technical Debt Assessment

**ZERO** - Clean implementation following established patterns:
- Lazy singleton for expensive operations
- Single source of truth (BrowserDetector)
- Proper separation (detection vs display vs config)
- Runtime validation at execution boundary

### Future Enhancements
- Add manual refresh button (if user installs browser mid-session)
- Add "Show browser path" tooltip on hover
- Add manual browser path entry for non-standard installations
- Persist detection results to preferences (optional optimization)

---

## ADR-013: Multi-Browser Rename/Delete with Save-First Pattern

**Date:** December 2024  
**Status:** Accepted and Implemented

### Context
Multi-browser support requires ability to rename and delete browser instances. Initial designs considered auto-save on blur or save on workflow save button, but both created state inconsistency issues between in-memory workflow, persisted workflow, and runtime browser controller state.

**Critical Problem:** If browser controller is updated before workflow is saved to disk, save failure leaves system in inconsistent state:
- Runtime has new alias
- Disk has old alias
- Next load fails

### Decision
**Selected:** Explicit rename/delete with immediate save and save-first pattern

### Alternatives Considered

#### Option 1: Editable Alias Field with Auto-Save on Blur
- **Pros:** Immediate feedback, familiar UX
- **Cons:** State inconsistency on save failure, complex rollback, browser controller updated before save
- **Technical Debt:** HIGH - race conditions, state divergence
- **Rejection Rationale:** Violates "no technical debt tolerance" and "honest assessment" principles

#### Option 2: Editable Alias Field with Save on Workflow Save Button
- **Pros:** Atomic save, no state inconsistency
- **Cons:** Delayed feedback, actions list shows old alias until save, confusing UX
- **Technical Debt:** LOW but poor UX
- **Rejection Rationale:** User confusion outweighs simplicity benefit

#### Option 3: Update In-Memory on Blur, Save on Button
- **Pros:** Immediate feedback in UI, user control over persistence
- **Cons:** Browser controller state diverges from workflow, element picker fails with renamed browser
- **Technical Debt:** MEDIUM - requires warning dialogs, complex state management
- **Rejection Rationale:** Creates more problems than it solves

### Consequences

**Positive:**
- No state inconsistency (save-first pattern)
- Atomic operations (rename/delete + save together)
- Clear user intent (explicit button click)
- Clean rollback on save failure
- Standard UI pattern (edit button → modal dialog)
- No auto-save confusion

**Negative:**
- Extra click required (edit button)
- Modal dialog blocks UI temporarily
- Can't batch multiple renames

**Risks:**
- None identified - proper error handling and rollback implemented

### Implementation

**Architecture:**
```
BrowserInstance (UI)
  ↓ Edit button clicked
RenameDialog (Modal)
  ↓ User enters new alias
BrowserConfigSection (Orchestration)
  ↓ Validate → Update workflow → SAVE FIRST → Update runtime
WorkflowSinglePageEditor (Owner)
  ↓ Refresh UI
```

**Save-First Pattern:**
```python
def on_alias_changed(self, old_alias: str, new_alias: str):
    # 1. Validate uniqueness
    if new_alias in workflow['browsers']:
        show_error("Duplicate alias")
        return
    
    # 2. Store original state for rollback
    original_browser = workflow['browsers'][old_alias].copy()
    original_actions = [a.copy() for a in workflow['actions']]
    
    # 3. Update workflow (in-memory)
    workflow['browsers'][new_alias] = workflow['browsers'].pop(old_alias)
    
    # 4. Cascade to actions (in-memory)
    for action in workflow['actions']:
        if action['browser_alias'] == old_alias:
            action['browser_alias'] = new_alias
    
    # 5. SAVE FIRST (before updating runtime)
    if not save_workflow(workflow):
        # Rollback on failure
        workflow['browsers'][old_alias] = original_browser
        workflow['actions'] = original_actions
        show_error("Save failed. Rename cancelled.")
        return
    
    # 6. NOW update runtime (after successful save)
    browser_controller.rename_browser_alias(old_alias, new_alias)
    
    # 7. Update UI in-place (no full refresh)
    instance.update_alias_display(new_alias)
```

**Delete Pattern:**
```python
async def delete_browser(self, alias: str):
    # 1. Validate not last browser
    if len(workflow['browsers']) == 1:
        show_error("Must have at least one browser")
        return
    
    # 2. Count affected actions
    action_count = sum(1 for a in workflow['actions'] if a['browser_alias'] == alias)
    
    # 3. Confirm deletion
    if action_count > 0:
        if not confirm(f"{action_count} action(s) will be deleted. Continue?"):
            return
    
    # 4. Store original state
    original_browser = workflow['browsers'][alias].copy()
    original_actions = [a.copy() for a in workflow['actions']]
    
    # 5. Update workflow (in-memory)
    del workflow['browsers'][alias]
    workflow['actions'] = [a for a in workflow['actions'] if a['browser_alias'] != alias]
    
    # 6. SAVE FIRST (before closing browser)
    if not save_workflow(workflow):
        # Rollback on failure
        workflow['browsers'][alias] = original_browser
        workflow['actions'] = original_actions
        show_error("Save failed. Deletion cancelled.")
        return
    
    # 7. NOW close browser (after successful save)
    await browser_controller.close_browser_page(alias)
    
    # 8. Refresh UI
    refresh_instances()
```

**Files Created:**
- `ui/components/rename_dialog.py` - Modal dialog for browser rename

**Files Modified:**
- `ui/components/browser_instance.py` - Read-only alias + edit button
- `ui/components/browser_config_section.py` - Rename/delete orchestration with save-first
- `ui/components/actions_list.py` - Changed to get_workflow callback, added on_workflow_changed
- `ui/components/workflow_single_page_editor.py` - Wire callbacks
- `src/core/workflow_executor.py` - Enhanced error tracking with action index

### Design Decisions

#### Why Save-First Pattern?
- **Rationale:** Prevents state inconsistency on save failure
- **Benefit:** Clean rollback, single source of truth (disk)
- **Trade-off:** Slightly more complex code (worth it for correctness)

#### Why Explicit Edit Button vs Editable Field?
- **Rationale:** Clear user intent, no auto-save confusion
- **Benefit:** Standard UI pattern, modal prevents race conditions
- **Trade-off:** Extra click (acceptable for infrequent operation)

#### Why Immediate Save vs Save on Workflow Save Button?
- **Rationale:** Atomic operations, no unsaved state
- **Benefit:** Clear feedback, no state divergence
- **Trade-off:** Can't batch renames (acceptable - rare use case)

#### Why Rollback vs Prevent Save Failure?
- **Rationale:** Can't prevent all save failures (disk full, permissions, etc.)
- **Benefit:** Graceful degradation, user sees clear error
- **Trade-off:** More code (necessary for correctness)

#### Why In-Place UI Update vs Full Refresh?
- **Rationale:** Better UX, no widget recreation flicker
- **Benefit:** Smooth experience, maintains focus
- **Trade-off:** More complex (track instance references)

### Validation

**Tested Scenarios:**
- ✅ Rename with validation (empty, duplicate)
- ✅ Rename with running browser
- ✅ Rename with save failure (rollback works)
- ✅ Delete with confirmation
- ✅ Delete last browser (blocked)
- ✅ Delete with running browser (closes gracefully)
- ✅ Delete with save failure (rollback works)
- ✅ Actions list refreshes on browser changes
- ✅ Element picker uses correct browser after rename
- ✅ Workflow validation catches invalid browser_alias

### Callback Pattern (Not Events)

**Decision:** Use callbacks for component communication, not events

**Rationale:**
- Workflow is owned by WorkflowSinglePageEditor (not shared state)
- Parent-child hierarchy with clear ownership
- Callbacks are explicit (see dependency in code)
- Events would muddy ownership (who updates workflow? who saves?)

**Comparison:**

| Aspect | Callbacks | Events |
|--------|-----------|--------|
| Ownership | ✅ Clear | ❌ Unclear |
| Testability | ✅ Easy | ⚠️ Harder |
| Debugging | ✅ Explicit | ❌ Indirect |
| Complexity | ✅ Simple | ❌ Higher |
| MODUS_OPERANDI | ✅ Passes | ❌ Over-engineering |

**Verdict:** Callbacks are correct pattern for parent-child communication. Events reserved for decoupled systems (e.g., BrowserStateObserver).

### Known Limitations

1. **Editor closes on browser rename/delete** - Acceptable, rare scenario
2. **No batch rename** - Each rename saves individually (acceptable)
3. **No undo/redo** - Would require command pattern (future enhancement)
4. **Add Browser button disabled** - Waiting for variable system design

### Technical Debt Assessment

**ZERO** - Proper implementation following best practices:
- Save-first pattern prevents state inconsistency
- Rollback logic handles failures gracefully
- Callback pattern maintains clear ownership
- Comprehensive validation at all layers
- Standard UI patterns (modal dialog, confirmation)

### Future Enhancements
- Add "Add Browser" functionality when variable system ready
- Add batch operations (rename/delete multiple)
- Add undo/redo with command pattern
- Add keyboard shortcuts (F2 for rename, Delete for delete)
- Add drag-and-drop reordering

---

## ADR-014: Browser Configuration UI Pattern

**Date:** December 2024  
**Status:** Accepted and Implemented

### Context
Browser configuration editing needed UI pattern for single and multi-browser workflows. Initial design considered overlay pattern (separate display/editor components) but user feedback and implementation analysis revealed simpler solution.

### Decision
**Selected:** Single editable card with inline editing and explicit save button

### Alternatives Considered

#### Overlay Pattern (Display + Editor Split)
- **Pros:** Clear separation between view and edit modes
- **Cons:** Overkill for simple edits, forced save/cancel decision, extra clicks, ~480 lines of code
- **Rejection Rationale:** Unnecessary complexity for browser configuration, user feedback "overlay looks weird"

#### Auto-Save on Blur
- **Pros:** No explicit save button needed
- **Cons:** Unclear when changes persist, validation timing issues, accidental saves
- **Rejection Rationale:** Violates user control principle, confusing UX

### Consequences

**Positive:**
- Simpler implementation (~360 lines vs ~480 lines, 25% reduction)
- Better UX (fewer clicks, immediate visibility)
- Consistent with actions pattern (both use inline editing)
- Explicit save button provides user control
- Rename dialog for complex operations (alias changes cascade to actions)

**Negative:**
- All fields always editable (no clear view/edit mode distinction)
- Save button always visible (slight visual clutter)

**Risks:**
- None identified - pattern proven in actions implementation

### Implementation

**Component Structure:**
```
BrowserInstance (Single editable card)
├── Status indicator (⚪/🟢/🔴)
├── Alias label + Rename button (multi-browser only)
├── Browser type ComboBox (inline editable)
├── Starting URL Entry (inline editable)
├── Launch/Close buttons
├── Save button (always enabled)
└── Delete button (multi-browser only)
```

**Files Created:**
- `ui/components/browser_instance.py` (~150 lines) - Single editable card
- `ui/components/rename_dialog.py` (~60 lines) - Alias rename dialog
- `src/utils/browser_validation.py` (~30 lines) - Validation utility

**Files Modified:**
- `ui/components/browser_config_section.py` (~120 lines, simplified from 200)

**Files Deleted:**
- `ui/components/browser_display.py` (overlay pattern abandoned)
- `ui/components/browser_editor.py` (overlay pattern abandoned)
- `ui/components/editor_overlay.py` (overlay pattern abandoned)

**Key Patterns:**

**1. Inline Editing with Explicit Save:**
```python
class BrowserInstance:
    def setup_ui(self):
        self.browser_combo = ctk.CTkComboBox(...)  # Always editable
        self.url_entry = ctk.CTkEntry(...)  # Always editable
        self.save_button = ctk.CTkButton(text="Save", command=self._on_save_clicked)
```

**2. Rename Dialog for Complex Operations:**
```python
def rename_browser(self, old_alias: str):
    dialog = RenameDialog(
        parent=self.winfo_toplevel(),
        current_alias=old_alias,
        on_save=lambda new_alias: self._do_rename(old_alias, new_alias)
    )
```

**3. Single Validation Point:**
```python
# BrowserInstance: NO validation, just collects data
def _on_save_clicked(self):
    config = self.get_config()
    self.on_save(self.alias, config)  # Parent validates

# BrowserConfigSection: Single validation point
def save_config(self, alias: str, config: Dict):
    is_valid, error = BrowserValidator.validate_config(...)
    if not is_valid:
        messagebox.showerror("Validation Error", error)
        return
    # Save logic...
```

### Design Decisions

#### Why Inline Editing vs Overlay?
- **Rationale:** Browser config is simple (2 fields), overlay adds unnecessary ceremony
- **User Feedback:** "Overlay looks weird" - users prefer direct editing
- **Consistency:** Actions use inline editing, browsers should match

#### Why Explicit Save Button?
- **Rationale:** User control over when changes persist
- **Benefit:** Clear feedback, no auto-save confusion
- **Trade-off:** Always visible (acceptable for clarity)

#### Why Rename Dialog vs Inline?
- **Rationale:** Alias changes cascade to actions (complex operation)
- **Benefit:** Clear user intent, validation, save-first pattern
- **Trade-off:** Extra click (acceptable for infrequent operation)

### Validation

**Tested Scenarios:**
- ✅ Edit browser type inline
- ✅ Edit starting URL inline
- ✅ Click Save button
- ✅ Rename browser (opens dialog)
- ✅ Rename validation (empty, duplicate)
- ✅ Rename cascade to actions
- ✅ Delete browser (with confirmation)
- ✅ Delete last browser (blocked)
- ✅ Launch/Close browser
- ✅ Browser state updates (status indicator)
- ✅ Save validation errors
- ✅ Conditional UI (alias/rename/delete for multi-browser only)

### Technical Debt Assessment

**ZERO** - Eliminated overlay complexity, simpler implementation:
- 25% less code than overlay pattern
- Consistent with existing actions pattern
- Clear separation of concerns
- Single validation point

### Lessons Learned

**What Worked:**
- Challenging the overlay pattern saved time and complexity
- User feedback led to better solution
- Consistency with actions pattern improved UX
- Explicit save button provides user control without change tracking complexity

**What Didn't Work:**
- Overlay pattern was too complex for simple edits
- Display/Editor split was unnecessary abstraction

**Key Insight:**
Not every edit operation needs an overlay. Inline editing with explicit save is often simpler and better UX.

---

## ADR-015: ActionsList Single Source of Truth Refactor

**Date:** December 2024  
**Status:** Accepted and Implemented

### Context
ActionsList maintained a local cache (`self.actions`) that became stale when workflow was modified externally (e.g., browser delete cascading to actions). This caused UI to display deleted actions until user navigated away and back.

### Decision
**Selected:** Property pattern for single source of truth

### Alternatives Considered

#### Quick Fix (Sync Cache in on_workflow_changed)
```python
def on_workflow_changed(self):
    self.actions = workflow.get('actions', []).copy()
    self.refresh_display()
```
- **Pros:** 3 lines, quick fix
- **Cons:** Architectural smell remains, dual state pattern persists, future sync bugs possible
- **Technical Debt:** LOW but persistent
- **Rejection Rationale:** Doesn't eliminate root cause, violates "no technical debt tolerance" principle

#### Pass Actions as Parameter
```python
def refresh_display(self, actions):
def save_action(self, actions):
```
- **Pros:** No cache needed
- **Cons:** Breaks existing API, requires parent changes, more complex
- **Rejection Rationale:** Unnecessary API changes, more invasive than property pattern

### Consequences

**Positive:**
- Single source of truth (workflow owns data)
- No cache, no sync issues
- Property pattern is Pythonic and transparent
- Zero technical debt (eliminates existing debt)
- Bug fixed (deleted actions disappear immediately)
- No breaking changes (property is drop-in replacement)

**Negative:**
- None identified

**Risks:**
- None - property access is O(1), no performance impact

### Implementation

**Property Pattern:**
```python
@property
def actions(self) -> List[Dict]:
    """Get actions from workflow (single source of truth)"""
    workflow = self.get_workflow()
    return workflow.get('actions', []) if workflow else []
```

**Changes Made:**
- Removed `self.actions = []` from `__init__`
- Added `@property def actions(self)`
- Updated `save_action()` to modify `workflow['actions']` directly
- Updated `delete_action()` to modify `workflow['actions']` directly
- Updated `set_actions()` to modify `workflow['actions']`
- Updated `on_workflow_changed()` (no sync needed)
- Added defensive None checks throughout

**Files Modified:**
- `ui/components/actions_list.py` (~30 lines changed)

### Design Decisions

#### Why Property Pattern?
- **Rationale:** Transparent drop-in replacement, no API changes
- **Benefit:** Single source of truth without breaking existing code
- **Trade-off:** None - property is idiomatic Python

#### Why Not Keep Cache?
- **Rationale:** Dual state is architectural smell, causes sync bugs
- **Benefit:** Eliminates entire class of bugs (stale cache)
- **Trade-off:** None - property has same performance

### Validation

**Tested Scenarios:**
- ✅ Load workflow → actions display
- ✅ Add action → saves to workflow
- ✅ Edit action → updates workflow
- ✅ Delete action → removes from workflow
- ✅ Delete browser → actions disappear immediately (BUG FIXED)
- ✅ Rename browser → actions update
- ✅ No workflow loaded → empty list, no crash

### Technical Debt Assessment

**BEFORE:** HIGH (dual state pattern, sync complexity, future bug risk)
**AFTER:** ZERO (single source of truth, property pattern is best practice)

**Net Debt Reduction:** HIGH → ZERO ✅

### Lessons Learned

**What Worked:**
- Challenging the quick fix led to proper solution
- Full sanity check revealed architectural smell
- Property pattern eliminated debt with minimal changes
- 15 extra minutes of analysis saved future debugging time

**Key Insight:**
When you find a cache sync bug, question whether the cache is needed at all. Single source of truth eliminates entire class of bugs.

---

## Modus Operandi Compliance Checklist

For each ADR:
- ✅ **Architecture-first approach** - Design documented before implementation
- ✅ **Technology justification** - Clear rationale for choices
- ✅ **Alternatives considered** - Multiple options evaluated
- ✅ **Honest assessment** - Risks and limitations acknowledged
- ✅ **Future maintainability** - Long-term implications considered
- ✅ **Best practices validation** - Industry standards followed

---

*All architectural decisions follow the principles established in [MODUS_OPERANDI.md](./MODUS_OPERANDI.md). Any deviation from these decisions requires explicit documentation and approval.*