"""
q2JSON Modules Package
Core processing logic extracted for testing and reusability
"""

__version__ = "1.0.0"
__author__ = "q2JSON Development Team"

from .json_processor import JSONProcessor
from .llm_repairs import repair_chatgpt_response, repair_claude_response, repair_copilot_response, repair_gemini_response

__all__ = [
    'JSONProcessor',
    'repair_chatgpt_response',
    'repair_claude_response', 
    'repair_copilot_response',
    'repair_gemini_response'
]