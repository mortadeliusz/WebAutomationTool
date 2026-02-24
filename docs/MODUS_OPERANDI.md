# Development Modus Operandi

## Critical Development Rules

### **Dependency Management:**
- **NEVER** edit `pyproject.toml` directly
- **ALWAYS** use `poetry add <package>` and `poetry remove <package>`
- Maintain clean dependency tree through Poetry's resolver

### **Implementation Protocol:**
- **Discussion first, implementation second** - No code without explicit confirmation
- All architectural decisions must be discussed and approved before coding
- Focus on brainstorming and design validation during discussion phase

### **Feedback Philosophy:**
- **No sugarcoating** - Provide brutal honesty about design flaws and implementation risks
- **Navigate away from corners** - Actively identify and prevent architectural dead ends
- **Challenge bad ideas** - Push back on decisions that compromise maintainability or scalability
- **Prioritize long-term success** over short-term convenience

### **Design Principles:**
- **Best practices first** - Follow established patterns and conventions
- **Future maintainability** - Code for the developer who comes after you
- **Scalability considerations** - Design for growth, not just current requirements
- **Technical debt awareness** - Identify and document trade-offs explicitly

### **Quality Standards:**
- **Proper brainstorming** - Explore alternatives, identify risks, validate assumptions
- **Architectural integrity** - Maintain consistent patterns and separation of concerns
- **Decision documentation** - Record rationale for major technical choices
- **Honest assessment** - Acknowledge limitations and potential failure points

---

## Implementation Standards

### **Pre-Implementation Analysis (MANDATORY):**
- **Architecture-first approach** - Design proper structure before any coding
- **Maintainability check** - "Will I be proud of this code in 6 months?"
- **Best practices validation** - "Does this follow established patterns?"
- **Technical debt assessment** - "Will this create future problems?"
- **Separation of concerns** - Plan file organization and component boundaries
- **Sanity check** - Verify adherence to all modus operandi principles before implementation

### **Code Quality Enforcement:**
- **No shortcuts** - No "quick and dirty" solutions that create technical debt
- **No single-file applications** - Proper separation into logical modules
- **No mixed concerns** - HTML/CSS/JS/Logic must be properly separated
- **No global scope pollution** - Use proper imports and module boundaries
- **No CDN shortcuts** - Use proper dependency management for production code
- **Type hints everywhere** - All functions must have complete type annotations
- **TypedDict for data structures** - Use TypedDict for complex dict structures (workflows, results, configs)

### **Type Safety Standards:**
- **All functions typed** - Parameters and return types must be explicit
- **TypedDict definitions** - Define structure in `src/types.py` for all complex dicts
- **Update TypedDicts first** - When changing data structures, update TypedDict BEFORE implementation
- **No Dict[str, Any] in public APIs** - Use specific TypedDict instead
- **Consistency** - Use same TypedDict across all functions handling that data structure

### **Logging Standards:**
- **Rotating file handler** - 1MB per file, 5 files max (5MB total) in `user_data/logs/`
- **Log to console + file** - Console for development, file for production debugging
- **INFO level default** - Log errors + key operations (startup, workflow execution, shutdown)
- **Critical files only** - main.py, app_services.py, workflow_executor.py (not every module)
- **User-actionable logs** - Users can send log files for bug reports

### **Testing Strategy:**
- **Pre-ship (active development)** - Manual testing via TESTING_CHECKLIST.md, automated tests optional
- **Post-ship (v1.0+)** - Automated tests required for core logic and bug-prone areas
- **Test-after-bug** - Write test for reported bugs before fixing (prevent regressions)
- **Focus on value** - Test core logic (validation, file ops, state), skip UI and browser integration

### **Self-Enforcement Protocol:**
Before any implementation, must provide:
1. **Architecture plan** - File structure and component organization
2. **Technology justification** - Why this approach over alternatives
3. **Scalability consideration** - How this grows with requirements
4. **Maintenance plan** - How this will be updated and extended

### **Implementation Rejection Criteria:**
Reject any approach that:
- Mixes multiple concerns in single files
- Uses shortcuts that compromise long-term maintainability
- Ignores established best practices without justification
- Creates technical debt for short-term convenience
- Cannot be easily extended or modified

---

## Definition of Done

### **Feature Completion Checklist:**
A feature is NOT done until ALL of the following are true:

#### **Code Quality:**
- [ ] Follows separation of concerns (no mixed HTML/CSS/JS/Logic)
- [ ] Proper module structure (no single-file solutions)
- [ ] Clean imports (no global scope pollution)
- [ ] Dependencies managed via Poetry (no manual pyproject.toml edits)
- [ ] Passes the "6-month pride test" - maintainable and clear
- [ ] All functions have type hints (parameters and return types)
- [ ] Complex dict structures use TypedDict (defined in src/types.py)
- [ ] TypedDicts updated if data structure changed

#### **Error Handling:**
- [ ] All failure paths handled gracefully
- [ ] User-facing errors are clear and actionable
- [ ] Logging implemented for debugging (errors, warnings, key operations)
- [ ] No silent failures or swallowed exceptions
- [ ] Specific exceptions caught (no bare `except:` or overly broad `except Exception:`)

#### **Testing:**
- [ ] Manual testing completed using TESTING_CHECKLIST.md
- [ ] Edge cases identified and manually verified
- [ ] No regressions in existing functionality
- [ ] Automated tests written (post-v1.0 only, optional pre-ship)

#### **Documentation:**
- [ ] Code is self-documenting (clear names, obvious structure)
- [ ] Complex logic has inline comments explaining "why" not "what"
- [ ] Module README updated if public API changed
- [ ] Architecture decisions documented if non-obvious
- [ ] TypedDict definitions document data structure contracts

#### **Security & Performance:**
- [ ] User inputs validated and sanitized
- [ ] No hardcoded secrets or credentials
- [ ] No obvious performance bottlenecks
- [ ] Resource cleanup (files, connections, memory)

#### **Version Control:**
- [ ] Atomic, logical commits with clear messages
- [ ] No debug code, commented-out blocks, or temp files
- [ ] No secrets, API keys, or sensitive data in commits

#### **Self-Review:**
- [ ] "Would I approve this in code review?"
- [ ] "Can someone else maintain this without asking me questions?"
- [ ] "Does this follow all modus operandi principles?"
- [ ] "Is this production-ready or just 'working'?"

### **Enforcement:**
- If ANY checkbox is unchecked, the feature is NOT done
- "It works on my machine" is NOT done
- "I'll add tests later" means it's NOT done (post-v1.0)
- "Good enough for now" means it's NOT done

---

## Post-Ship Testing Requirements (v1.0+)

Once the application is shipped and architecture stabilizes:

### **Required Automated Tests:**
- **Core logic** - Workflow validation, template evaluation, data loading
- **File operations** - Workflow save/load, state persistence
- **Bug-reported areas** - Write test before fixing any reported bug
- **Refactoring targets** - Test before refactoring to prevent regressions

### **Optional Tests:**
- UI components (hard to test, changes frequently)
- Browser automation (Playwright's responsibility)
- End-to-end workflows (brittle, slow)

### **Test-Driven Bug Fixes:**
1. User reports bug
2. Write failing test that reproduces bug
3. Fix bug
4. Test passes
5. Bug cannot regress

---

*This modus operandi applies to all development work regardless of technology stack or project phase. These principles ensure long-term project success and maintainable code quality.*
