# Documentation Update - Domain-Specific Field Components & Data Expression Helper

## Latest Implementation (January 2025)

### **Domain-Specific Field Component Architecture** ✅

**Problem Solved:** Generic field components trying to serve multiple purposes created complexity and conditional logic

**Solution Implemented:** Purpose-built components for each action field type

**Component Structure:**
```
ui/components/fields/
├── action_value_input.py          # Value field with expression helper + help button
├── action_url_input.py            # URL field (future - same pattern as value)
├── action_selector_input.py       # Selector field (future - picker + helper)
├── action_type_selector.py        # Action type dropdown (future rename)
├── action_key_input.py            # Key capture (future rename)
├── action_description_input.py    # Simple description (future)
├── text_input.py                  # Generic text input (legacy)
├── dropdown.py                    # Generic dropdown (legacy)
├── selector_picker.py             # Selector with element picker
├── key_picker.py                  # Key capture component
├── number_input.py                # Numeric validation
└── data_expression_helper.py      # Reusable utility component
```

**Benefits:**
- ✅ **Zero ambiguity** - Component name = exact purpose
- ✅ **No conditionals** - Each component knows exactly what it needs
- ✅ **Easy to find** - "Where's value input?" → `action_value_input.py`
- ✅ **Self-documenting** - Code reads like domain language
- ✅ **Future-proof** - Add new field? Create new component

---

### **Data Sample Status Indicator** ✅

**Problem Solved:** Users didn't understand when/why to load data sample

**Solution Implemented:** Persistent status indicator with clear actions

**Component:** `ui/components/data_sample_status.py`

**States:**

**No Data:**
```
[⚠️ No sample data loaded | Load Data Sample]
```

**Data Loaded:**
```
[✅ sample.csv (10 rows) | ✕ | Replace]
```

**Features:**
- **Always visible** - User always knows data state
- **Actionable** - Click to load/clear/replace
- **Clear feedback** - Visual status indicators
- **Reusable** - Can be used in other pages

**Integration:**
```python
# In WorkflowEditorView header
self.data_status = DataSampleStatus(
    header_frame,
    on_load=self.load_data_sample,
    on_change=self.on_data_changed
)
```

---

### **Session-Level Data Sample Service** ✅

**Problem Solved:** Data sample needs to be shared across multiple helper instances

**Solution Implemented:** Service layer with session-scoped storage

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
- ✅ **No prop drilling** - Components access via service
- ✅ **Single source of truth** - All helpers share same data
- ✅ **Clean lifecycle** - Explicit set/clear
- ✅ **Session-scoped** - Resets on app restart

---

### **Callback Pattern for Data Loading** ✅

**Problem Solved:** Educational popup needs to trigger data loading in parent

**Solution Implemented:** Callback chain from helper to editor

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
    
    def on_load_data_clicked(self):
        if self.on_load_data_callback:
            self.on_load_data_callback()

# ActionsList - passes callback through
class ActionsList:
    def __init__(self, parent, on_actions_changed, on_load_data):
        self.on_load_data = on_load_data
    
    def rebuild_fields(self, action_type):
        component = ActionValueInput(
            ...,
            on_load_data=self.on_load_data
        )

# WorkflowEditorView - owns data loading
class WorkflowEditorView:
    def setup_ui(self):
        self.actions_list = ActionsList(
            content,
            self.on_actions_changed,
            on_load_data=self.load_data_sample
        )
    
    def load_data_sample(self):
        # File picker → Load data → Set in service → Refresh helpers
        set_workflow_data_sample(df.head(10))
        self.on_data_changed()
```

**Benefits:**
- ✅ **Inversion of control** - Child doesn't know about parent
- ✅ **Loose coupling** - Components communicate via callbacks
- ✅ **Follows existing pattern** - Same as element picker
- ✅ **Easy to test** - Mock callbacks for testing

---

### **User Flows** ✅

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

### **Field Definition Updates** ✅

```python
# src/core/action_handlers.py
FIELD_DEFINITIONS = {
    'value': {
        'component': 'action_value_input',  # Changed from 'text_input'
        'label': 'Value',
        'placeholder': 'Type value or click 📊 to insert column'
    },
    'url': {
        'component': 'text_input',  # Will change to 'action_url_input'
        'label': 'URL',
        'placeholder': 'https://example.com or {{col("url")}}'
    },
    'description': {
        'component': 'text_input',  # Stays generic (no helper needed)
        'label': 'Description',
        'placeholder': 'Action description'
    }
}
```

---

### **Modus Operandi Compliance** ✅

**✅ Architecture-first approach:** Discussed domain-specific vs generic components  
**✅ Best practices validation:** Callback pattern, service layer, reusable components  
**✅ YAGNI principle:** Minimal code, no over-engineering  
**✅ Future maintainability:** Easy to add new field types  
**✅ Technical debt awareness:** Zero debt - clean implementation  
**✅ Separation of concerns:** UI, service, business logic properly separated

---

### **Next Steps**

**Phase 2: Add to URL Field**
- Create `action_url_input.py` (copy of action_value_input)
- Update field definition in action_handlers.py

**Phase 3: Add to Selector Field**
- Create `action_selector_input.py` (picker + helper)
- Update field definition in action_handlers.py

**Phase 4: Rename Legacy Components**
- `dropdown.py` → `action_type_selector.py`
- `key_picker.py` → `action_key_input.py`
- Update all references

---

*This implementation provides a clean, maintainable foundation for data expression helpers with zero technical debt and proper separation of concerns.*
