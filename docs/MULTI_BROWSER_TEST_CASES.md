# Multi-Browser Test Cases

## Test Case 1: Browser Rename - Happy Path
**Steps:**
1. Open workflow editor
2. Click edit button (✏️) next to browser alias
3. Enter new alias: "primary"
4. Click Save in dialog
5. Verify alias updated in UI
6. Verify actions using old alias now show new alias
7. Close and reopen workflow
8. Verify alias persisted correctly

**Expected:** Rename succeeds, cascades to actions, persists to disk

---

## Test Case 2: Browser Rename - Empty Alias
**Steps:**
1. Click edit button
2. Clear alias field (empty)
3. Click Save

**Expected:** Error dialog "Alias cannot be empty", dialog stays open

---

## Test Case 3: Browser Rename - Duplicate Alias
**Setup:** Workflow has browsers "main" and "secondary"

**Steps:**
1. Click edit on "main"
2. Enter "secondary"
3. Click Save

**Expected:** Error dialog "Browser alias 'secondary' already exists", dialog stays open

---

## Test Case 4: Browser Rename - With Running Browser
**Setup:** Browser "main" is running

**Steps:**
1. Rename "main" to "primary"
2. Verify browser continues running
3. Open action editor
4. Click element picker
5. Verify element picker works with renamed browser

**Expected:** Browser continues running under new alias, element picker works

---

## Test Case 5: Browser Rename - Save Failure
**Setup:** Make workflow file read-only (simulate save failure)

**Steps:**
1. Rename browser
2. Observe error dialog

**Expected:** Error "Could not save workflow. Rename cancelled.", workflow unchanged

---

## Test Case 6: Browser Delete - Happy Path
**Setup:** Workflow has 2 browsers, "secondary" has 3 actions

**Steps:**
1. Click delete button (🗑️) on "secondary"
2. Confirm deletion in dialog
3. Verify browser removed from UI
4. Verify 3 actions deleted
5. Close and reopen workflow
6. Verify deletion persisted

**Expected:** Browser and related actions deleted, persists to disk

---

## Test Case 7: Browser Delete - Last Browser
**Setup:** Workflow has only 1 browser

**Steps:**
1. Click delete button

**Expected:** Error dialog "Workflow must have at least one browser", deletion blocked

---

## Test Case 8: Browser Delete - Cancel Confirmation
**Setup:** Browser has 5 actions

**Steps:**
1. Click delete button
2. See confirmation: "5 action(s) use this browser"
3. Click Cancel

**Expected:** Deletion cancelled, nothing changed

---

## Test Case 9: Browser Delete - With Running Browser
**Setup:** Browser "secondary" is running

**Steps:**
1. Delete browser
2. Confirm deletion

**Expected:** Browser closes gracefully, then deleted from workflow

---

## Test Case 10: Browser Delete - Save Failure
**Setup:** Make workflow file read-only

**Steps:**
1. Delete browser
2. Confirm deletion

**Expected:** Error "Could not save workflow. Deletion cancelled.", workflow unchanged

---

## Test Case 11: Action Editor - Single Browser
**Setup:** Workflow has 1 browser

**Steps:**
1. Add new action
2. Verify no browser dropdown shown
3. Save action
4. Verify action has correct browser_alias

**Expected:** Browser auto-assigned, no dropdown needed

---

## Test Case 12: Action Editor - Multiple Browsers
**Setup:** Workflow has 3 browsers

**Steps:**
1. Add new action
2. Verify browser dropdown shown with blank default
3. Try to save without selecting browser
4. Verify error "Please select a browser"
5. Select browser
6. Save action

**Expected:** Browser selection required, validation works

---

## Test Case 13: Action Editor - Browser Renamed While Editing
**Setup:** Action editor open, editing action with browser "main"

**Steps:**
1. In another window/tab, rename "main" to "primary"
2. Return to action editor

**Expected:** Editor closes (acceptable limitation), action shows new alias when reopened

---

## Test Case 14: Action Editor - Browser Deleted While Editing
**Setup:** Action editor open, editing action with browser "secondary"

**Steps:**
1. Delete browser "secondary"
2. Confirm deletion

**Expected:** Editor closes, action deleted (acceptable limitation)

---

## Test Case 15: Element Picker - Multiple Browsers
**Setup:** Workflow has 2 browsers, both running

**Steps:**
1. Create action, select browser "secondary"
2. Click element picker
3. Verify correct browser ("secondary") is used for picking

**Expected:** Element picker uses selected browser

---

## Test Case 16: Element Picker - Browser Not Running
**Setup:** Browser "secondary" not running

**Steps:**
1. Create action, select browser "secondary"
2. Click element picker

**Expected:** Browser auto-launches, element picker works

---

## Test Case 17: Workflow Execution - Multiple Browsers
**Setup:** Workflow has 2 browsers, actions use both

**Steps:**
1. Load data file
2. Execute workflow
3. Verify both browsers launch
4. Verify actions execute on correct browsers

**Expected:** Both browsers launch, actions execute correctly

---

## Test Case 18: Workflow Execution - Error Export
**Setup:** Workflow with actions that will fail

**Steps:**
1. Execute workflow
2. Let some rows fail
3. Check error CSV file

**Expected:** CSV contains: row, action, description, error columns

---

## Test Case 19: Workflow Validation - Missing Browser
**Setup:** Manually edit workflow file, delete browser but keep actions referencing it

**Steps:**
1. Try to open workflow
2. Try to execute workflow

**Expected:** Validation error "Action X references non-existent browser 'Y'"

---

## Test Case 20: Workflow Validation - Empty Browser Alias
**Setup:** Manually edit workflow file, set browser_alias to empty string

**Steps:**
1. Try to execute workflow

**Expected:** Validation error "Action X missing browser_alias"

---

## Test Case 21: Rename Dialog - Keyboard Navigation
**Steps:**
1. Open rename dialog
2. Press Tab to navigate
3. Press Enter to save
4. Press Escape to cancel

**Expected:** Keyboard shortcuts work correctly

---

## Test Case 22: Rename Dialog - Modal Behavior
**Steps:**
1. Open rename dialog
2. Try to click on main window

**Expected:** Dialog blocks interaction with main window (modal)

---

## Test Case 23: Browser Config - Conditional Display
**Setup:** Workflow with 1 browser

**Steps:**
1. Verify alias label NOT shown
2. Verify edit button NOT shown
3. Verify delete button NOT shown

**Expected:** Single browser mode hides multi-browser UI

---

## Test Case 24: Browser Config - Show Alias When Multiple
**Setup:** Add second browser (when feature enabled)

**Steps:**
1. Verify alias labels shown for both
2. Verify edit buttons shown
3. Verify delete buttons shown

**Expected:** Multi-browser UI appears when multiple browsers exist

---

## Test Case 25: Workflow Save - Validation Before Save
**Steps:**
1. Manually corrupt workflow in memory (invalid structure)
2. Click Save Workflow

**Expected:** Validation error shown, save blocked

---

## Performance Tests

### PT-1: Rename with 100 Actions
**Setup:** Workflow with 100 actions using same browser

**Steps:**
1. Rename browser
2. Measure time

**Expected:** Completes in < 1 second

---

### PT-2: Delete with 100 Actions
**Setup:** Workflow with 100 actions using same browser

**Steps:**
1. Delete browser
2. Confirm

**Expected:** Completes in < 1 second

---

## Edge Cases

### EC-1: Rapid Rename Attempts
**Steps:**
1. Open rename dialog
2. Save
3. Immediately open rename dialog again
4. Save

**Expected:** Both renames succeed (modal prevents race)

---

### EC-2: Special Characters in Alias
**Steps:**
1. Rename browser to "Main Browser (Primary)"
2. Verify works correctly

**Expected:** Spaces and special characters allowed

---

### EC-3: Very Long Alias
**Steps:**
1. Rename browser to 100-character string
2. Verify UI handles it

**Expected:** Long alias displays correctly (may truncate in UI)

---

## Regression Tests

### RT-1: Single Browser Workflow Still Works
**Setup:** Existing workflow with single browser

**Steps:**
1. Open workflow
2. Edit actions
3. Execute workflow

**Expected:** No breaking changes, works as before

---

### RT-2: Workflow File Format Compatibility
**Setup:** Workflow file from before multi-browser changes

**Steps:**
1. Load old workflow file

**Expected:** Loads correctly, structure compatible

---

## Test Summary

- **Total Test Cases:** 27
- **Happy Path:** 6
- **Error Handling:** 8
- **Edge Cases:** 3
- **Validation:** 4
- **Performance:** 2
- **Regression:** 2
- **UI/UX:** 2

**Estimated Testing Time:** 3-4 hours for full manual test suite
