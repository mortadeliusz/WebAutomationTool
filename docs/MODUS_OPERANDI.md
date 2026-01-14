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

*This modus operandi applies to all development work regardless of technology stack or project phase. These principles ensure long-term project success and maintainable code quality.*