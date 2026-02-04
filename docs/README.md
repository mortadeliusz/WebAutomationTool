# Documentation Index

> **Start Here:** This index guides you to the right documentation based on your needs and role.

## **🏛️ Foundation Documents**

### **[MODUS_OPERANDI.md](./MODUS_OPERANDI.md)** - Golden Standard
**Who:** All developers and contributors  
**Purpose:** Core development principles and quality standards  
**When:** Read first, reference always  

---

## **📋 Project Understanding**

### **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)** - Business Focus
**Who:** Product managers, stakeholders, new team members  
**Purpose:** Business requirements, user needs, market positioning  
**Content:** Users, use cases, success metrics, constraints  

### **[BEHAVIORAL_SPECIFICATION.md](./BEHAVIORAL_SPECIFICATION.md)** - User Requirements
**Who:** Developers, testers, UX designers  
**Purpose:** Detailed user requirements and acceptance criteria  
**Content:** User workflows, feature specifications, quality standards  

---

## **🏗️ Technical Documentation**

### **[ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md)** - Decision Records
**Who:** Technical leads, architects, senior developers  
**Purpose:** Technology choices with rationale and alternatives  
**Content:** ADRs for UI framework, browser automation, async integration  

### **[TECHNICAL_REFERENCE.md](./TECHNICAL_REFERENCE.md)** - Implementation Details
**Who:** Developers implementing features  
**Purpose:** Code patterns, architecture, integration examples  
**Content:** File structure, patterns, async integration, component architecture  

### **[ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)** - Detailed Architecture
**Who:** Developers working on complex features  
**Purpose:** Deep dive into architectural patterns and design decisions  
**Content:** Component interactions, design patterns, integration strategies  

---

## **📊 Project Status**

### **[IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)** - Honest Assessment
**Who:** Project managers, stakeholders, developers  
**Purpose:** Brutal honesty about current implementation status  
**Content:** What's actually complete, gaps, realistic timelines, risks  

### **[DEVELOPMENT_PROGRESS.md](./DEVELOPMENT_PROGRESS.md)** - Historical Progress
**Who:** Team members tracking progress  
**Purpose:** Development milestones and breakthrough documentation  
**Content:** Major achievements, lessons learned, implementation history  

---

## **🧪 Quality Assurance**

### **[TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md)** - Testing Procedures
**Who:** QA engineers, developers  
**Purpose:** Comprehensive testing procedures and validation  
**Content:** Test cases, validation criteria, regression testing  

---

## **🔧 Implementation Details**

### **`implementations/` folder** - Tactical Documentation
**Who:** Developers working on specific features  
**Purpose:** Code-level implementation guides for specific features  
**Content:** Technical deep-dives, implementation patterns, design decisions

**Current implementations:**
- `element_picker_parent_selector.md` - Parent selector enhancement with registry pattern
- `datatable_wrapper_pattern.md` - DataTable component architecture
- `browser_state_observer.md` - Reactive browser state management
- `domain_specific_fields.md` - Domain-specific field components  

---

## **📖 Reading Paths by Role**

### **New Developer:**
1. [MODUS_OPERANDI.md](./MODUS_OPERANDI.md) - Learn development principles
2. [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - Understand business context
3. [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - Know current reality
4. [TECHNICAL_REFERENCE.md](./TECHNICAL_REFERENCE.md) - Learn implementation patterns

### **Product Manager:**
1. [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - Business requirements and goals
2. [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - Current status and timeline
3. [BEHAVIORAL_SPECIFICATION.md](./BEHAVIORAL_SPECIFICATION.md) - User requirements
4. [MODUS_OPERANDI.md](./MODUS_OPERANDI.md) - Understand development approach

### **Technical Lead:**
1. [MODUS_OPERANDI.md](./MODUS_OPERANDI.md) - Development standards
2. [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) - Technology rationale
3. [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - Detailed architecture
4. [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - Honest assessment

### **QA Engineer:**
1. [BEHAVIORAL_SPECIFICATION.md](./BEHAVIORAL_SPECIFICATION.md) - Requirements to test
2. [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md) - Testing procedures
3. [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - What's actually testable
4. [TECHNICAL_REFERENCE.md](./TECHNICAL_REFERENCE.md) - Implementation details

---

## **🔄 Document Maintenance**

### **Update Frequency:**
- **IMPLEMENTATION_STATUS.md** - Weekly during active development
- **TECHNICAL_REFERENCE.md** - When architecture changes
- **MODUS_OPERANDI.md** - Rarely (foundational principles)
- **implementations/** - When features are implemented/updated

### **Ownership:**
- **Business Documents** - Product Manager
- **Technical Documents** - Technical Lead
- **Status Documents** - Project Manager
- **Quality Documents** - QA Lead

---

## **💡 Quick Reference**

### **Need to understand the business?** → [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
### **Want to know what's actually done?** → [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
### **Looking for code patterns?** → [TECHNICAL_REFERENCE.md](./TECHNICAL_REFERENCE.md)
### **Why was this technology chosen?** → [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md)
### **What are the development rules?** → [MODUS_OPERANDI.md](./MODUS_OPERANDI.md)
### **How do I test this?** → [TESTING_CHECKLIST.md](./TESTING_CHECKLIST.md)

---

*All documentation follows the principles established in [MODUS_OPERANDI.md](./MODUS_OPERANDI.md). Each document serves a single responsibility and maintains clear separation of concerns.*