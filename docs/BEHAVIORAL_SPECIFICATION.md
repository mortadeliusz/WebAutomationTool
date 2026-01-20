# Web Automation Tool - Behavioral Specification

## Project Overview

**Purpose:** Desktop application enabling non-technical users to automate repetitive browser tasks through visual task creation and data-driven execution.

**Target Users:** General consumers requiring web form automation for 30-150 rows of data entry without development skills.

**Core Value Proposition:** Transform hours of manual data entry into minutes of automated execution.

---

## Core Behavioral Requirements

### **1. Data Input & Management**

**Data Loading Capabilities:**
- File upload support: CSV, Excel (.xlsx), JSON, YAML
- Copy/paste text input with format auto-detection
- Real-time data preview (first 5-10 rows)
- Column mapping and validation
- Format conversion and normalization

**Data Processing Behaviors:**
- Automatic delimiter detection for CSV
- JSON flattening with dot notation (`user.contact.email`)
- Missing data handling with fallback values
- Data type inference and validation

### **Task Creation & Management**

**Task Structure:**
- Reusable automation templates stored as JSON
- Immediate disk persistence on action saves
- User-controlled save operations (no auto-save)
- Task sharing and duplication capabilities

**Interactive Task Building:**
- Visual element selection through browser interaction
- Real-time selector generation and validation
- Action sequence definition with descriptions
- Template variable integration for data mapping
- Auto-close editor switching between actions

### **3. Browser Session Management**

**Persistent Browser Sessions:**
- Browser remains active during entire task editing session
- User can navigate pages between element selections
- Authentication state preserved across interactions
- Multiple element picks without session restart

**Focus Management Protocol:**
1. User initiates element picker from application
2. Application focuses browser window
3. User selects element in browser
4. Selector generated and returned to application
5. Application regains focus
6. Browser remains available for continued navigation

### **4. Element Selector Generation Algorithm**

**Priority Hierarchy:**
1. **Testing Attributes** (Highest Priority)
   - `data-testid`, `data-cy`, `data-test`
   - `data-automation`, `data-qa`
   - Other `data-*` testing attributes

2. **Semantic Attributes**
   - `id` (if not random)
   - `name` attribute
   - `type` attribute
   - `role` and `aria-label`

3. **Structural Selectors**
   - Tag name + meaningful attributes
   - Class names (if semantic)
   - Text content (for buttons/links)

**Validation Pipeline:**

**Randomness Filtering:**
- Reject auto-generated identifiers
- Accept only semantic naming patterns:
  - Simple: `header`, `modal`
  - Kebab-case: `login-form`, `submit-button`
  - CamelCase: `loginForm`, `submitButton`
  - Snake_case: `login_form`, `submit_button`
  - PascalCase: `LoginForm`, `SubmitButton`

**Uniqueness Verification:**
- Test selector against current page
- Ensure single element match
- If multiple matches, add parent context
- Recursively validate parent selectors for randomness

**Fallback Strategy:**
- Position-based selectors as last resort
- User warning for brittle selectors
- Alternative selector suggestions when possible

### **5. Template Variable System**

**Syntax Specification:**
- Template detection: `{{...}}` pattern
- Static values: plain text without templates
- Hybrid values: `"user_{{col('Email')}}_2024"`

**Data Access Methods:**
- Column by name: `{{col('Email')}}`
- Column by index: `{{col(0)}}` (0-based)
- Type-based resolution:
  - String parameter = column name
  - Number parameter = column index

**Template Processing:**
- Regex-based detection and replacement
- Row-by-row evaluation during execution
- Error handling for missing columns
- Default value support

### **6. Task Execution Workflow**

**Pre-Execution Validation:**
- Task completeness verification
- Data compatibility checking
- Browser availability confirmation
- User confirmation for destructive actions

**Execution Process:**
- Initialization actions (navigation, authentication)
- Pre-loop setup actions
- Row-by-row data processing with template substitution
- Post-loop cleanup actions
- Progress reporting and user feedback

**Execution Blocking:**
- Task editing disabled during execution
- Clear progress indication
- Cancellation capability
- Error recovery options

### **7. Error Handling Philosophy**

**Graceful Degradation:**
- Application continues functioning when non-critical features fail
- Partial success reporting (X of Y rows completed)
- Recovery suggestions for common failures
- Automatic retry logic for transient errors

**User Communication:**
- Technical errors translated to actionable feedback
- Clear distinction between user errors and system errors
- Step-by-step recovery instructions
- Contact information for unresolvable issues

**Logging Strategy:**
- Detailed technical logs for debugging
- User-friendly progress messages
- Error categorization and reporting
- Performance metrics collection

### **8. User Preference Management**

**"Keep It As I Left It" Philosophy:**
- UI state preservation across sessions
- Last selected task memory
- Window size and position retention
- Theme and display preferences

**Preference Categories:**
- **Explicit Settings:** Theme, default browser, file locations
- **Implicit State:** Last task, UI layout, recent files
- **Session Data:** Window position, panel sizes

**Persistence Strategy:**
- Load preferences on application startup
- Maintain in memory during session
- Save on application close
- Graceful fallback for corrupted preferences

### **9. Security & Privacy Principles**

**Local Processing:**
- All automation logic executed locally
- No data transmission to external servers
- User authentication handled through existing browser sessions
- Task definitions stored locally

**Browser Integration:**
- Use existing user browser installations
- Preserve user authentication and extensions
- Respect browser security policies
- Clean session management

---

## Advanced Features (Post-MVP)

### **Selector Self-Healing**
- Failed selector analysis and decomposition
- Alternative selector generation
- Automatic fallback to working selectors
- User notification of selector changes

### **Conditional Logic**
- If/then/else actions based on page content
- Dynamic data validation
- Branching execution paths
- Error condition handling

### **Batch Operations**
- Multiple task execution
- Parallel processing capabilities
- Resource management and throttling
- Comprehensive reporting

---

## Quality Standards

### **Reliability Expectations**
- Standard form elements: 90% success rate
- Popular UI libraries: 80% success rate
- Custom components: 60% success rate
- Legacy implementations: 40% success rate with manual fallback

### **Performance Targets**
- Application startup: < 3 seconds
- Task execution initiation: < 5 seconds
- Element selector generation: < 2 seconds
- Data processing: 100+ rows per minute

### **User Experience Goals**
- Intuitive task creation without technical knowledge
- Clear progress indication during long operations
- Helpful error messages with recovery suggestions
- Consistent behavior across different websites

---

*This specification defines the core behaviors and algorithms independent of implementation technology. All features should maintain these behavioral characteristics regardless of the chosen technical stack.*