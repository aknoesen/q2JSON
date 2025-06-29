"""
LLM-specific repair strategies
Each LLM has unique formatting quirks that require targeted fixes
"""

import re
import json
from typing import Callable


def repair_chatgpt_response(json_str: str) -> str:
    """
    Handle ChatGPT-specific issues:
    - Display math ($$..$$) with complex LaTeX
    - LaTeX command escaping
    - Unicode in mathematical expressions
    """
    repaired = json_str
    
    # MOST AGGRESSIVE: Replace complex display math with placeholders
    # This handles the problematic $$f_r = \frac{...}$$ patterns
    repaired = re.sub(r'\$\$([^$]*\\[a-zA-Z]+[^$]*)\$\$', r'[Mathematical Formula]', repaired)
    
    # Convert remaining simple display math to inline math
    repaired = re.sub(r'\$\$([^$]+)\$\$', r'$\1$', repaired)
    
    # Fix ALL LaTeX escaping issues (both single and double backslashes)
    latex_fixes = [
        ('\\\\frac', 'frac'),
        ('\\\\log', 'log'),
        ('\\\\sqrt', 'sqrt'),
        ('\\\\times', 'times'),
        ('\\\\text', 'text'),
        ('\\\\approx', 'approx'),
        ('\\\\circ', 'circ'),
        ('\\\\varepsilon', 'varepsilon'),
        ('\\\\epsilon', 'epsilon'),
        ('\\\\Gamma', 'Gamma'),
        ('\\\\dfrac', 'dfrac'),
        ('\\\\cdot', 'cdot'),
        ('\\\\pm', 'pm'),
        ('\\\\infty', 'infty'),
        ('\\\\pi', 'pi'),
        ('\\\\omega', 'omega'),
        ('\\\\Omega', 'Omega'),
        ('\\\\mu', 'mu'),
        ('\\\\alpha', 'alpha'),
        ('\\\\beta', 'beta'),
        ('\\\\gamma', 'gamma'),
        ('\\\\theta', 'theta'),
        ('\\\\lambda', 'lambda'),
        ('\\\\sigma', 'sigma'),
    ]
    
    # Apply double backslash fixes
    for old, new in latex_fixes:
        repaired = repaired.replace(old, new)
    
    # Apply single backslash fixes
    for old, new in latex_fixes:
        repaired = repaired.replace(old.replace('\\\\', '\\'), new)
    
    # Fix common escape sequences
    escape_fixes = [
        ('\\"', '"'),
        ("\\'", "'"),
        ('\\[', '['),
        ('\\]', ']'),
        ('\\{', '{'),
        ('\\}', '}'),
        ('\\(', '('),
        ('\\)', ')'),
        ('\\/', '/'),
        ('\\\\', '\\'),
    ]
    
    for old, new in escape_fixes:
        repaired = repaired.replace(old, new)
    
    # Fix field name escapes
    repaired = re.sub(r'"(\w+)\\_(\w+)":', r'"\1_\2":', repaired)
    
    # Remove remaining problematic escapes
    repaired = re.sub(r'\\([^"\\\/bfnrt])', r'\1', repaired)
    
    return repaired


def repair_claude_response(json_str: str) -> str:
    """
    Handle Claude-specific issues:
    - Preference bleeding (PowerShell, user context)
    - Over-verbose responses
    - Boundary confusion
    """
    repaired = json_str
    
    # Remove any PowerShell-specific artifacts
    repaired = re.sub(r'PowerShell[^"]*', '', repaired)
    
    # Remove preference-related content
    repaired = re.sub(r'[Pp]reference[^"]*', '', repaired)
    
    # Standard escape fixes
    repaired = repaired.replace('\\"', '"')
    repaired = repaired.replace("\\'", "'")
    
    return repaired


def repair_copilot_response(json_str: str) -> str:
    """
    Handle Microsoft Copilot-specific issues:
    - Safety filter artifacts
    - Truncated responses
    - Conservative formatting
    """
    repaired = json_str
    
    # Remove safety filter messages
    safety_patterns = [
        r'I cannot.*',
        r'I\'m not able to.*',
        r'I apologize.*',
        r'Safety.*',
    ]
    
    for pattern in safety_patterns:
        repaired = re.sub(pattern, '', repaired, flags=re.IGNORECASE)
    
    # Standard escape fixes
    repaired = repaired.replace('\\"', '"')
    repaired = repaired.replace("\\'", "'")
    
    return repaired


def repair_gemini_response(json_str: str) -> str:
    """
    Handle Google Gemini-specific issues:
    - Generally the most compliant LLM
    - Minimal fixes needed
    """
    repaired = json_str
    
    # Basic escape fixes
    repaired = repaired.replace('\\"', '"')
    repaired = repaired.replace("\\'", "'")
    
    return repaired


def repair_generic_response(json_str: str) -> str:
    """
    Generic repair function for unknown LLMs
    Applies common fixes that work across most LLMs
    """
    repaired = json_str
    
    # Basic LaTeX fixes
    repaired = repaired.replace('\\circ', 'circ')
    repaired = repaired.replace('\\times', 'times')
    repaired = repaired.replace('\\text', 'text')
    
    # Basic escape fixes
    repaired = repaired.replace('\\"', '"')
    repaired = repaired.replace("\\'", "'")
    repaired = repaired.replace('\\[', '[')
    repaired = repaired.replace('\\]', ']')
    
    return repaired


def get_repair_function(llm_type: str) -> Callable[[str], str]:
    """
    Factory function to get appropriate repair function based on LLM type
    
    Args:
        llm_type: Type of LLM ("chatgpt", "claude", "copilot", "gemini", "auto")
        
    Returns:
        Appropriate repair function
    """
    repair_functions = {
        'chatgpt': repair_chatgpt_response,
        'claude': repair_claude_response,
        'copilot': repair_copilot_response,
        'gemini': repair_gemini_response,
        'auto': repair_chatgpt_response,  # Default to ChatGPT (most complex)
        'generic': repair_generic_response,
    }
    
    return repair_functions.get(llm_type.lower(), repair_generic_response)


def detect_llm_type(json_str: str) -> str:
    """
    Attempt to detect LLM type based on response characteristics
    
    Args:
        json_str: Raw JSON response string
        
    Returns:
        Detected LLM type or "unknown"
    """
    # ChatGPT indicators
    if '$$' in json_str or '\\frac' in json_str or '\\dfrac' in json_str:
        return 'chatgpt'
    
    # Claude indicators
    if 'PowerShell' in json_str or 'preference' in json_str.lower():
        return 'claude'
    
    # Copilot indicators
    if 'cannot' in json_str.lower() or 'safety' in json_str.lower():
        return 'copilot'
    
    # Default
    return 'unknown'