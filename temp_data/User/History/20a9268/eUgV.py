# Q2LMS Component Extraction Library
"""
Extracted and enhanced Q2LMS components for Q2JSON Stage 4 integration.

This library provides:
1. LaTeX Processing Pipeline - Mathematical notation rendering and validation
2. Question Renderer - Multi-type question display with LaTeX support
3. Editor Framework - Side-by-side editing with live preview
4. Validation Manager - Mathematical validation and flagging system

All components are extracted from the proven Q2LMS codebase and enhanced
with mathematical validation capabilities for Q2JSON integration.
"""

# Import components with error handling
try:
    from .latex_processor import Q2JSONLaTeXProcessor, MathValidationManager
    LATEX_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LaTeX processor not available: {e}")
    LATEX_AVAILABLE = False

try:
    from .question_renderer import Q2JSONQuestionRenderer
    RENDERER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Question renderer not available: {e}")
    RENDERER_AVAILABLE = False

try:
    from .editor_framework import Q2JSONEditorFramework
    EDITOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Editor framework not available: {e}")
    EDITOR_AVAILABLE = False

try:
    from .validation_manager import Q2JSONValidationManager
    VALIDATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Validation manager not available: {e}")
    VALIDATION_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "Q2LMS Component Extraction"
__description__ = "Proven Q2LMS components for Q2JSON Stage 4"

# Build __all__ dynamically based on what's available
__all__ = []
if LATEX_AVAILABLE:
    __all__.extend(['Q2JSONLaTeXProcessor', 'MathValidationManager'])
if RENDERER_AVAILABLE:
    __all__.append('Q2JSONQuestionRenderer')
if EDITOR_AVAILABLE:
    __all__.append('Q2JSONEditorFramework')
if VALIDATION_AVAILABLE:
    __all__.append('Q2JSONValidationManager')
