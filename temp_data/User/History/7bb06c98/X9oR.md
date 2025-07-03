# Q2LMS Component Extraction Documentation

## Overview

This directory contains proven Q2LMS components extracted and enhanced for Q2JSON Stage 4 integration. These components provide sophisticated question viewing, editing, and mathematical validation capabilities.

## Components

### 1. 🧮 LaTeX Processing Pipeline (`latex_processor.py`)

**Extracted from:**
- `Q2LMS utils.py` (render_latex_in_text, normalize_latex_for_display)
- `Q2LMS export/latex_converter.py` (CanvasLaTeXConverter)

**Key Classes:**
- `Q2JSONLaTeXProcessor`: Enhanced LaTeX processor with validation
- `MathValidationManager`: Mathematical validation and flagging system

**Key Features:**
- Real-time LaTeX rendering with Streamlit
- Comprehensive LaTeX normalization (degree symbols, angle notation, subscripts/superscripts)
- Mathematical validation and error detection
- Canvas/QTI delimiter conversion
- Unicode to LaTeX conversion support

**Usage Example:**
```python
from extracted_components import Q2JSONLaTeXProcessor

processor = Q2JSONLaTeXProcessor()
rendered_text, validation = processor.render_latex_with_validation(
    "The voltage is $V = 10\\,\\text{V}$ at frequency $f = 50\\,\\text{Hz}$"
)
```

### 2. 👁️ Question Renderer (`question_renderer.py`)

**Extracted from:**
- `Q2LMS interface_delete_questions._render_question_preview()`
- `Q2LMS question_editor.display_live_question_preview()`

**Key Classes:**
- `Q2JSONQuestionRenderer`: Multi-type question display with validation indicators

**Key Features:**
- Support for all question types (multiple choice, numerical, true/false, fill-in-blank)
- Live LaTeX rendering with validation indicators
- Mathematical validation flagging in preview
- Accessibility-friendly rendering
- Extensible question type system

**Usage Example:**
```python
from extracted_components import Q2JSONQuestionRenderer

renderer = Q2JSONQuestionRenderer()
renderer.render_question_with_validation(
    question_data,
    validation_results,
    show_validation_indicators=True
)
```

### 3. ✏️ Editor Framework (`editor_framework.py`)

**Extracted from:**
- `Q2LMS interface_delete_questions._render_question_edit_form()`
- `Q2LMS question_editor.side_by_side_question_editor()`

**Key Classes:**
- `Q2JSONEditorFramework`: Side-by-side editing with live preview and validation

**Key Features:**
- Side-by-side edit/preview layout (proven Q2LMS pattern)
- Real-time mathematical validation during editing
- Type-specific editing forms
- Session state management for unsaved changes
- Customizable save callbacks

**Usage Example:**
```python
from extracted_components import Q2JSONEditorFramework

def save_callback(index, data):
    # Your save logic here
    return True

editor = Q2JSONEditorFramework(save_callback=save_callback)
result = editor.render_side_by_side_editor(question_data, question_index)
```

### 4. 🔍 Validation Manager (`validation_manager.py`)

**Extracted from:**
- `Q2LMS question_flag_manager.py` (flagging architecture)
- Enhanced with comprehensive mathematical validation

**Key Classes:**
- `Q2JSONValidationManager`: Comprehensive validation and flagging system

**Key Features:**
- Multi-level validation (critical/warning/info)
- Batch validation operations
- Validation dashboard and reporting
- DataFrame integration with validation flags
- Comprehensive validation analytics

**Usage Example:**
```python
from extracted_components import Q2JSONValidationManager

validator = Q2JSONValidationManager()

# Single question validation
results = validator.validate_question_comprehensive(question_data)

# Batch validation
batch_results = validator.validate_question_batch(questions_list)

# Render validation dashboard
validator.render_validation_dashboard(results)
```

## Integration Guide

### Step 1: Basic Setup

```python
import streamlit as st
from extracted_components import (
    Q2JSONLaTeXProcessor,
    Q2JSONQuestionRenderer,
    Q2JSONEditorFramework,
    Q2JSONValidationManager
)

# Initialize components
latex_processor = Q2JSONLaTeXProcessor()
renderer = Q2JSONQuestionRenderer()
validator = Q2JSONValidationManager()
editor = Q2JSONEditorFramework()
```

### Step 2: Configure Streamlit for LaTeX

```python
# Apply MathJax configuration
st.markdown(\"\"\"
<script>
window.MathJax = {
    tex: {inlineMath: [['$', '$'], ['\\\\(', '\\\\)']]},
    svg: {fontCache: 'global'}
};
</script>
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
\"\"\", unsafe_allow_html=True)
```

### Step 3: Basic Question Review Interface

```python
def render_question_review(question_data):
    # Validate question
    validation_results = validator.validate_question_comprehensive(question_data)
    
    # Render with validation
    renderer.render_question_with_validation(
        question_data,
        validation_results,
        show_validation_indicators=True
    )
```

### Step 4: Side-by-Side Editor

```python
def render_question_editor(question_data, question_index):
    def save_question(index, data):
        # Your save logic
        st.session_state.questions[index] = data
        return True
    
    editor_framework = Q2JSONEditorFramework(save_callback=save_question)
    
    result = editor_framework.render_side_by_side_editor(
        question_data,
        question_index,
        show_validation=True
    )
    
    return result
```

### Step 5: Batch Validation Dashboard

```python
def render_batch_validation(questions_list):
    # Run batch validation
    batch_results = validator.validate_question_batch(questions_list)
    
    # Render dashboard
    validator.render_validation_dashboard(batch_results)
    
    # Create DataFrame with validation flags
    df = pd.DataFrame(questions_list)
    df_with_flags = validator.add_validation_flags_to_dataframe(df, batch_results)
    
    return df_with_flags
```

## Mathematical Validation Features

### Validation Types

1. **Critical Issues** (🚨)
   - Unmatched LaTeX delimiters
   - Invalid LaTeX syntax
   - Rendering-breaking errors

2. **Warnings** (⚠️)
   - Unicode symbols in mathematical expressions
   - Inconsistent notation
   - Spacing issues

3. **Info** (ℹ️)
   - Optimization suggestions
   - Accessibility improvements
   - Best practice recommendations

### Validation Rules

- **LaTeX Syntax**: Checks for proper delimiter matching, brace matching
- **Unicode Detection**: Identifies Unicode math symbols that should be LaTeX
- **Rendering Validation**: Tests actual LaTeX rendering
- **Consistency Checks**: Ensures consistent mathematical notation
- **Accessibility**: Validates screen reader compatibility

## Dependencies

### Required Libraries
```python
import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import html
import logging
```

### Streamlit Configuration
- MathJax 3.x for LaTeX rendering
- Custom CSS for validation indicators
- Wide layout mode recommended

## Best Practices

### 1. LaTeX Formatting
- Use `$...$` for inline mathematics
- Use `$$...$$` for display mathematics
- Include proper spacing: `$10\\,\\Omega$`
- Avoid Unicode symbols in mathematical expressions

### 2. Validation Integration
- Run validation before saving questions
- Display validation indicators in real-time
- Provide clear error messages and suggestions
- Use batch validation for large question sets

### 3. User Experience
- Show live preview during editing
- Provide immediate feedback on mathematical issues
- Use consistent validation indicators
- Offer one-click fixes for common issues

## Performance Considerations

- **Validation Caching**: Cache validation results to avoid re-computation
- **Incremental Validation**: Validate only changed fields during editing
- **Batch Processing**: Use batch validation for large datasets
- **Lazy Loading**: Load validation results on-demand for large question sets

## Complete Example

See `q2json_stage4_example.py` for a complete implementation showing:
- Full Q2JSON Stage 4 interface
- All components working together
- Validation dashboard
- Question review and editing
- Batch operations
- Sample data with mathematical issues

## Migration from Q2LMS

These components are designed to be drop-in replacements for Q2LMS functionality:

| Q2LMS Function | Extracted Component | Enhancement |
|---------------|-------------------|-------------|
| `render_latex_in_text()` | `Q2JSONLaTeXProcessor.render_latex_with_validation()` | Added validation feedback |
| `_render_question_preview()` | `Q2JSONQuestionRenderer.render_question_with_validation()` | Added validation indicators |
| `side_by_side_question_editor()` | `Q2JSONEditorFramework.render_side_by_side_editor()` | Added real-time validation |
| `QuestionFlagManager` | `Q2JSONValidationManager` | Enhanced with mathematical validation |

## Support and Extensions

### Adding New Question Types

```python
# Extend the question renderer
class CustomQuestionRenderer(Q2JSONQuestionRenderer):
    def __init__(self):
        super().__init__()
        self.question_types['custom_type'] = self._render_custom_preview
    
    def _render_custom_preview(self, question_data, validation_results):
        # Your custom rendering logic
        pass
```

### Custom Validation Rules

```python
# Extend the validation manager
class CustomValidationManager(Q2JSONValidationManager):
    def _validate_custom_rules(self, question_data):
        # Your custom validation logic
        return validation_results
```

### Integration with External Systems

```python
# Custom save callback for external databases
def external_save_callback(question_index, question_data):
    try:
        # Save to your external system
        external_api.save_question(question_data)
        return True
    except Exception as e:
        st.error(f"External save failed: {e}")
        return False

editor = Q2JSONEditorFramework(save_callback=external_save_callback)
```
