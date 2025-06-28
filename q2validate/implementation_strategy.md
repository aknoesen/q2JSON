# Q2LMS JSON Validator Implementation Strategy

**Date**: December 2024  
**Purpose**: Instructor tooling for validating q2prompt JSON output before Q2LMS import  
**Context**: Top-down course planning workflow with PowerShell/VS Code environment

## Project Overview

### Problem Statement
- q2prompt (LLM-based question generator) sometimes produces Unicode characters despite LaTeX instructions
- Need validation layer between q2prompt → Q2LMS import
- Instructor needs visual preview of questions before committing to LMS
- Current pain point: Manual checking of JSON format and Unicode conversion

### Solution Architecture
**Option 1A: Standalone Validator + Submodule Integration** ✅ **SELECTED**

## Repository Structure

### New Repository: `q2lms-json-validator`
```
q2lms-json-validator/
├── README.md
├── requirements.txt
├── setup.py
├── validator_app.py                 # Main Streamlit app
├── modules/
│   ├── __init__.py
│   ├── unicode_converter.py         # Existing converter (provided)
│   ├── schema_validator.py          # JSON schema validation
│   ├── latex_renderer.py           # Basic LaTeX preview
│   ├── q2lms_adapter.py            # Adapter to Q2LMS components
│   └── question_preview.py         # Extracted from Q2LMS
├── templates/
│   ├── question_schema.json        # JSON schema definition
│   └── example_questions.json      # Sample valid questions
├── scripts/
│   ├── instructor_pipeline.ps1     # PowerShell orchestration
│   ├── batch_validate.ps1          # Batch processing
│   └── install_dependencies.ps1    # Setup script
├── shared/
│   └── q2lms/                      # Git submodule → Q2LMS repo
├── docs/
│   ├── installation.md
│   ├── usage.md
│   └── integration_with_q2lms.md
└── tests/
    ├── test_unicode_conversion.py
    ├── test_schema_validation.py
    └── sample_data/
```

### Integration with Existing Repositories

#### Q2Prompt Integration
```bash
cd q2prompt
git submodule add https://github.com/aknoesen/q2lms.git shared/q2lms
```

```
q2prompt/
├── (existing structure)
├── shared/
│   └── q2lms/                      # Git submodule → Q2LMS repo
└── integrations/
    ├── q2lms_preview.py            # Preview adapter
    └── validator_bridge.py         # Bridge to validator
```

## Technical Implementation

### Core Components

#### 1. Unicode Detection & Conversion
- **Source**: Existing `unicode_to_latex_converter.py` (provided)
- **Enhancement**: Integration with real-time validation
- **Patterns**: Ω, π, μ, °, ², ±, ≤, ≥, etc. → LaTeX equivalents

#### 2. JSON Schema Validation
```python
# Required fields validation
required_fields = ['type', 'title', 'question_text', 'correct_answer', 'topic', 'difficulty']

# Valid question types
valid_types = ['multiple_choice', 'numerical', 'true_false', 'fill_in_multiple_blanks']

# Valid difficulty levels  
valid_difficulties = ['Easy', 'Medium', 'Hard']
```

#### 3. Q2LMS Component Integration
```python
# q2lms_adapter.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared', 'q2lms'))

# Direct import of Q2LMS components
from modules.question_editor import display_live_question_preview
from modules.utils import render_latex_in_text
from modules.export.latex_converter import CanvasLaTeXConverter
```

#### 4. Question Schema (Q2LMS Compatible)
```json
{
  "type": "multiple_choice|numerical|true_false|fill_in_multiple_blanks",
  "title": "string",
  "question_text": "string (LaTeX notation)", 
  "choices": ["array (if multiple_choice)"],
  "correct_answer": "string|number",
  "points": "number",
  "tolerance": "number (if numerical)",
  "feedback_correct": "string",
  "feedback_incorrect": "string",
  "topic": "string",
  "subtopic": "string",
  "difficulty": "Easy|Medium|Hard"
}
```

### Key Features

#### Validation Pipeline
1. **JSON Structure Validation** - Schema compliance checking
2. **Unicode Detection** - Scan for problematic characters
3. **Auto-Conversion** - Unicode → LaTeX with user confirmation
4. **Visual Preview** - Using Q2LMS preview components
5. **Export Options** - Corrected JSON ready for Q2LMS import

#### User Interface (Streamlit)
- **Input Methods**: File upload OR text paste
- **Status Dashboard**: Schema ✅/❌, Unicode ✅/⚠️, Ready ✅/❌
- **Question Gallery**: Expandable preview of each question
- **Batch Operations**: Process multiple questions simultaneously
- **Export Controls**: Download corrected JSON + metadata

## Workflow Integration

### Instructor Pipeline
```powershell
# instructor_pipeline.ps1

# Step 1: Generate questions (q2prompt)
Set-Location "C:\Path\q2prompt"
# Call q2prompt with topic/parameters

# Step 2: Validate questions  
Set-Location "C:\Path\q2lms-json-validator"
streamlit run validator_app.py

# Step 3: Import to Q2LMS
Set-Location "C:\Path\q2lms"  
# Import validated JSON
```

### VS Code Workspace
```json
{
  "folders": [
    {"path": "./q2prompt"},
    {"path": "./q2lms-json-validator"}, 
    {"path": "./q2lms"}
  ],
  "settings": {
    "python.defaultInterpreterPath": "./venv/bin/python"
  }
}
```

## Implementation Phases

### Phase 1: Core Functionality (Week 1)
- [ ] Create repository structure
- [ ] Set up Q2LMS submodule
- [ ] Integrate Unicode converter
- [ ] Basic JSON schema validation
- [ ] Extract Q2LMS preview components
- [ ] Basic Streamlit interface

### Phase 2: Integration & Polish (Week 2)  
- [ ] Q2LMS adapter layer
- [ ] PowerShell orchestration scripts
- [ ] Enhanced LaTeX rendering
- [ ] Batch processing capabilities
- [ ] Error handling and user feedback

### Phase 3: Testing & Documentation (Week 3)
- [ ] Test with real course content
- [ ] Performance optimization
- [ ] Complete documentation
- [ ] Installation/setup scripts
- [ ] Integration testing across pipeline

## Technical Dependencies

### Python Requirements
```txt
streamlit>=1.28.0
pandas>=2.0.0
json-schema>=4.0.0
```

### System Requirements
- **OS**: Windows (PowerShell integration)
- **Editor**: VS Code
- **Python**: 3.8+
- **Git**: For submodule management

## Key Design Decisions

### Why Submodules?
- **DRY Principle**: No code duplication across repos
- **Maintenance**: Single source of truth for Q2LMS components  
- **Integration**: Direct access to Q2LMS LaTeX rendering
- **Instructor Workflow**: Seamless cross-repository development

### Why Standalone Repository?
- **Separation of Concerns**: Validation is distinct from generation/import
- **Flexibility**: Can be used independently or in pipeline
- **Maintainability**: Clear boundaries and responsibilities
- **Professional Tooling**: Instructor-grade validation without student complexity

### Why PowerShell Integration?
- **Instructor Preference**: Matches existing Windows/VS Code workflow
- **Automation**: Scriptable pipeline for course development
- **Batch Processing**: Handle multiple question sets efficiently

## Future Considerations

### Potential Extensions
- **Custom Validation Rules**: Course-specific validation logic
- **Question Analytics**: Statistics on question complexity/topics
- **LMS Integration**: Direct upload to Canvas/Moodle
- **Collaboration Features**: Multi-instructor question review

### Scalability
- **Performance**: Handle large question databases (100+ questions)
- **Memory**: Efficient processing of LaTeX-heavy content
- **Reliability**: Robust error handling for production use

## Success Criteria

### Functional
- ✅ Detects and converts Unicode characters
- ✅ Validates JSON schema compliance  
- ✅ Provides visual question preview
- ✅ Exports Q2LMS-ready JSON
- ✅ Integrates with PowerShell workflow

### Non-Functional  
- ✅ Fast validation (< 5 seconds for 20 questions)
- ✅ Reliable Unicode detection (100% accuracy)
- ✅ Intuitive interface for instructors
- ✅ Comprehensive error messages
- ✅ Maintainable codebase

---

**Next Steps**: Proceed with Phase 1 implementation, starting with repository creation and submodule setup.