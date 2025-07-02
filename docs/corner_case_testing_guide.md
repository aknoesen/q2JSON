# Corner Case Testing Guide for q2JSON LLM Output Validation

## Overview

The q2JSON application includes comprehensive independent testing capabilities to analyze, validate, and auto-correct LLM-generated JSON output. This document outlines how to perform corner case testing and understand the auto-correction mechanisms.

## Critical Requirements Analysis

### Preamble Requirements (from `templates/preamble_default.txt`)
- **ABSOLUTE**: No Unicode characters allowed
- **REQUIRED**: All mathematical expressions MUST use LaTeX syntax
- **FORBIDDEN**: Unicode symbols (Ω, °, ², μ, π, ±, ≤, ≥)
- **MANDATORY**: LaTeX equivalents ($\Omega$, $^\circ$, $^2$, $\mu$, $\pi$, $\pm$, $\leq$, $\geq$)

### Postamble Requirements (from `templates/postamble_default.txt`)
- **STRICT**: Output ONLY valid JSON starting with { and ending with }
- **FORBIDDEN**: Citation patterns, markdown blocks, explanatory text
- **MANDATORY**: LaTeX math notation for ALL mathematical content
- **REQUIRED**: Exact JSON structure with "questions" array

## Independent Testing Framework

### 1. Core Test Scripts

#### `tests/test_edge_cases_and_llm_behaviors.py`
- **Purpose**: Comprehensive edge case testing without pytest dependency
- **Capabilities**:
  - Corner case data processing from `test_data/CornerCases.json`
  - ChatGPT markdown pattern extraction
  - Malformed JSON recovery testing
  - Performance testing with large datasets (20+ questions)

**Run Command:**
```powershell
python tests/test_edge_cases_and_llm_behaviors.py
```

#### `test_real_data.py`
- **Purpose**: Test with actual problematic LLM responses
- **Capabilities**:
  - Real ChatGPT response testing from `test_data/chatgpt_responses/`
  - Simulated problematic data testing
  - Display math issue detection and repair

**Run Command:**
```powershell
python test_real_data.py
```

#### `tests/diagnostic_test.py`
- **Purpose**: Deep diagnostic analysis of Master.json processing
- **Capabilities**:
  - Individual question analysis
  - JSON structure validation
  - Serialization testing
  - Error pattern identification

**Run Command:**
```powershell
python tests/diagnostic_test.py
```

### 2. Test Data Structure

#### `test_data/CornerCases.json`
- Contains edge cases with:
  - Complex LaTeX expressions
  - Unicode characters (for testing detection)
  - Extended JSON fields
  - Metadata preservation tests
  - Phase relationships and mathematical formulas

#### `test_data/chatgpt_responses/antenna_display_math.json`
- Real ChatGPT output with problematic display math patterns
- Contains `$$...$$` display math blocks
- LaTeX escaping issues (`\\frac`, `\\dfrac`)

### 3. LLM-Specific Repair Strategies

#### ChatGPT Issues (`modules/llm_repairs.py::repair_chatgpt_response`)
- **Display Math**: `$$f_r = \frac{...}$$` → `[Mathematical Formula]` or `$...$`
- **LaTeX Escaping**: `\\frac` → `frac`, `\\text` → `text`
- **Complex Patterns**: Aggressive replacement of problematic display math
- **Field Escapes**: `"field\_name"` → `"field_name"`

#### Claude Issues (`modules/llm_repairs.py::repair_claude_response`)
- **Preference Bleeding**: Removes PowerShell context artifacts
- **Over-verbose**: Strips explanatory content
- **Boundary Confusion**: Cleans user context leakage

#### Copilot Issues (`modules/llm_repairs.py::repair_copilot_response`)
- **Safety Filters**: Removes "I cannot", "I'm not able to" patterns
- **Conservative Formatting**: Handles truncated responses
- **Apology Patterns**: Strips apologetic content

#### Gemini Issues (`modules/llm_repairs.py::repair_gemini_response`)
- **Minimal Fixes**: Generally most compliant LLM
- **Basic Escaping**: Standard quote and bracket fixes

## Auto-Correction Mechanisms

### 1. JSONProcessor Core Logic (`modules/json_processor.py`)

#### Preprocessing Pipeline
1. **Markdown Extraction**: ````json ... ```` block detection
2. **JSON Boundary Detection**: First `{` to last `}` extraction
3. **Smart Quote Conversion**: `"` and `"` → `"`
4. **Underscore Escape Removal**: `\_` → `_`
5. **Comment Removal**: Lines starting with `#`
6. **Bracket Balancing**: Auto-close unclosed `[` and `{`

#### Processing Flow
```python
def process_raw_json(self, raw_json: str, llm_type: str = "auto"):
    1. Simple preprocessing (markdown, quotes, brackets)
    2. Direct JSON parsing attempt
    3. Structure validation (requires "questions" array)
    4. If failed: Auto-repair with LLM-specific strategies
    5. Re-parse and validate repaired JSON
    6. Return success/failure with detailed messages
```

#### Validation Levels
- **Structure**: Must be dict with "questions" array
- **Content**: Required fields per question type
- **Type-Specific**: Multiple choice (4 choices), numerical (numeric answer), true/false (boolean)

### 2. Independent Validation Features

#### Question Type Validation
```python
# Multiple Choice
if q_type == 'multiple_choice':
    if len(question.get('choices', [])) != 4:
        q_analysis['issues'].append("Expected 4 choices")

# Numerical
elif q_type == 'numerical':
    try:
        float(str(question['correct_answer']))
    except (ValueError, TypeError):
        q_analysis['issues'].append("Correct answer is not numeric")

# True/False
elif q_type == 'true_false':
    if str(question['correct_answer']).lower() not in ['true', 'false']:
        q_analysis['issues'].append("Must be 'True' or 'False'")
```

#### Export Validation
- **Compact**: `separators=(',', ':')`
- **Pretty**: `indent=4`
- **Standard**: `indent=2`
- **Unicode Safety**: `ensure_ascii=False`

## Corner Case Investigation Workflow

### 1. Identify New Corner Cases
```powershell
# Run comprehensive edge case tests
python tests/test_edge_cases_and_llm_behaviors.py

# Test with real LLM data
python test_real_data.py

# Deep diagnostic analysis
python tests/diagnostic_test.py
```

### 2. Add New Test Cases
```python
# Add to test_edge_cases_and_llm_behaviors.py
def test_new_corner_case():
    processor = JSONProcessor()
    
    # Your problematic LLM output
    problematic_json = '''...'''
    
    success, data, messages = processor.process_raw_json(problematic_json, "llm_type")
    
    # Analyze results
    print(f"Success: {success}")
    for message in messages:
        print(f"  - {message}")
```

### 3. Enhance Repair Functions
```python
# Add to modules/llm_repairs.py
def repair_new_pattern(json_str: str) -> str:
    repaired = json_str
    
    # Add specific repair logic
    repaired = re.sub(r'problematic_pattern', r'fixed_pattern', repaired)
    
    return repaired
```

### 4. Test Repair Effectiveness
```powershell
# Test specific repair function
python -c "
from modules.llm_repairs import repair_chatgpt_response
result = repair_chatgpt_response('your_test_data')
print(result)
"
```

## Production Usage

### Integrated Testing
The main Streamlit app (`app.py`) uses the same `JSONProcessor` class, ensuring that:
- All test-validated repairs work in production
- Corner case fixes are automatically applied
- User feedback shows the same diagnostic messages

### Continuous Improvement
1. **Collect**: Save problematic LLM outputs to `test_data/`
2. **Test**: Run independent test scripts
3. **Analyze**: Review failure patterns and messages
4. **Enhance**: Update repair functions in `llm_repairs.py`
5. **Validate**: Re-run tests to confirm fixes
6. **Deploy**: Changes automatically work in main app

## Summary

The q2JSON codebase provides comprehensive independent testing and auto-correction capabilities:

- **4 independent test scripts** for different aspects of validation
- **LLM-specific repair strategies** for ChatGPT, Claude, Copilot, and Gemini
- **Comprehensive validation** of JSON structure and content
- **Automatic preprocessing** to handle common formatting issues
- **Detailed diagnostic output** for debugging and improvement
- **Real-world test data** including actual problematic LLM responses

This system enables thorough corner case investigation and continuous improvement of auto-correction mechanisms without requiring the full Streamlit application.
