# UI Enhancement Ideas - q2JSON

## **Priority Enhancement: Multiple Question Type Selection**

**Current Behavior**: 
- Single selection from dropdown: Mixed types, Multiple choice only, etc.

**Proposed Enhancement**:
- When "Mixed types" is NOT selected, allow multiple selections
- Example: Could select both "Multiple choice only" + "True/False only"
- UI could be checkboxes when not in "Mixed" mode

**Implementation Approach**:
```python
# Streamlit multiselect when not Mixed
if not mixed_mode:
    question_types = st.multiselect(
        "Select Question Types:",
        ["Multiple choice", "Multiple dropdowns", "Numerical", "True/False"]
    )
else:
    question_types = ["Mixed"]
```

**Benefits**:
- More granular control for educators
- Better testing capabilities (e.g., only MC + T/F for quick assessments)
- Maintains simplicity with "Mixed" option for general use

---

## **Other Potential Enhancements**

### **Template Status Display**
- Show template loading status more prominently
- Preview template content in expandable section

### **Question Preview**
- Show sample question based on current settings
- Help users understand what they'll get before generating

### **Prompt Preview**
- Expandable section showing the actual prompt being generated
- Useful for advanced users and debugging

### **LLM-Specific Settings**
- Dropdown to optimize prompt for specific LLMs
- Could adjust template complexity automatically

---

## **Development Priority**
1. **Complete current testing** (ChatGPT validation, Stage 2-3 testing)
2. **Multi-select question types** (highest impact UX improvement)
3. **Template preview features** (development/debugging aid)
4. **LLM optimization** (after compatibility matrix complete)