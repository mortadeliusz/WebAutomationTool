# Testing Checklist - Mini-Controller Implementation

## Workflow List View

- [ ] Page loads with workflow list visible
- [ ] Empty state shows "No workflows yet" message
- [ ] Workflow cards display correctly (name, action count, browser type)
- [ ] "New Workflow" button is visible at bottom
- [ ] Edit button on each card works
- [ ] Delete button (🗑️) on each card works
- [ ] List refreshes after delete

## Workflow Editor View

- [ ] Clicking "New Workflow" shows editor with empty form
- [ ] Clicking "Edit" on workflow card loads workflow data
- [ ] Back button (← Back) returns to list view
- [ ] Workflow name input works
- [ ] Browser configuration section displays correctly
- [ ] Actions list displays correctly
- [ ] Save button persists changes
- [ ] After save, returns to list view
- [ ] List view shows updated workflow

## View Switching

- [ ] List view → Editor view transition is smooth
- [ ] Editor view → List view transition is smooth
- [ ] No visual glitches during transitions
- [ ] Grid layout works correctly (full screen for each view)
- [ ] No components overlap during transitions

## Actions Section (Inline Editing)

- [ ] Actions list displays existing actions
- [ ] "Add Action" button shows inline editor
- [ ] Inline editor displays below actions list
- [ ] Action type dropdown works
- [ ] Dynamic fields appear based on action type
- [ ] Element picker button works (🎯)
- [ ] Save button adds action to list
- [ ] Cancel button hides inline editor
- [ ] Actions list stays visible during editing

## Integration

- [ ] Browser config section works in editor view
- [ ] Browser launch/close buttons work
- [ ] Status indicators update correctly
- [ ] Workflow saves with all data (name, browser, actions)
- [ ] Workflow loads with all data intact
- [ ] No console errors during normal operation

## Edge Cases

- [ ] Creating workflow with empty name (should default to "Unnamed Workflow")
- [ ] Deleting last workflow (should show empty state)
- [ ] Editing workflow and clicking back without saving (data not persisted)
- [ ] Rapid clicking between list and editor (no race conditions)
- [ ] Long workflow names display correctly
- [ ] Many actions (10+) display correctly in scrollable area

## Performance

- [ ] List view loads quickly (< 1 second)
- [ ] Editor view loads quickly (< 1 second)
- [ ] View transitions are instant (no lag)
- [ ] Scrolling is smooth in both views
- [ ] No memory leaks during repeated view switching

## Cleanup Verification

- [ ] Old components (WorkflowListPanel, WorkflowEditorPanel) can be removed
- [ ] StatusBar component no longer needed in workflow management
- [ ] No broken imports in other files
- [ ] All new components follow project structure conventions
