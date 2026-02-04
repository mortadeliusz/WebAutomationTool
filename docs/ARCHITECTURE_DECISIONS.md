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