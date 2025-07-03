# Q2JSON LaTeX Processor Component
"""
Q2JSONLaTeXProcessor - Mathematical notation processing and validation

Extracted and enhanced from Q2LMS codebase for Q2JSON Stage 4 integration.
Provides comprehensive LaTeX processing, KaTeX rendering support, and mathematical
expression validation with error reporting.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import html
import unicodedata

try:
    from .unicode_converter import convert_unicode_to_latex
except ImportError:
    # Fallback implementation if unicode_converter is not available
    def convert_unicode_to_latex(text: str) -> str:
        """Fallback unicode to LaTeX conversion."""
        replacements = {
            'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
            'ε': r'\epsilon', 'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta',
            'ι': r'\iota', 'κ': r'\kappa', 'λ': r'\lambda', 'μ': r'\mu',
            'ν': r'\nu', 'ξ': r'\xi', 'ο': r'o', 'π': r'\pi',
            'ρ': r'\rho', 'σ': r'\sigma', 'τ': r'\tau', 'υ': r'\upsilon',
            'φ': r'\phi', 'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega',
            '²': r'^2', '³': r'^3', '°': r'^\circ', '±': r'\pm',
            '×': r'\times', '÷': r'\div', '≤': r'\leq', '≥': r'\geq',
            '≠': r'\neq', '≈': r'\approx', '∞': r'\infty', '∑': r'\sum',
            '∫': r'\int', '√': r'\sqrt', '∆': r'\Delta', '∇': r'\nabla'
        }
        
        result = text
        for unicode_char, latex_cmd in replacements.items():
            result = result.replace(unicode_char, latex_cmd)
        
        return result


@dataclass
class MathValidationResult:
    """Result of mathematical expression validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    processed_expression: str
    render_html: str


class Q2JSONLaTeXProcessor:
    """
    Advanced LaTeX processor extracted from Q2LMS with enhanced mathematical support.
    
    Features:
    - LaTeX expression parsing and validation
    - KaTeX/MathJax rendering support
    - Unicode to LaTeX conversion
    - Mathematical notation standardization
    - Error detection and suggestions
    - Safe HTML rendering
    """
    
    def __init__(self, 
                 renderer: str = 'katex',
                 strict_mode: bool = False,
                 auto_convert_unicode: bool = True):
        """
        Initialize the LaTeX processor.
        
        Args:
            renderer: Math renderer to use ('katex', 'mathjax', or 'plain')
            strict_mode: Whether to use strict LaTeX validation
            auto_convert_unicode: Whether to automatically convert Unicode to LaTeX
        """
        self.renderer = renderer
        self.strict_mode = strict_mode
        self.auto_convert_unicode = auto_convert_unicode
        
        # LaTeX command patterns
        self.latex_patterns = {
            'inline_math': re.compile(r'\$([^$]+)\$'),
            'display_math': re.compile(r'\$\$([^$]+)\$\$'),
            'latex_command': re.compile(r'\\([a-zA-Z]+)(?:\{([^}]*)\})?'),
            'subscript': re.compile(r'_\{([^}]+)\}|_([a-zA-Z0-9])'),
            'superscript': re.compile(r'\^\{([^}]+)\}|\^([a-zA-Z0-9])'),
            'fraction': re.compile(r'\\frac\{([^}]+)\}\{([^}]+)\}'),
            'sqrt': re.compile(r'\\sqrt(?:\[([^\]]*)\])?\{([^}]+)\}'),
            'matrix': re.compile(r'\\begin\{(matrix|pmatrix|bmatrix|vmatrix)\}(.*?)\\end\{\1\}', re.DOTALL)
        }
        
        # Common LaTeX commands and their validation
        self.valid_commands = {
            # Greek letters
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
            'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma',
            'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
            'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta',
            'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Pi', 'Rho', 'Sigma',
            'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
            
            # Mathematical operators
            'sum', 'prod', 'int', 'oint', 'iint', 'iiint', 'lim', 'inf', 'sup',
            'min', 'max', 'arg', 'det', 'exp', 'ln', 'log', 'sin', 'cos', 'tan',
            'sec', 'csc', 'cot', 'sinh', 'cosh', 'tanh', 'arcsin', 'arccos', 'arctan',
            
            # Symbols
            'pm', 'mp', 'times', 'div', 'cdot', 'ast', 'star', 'bullet',
            'cap', 'cup', 'sqcap', 'sqcup', 'vee', 'wedge', 'setminus',
            'wr', 'diamond', 'bigtriangleup', 'bigtriangledown', 'triangleleft',
            'triangleright', 'lhd', 'rhd', 'unlhd', 'unrhd', 'oplus', 'ominus',
            'otimes', 'oslash', 'odot', 'bigcirc', 'dagger', 'ddagger', 'amalg',
            
            # Relations
            'leq', 'geq', 'equiv', 'models', 'prec', 'succ', 'sim', 'perp',
            'preceq', 'succeq', 'simeq', 'mid', 'll', 'gg', 'asymp', 'parallel',
            'subset', 'supset', 'approx', 'bowtie', 'subseteq', 'supseteq',
            'cong', 'sqsubset', 'sqsupset', 'neq', 'smile', 'sqsubseteq',
            'sqsupseteq', 'doteq', 'frown', 'in', 'ni', 'propto', 'vdash',
            'dashv', 'exists', 'forall',
            
            # Arrows
            'leftarrow', 'rightarrow', 'uparrow', 'downarrow', 'leftrightarrow',
            'updownarrow', 'Leftarrow', 'Rightarrow', 'Uparrow', 'Downarrow',
            'Leftrightarrow', 'Updownarrow', 'mapsto', 'longmapsto', 'hookleftarrow',
            'hookrightarrow', 'leftharpoonup', 'rightharpoonup', 'leftharpoondown',
            'rightharpoondown', 'rightleftharpoons', 'leadsto',
            
            # Formatting
            'frac', 'sqrt', 'overline', 'underline', 'overbrace', 'underbrace',
            'overset', 'underset', 'stackrel', 'text', 'mathrm', 'mathbf',
            'mathit', 'mathsf', 'mathtt', 'mathcal', 'mathbb', 'mathfrak',
            
            # Environments
            'matrix', 'pmatrix', 'bmatrix', 'vmatrix', 'Vmatrix', 'array',
            'align', 'aligned', 'gather', 'gathered', 'split', 'multline',
            'cases', 'dcases',
            
            # Spacing
            'quad', 'qquad', 'hspace', 'vspace', 'phantom', 'hphantom', 'vphantom',
            
            # Delimiters
            'left', 'right', 'big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr',
            'Bigl', 'Bigr', 'biggl', 'biggr', 'Biggl', 'Biggr'
        }
        
        # Renderer-specific configurations
        self.renderer_config = {
            'katex': {
                'delimiters': [
                    {'left': '$$', 'right': '$$', 'display': True},
                    {'left': '$', 'right': '$', 'display': False},
                    {'left': '\\[', 'right': '\\]', 'display': True},
                    {'left': '\\(', 'right': '\\)', 'display': False}
                ],
                'strict': self.strict_mode,
                'trust': False,
                'macros': {}
            },
            'mathjax': {
                'tex': {
                    'inlineMath': [['$', '$'], ['\\(', '\\)']],
                    'displayMath': [['$$', '$$'], ['\\[', '\\]']],
                    'processEscapes': True,
                    'processEnvironments': True
                },
                'options': {
                    'ignoreHtmlClass': 'tex2jax_ignore',
                    'processHtmlClass': 'tex2jax_process'
                }
            }
        }
    
    def process_text(self, text: str) -> str:
        """
        Process text containing LaTeX expressions.
        
        Args:
            text: Text that may contain LaTeX expressions
            
        Returns:
            Processed text with rendered mathematical expressions
        """
        if not text:
            return text
        
        # Auto-convert Unicode if enabled
        if self.auto_convert_unicode:
            text = convert_unicode_to_latex(text)
        
        # Process different types of math expressions
        text = self._process_display_math(text)
        text = self._process_inline_math(text)
        text = self._process_text_commands(text)
        
        return text
    
    def render_latex_with_validation(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Render LaTeX text with validation feedback.
        
        Args:
            text: Text containing LaTeX expressions
            
        Returns:
            Tuple of (rendered_text, validation_results)
        """
        if not text or not isinstance(text, str):
            return text, {'status': 'empty', 'issues': []}
        
        # Step 1: Validate mathematical content
        validation_results = self.validator.validate_math_content(text)
        
        # Step 2: Normalize LaTeX formatting (from Q2LMS utils.py)
        normalized_text = self.normalize_latex_for_display(text)
        
        # Step 3: Apply space protection
        final_text = self._protect_latex_spaces(normalized_text)
        
        # Step 4: Add validation status
        validation_results['rendered_text'] = final_text
        validation_results['normalization_applied'] = (text != normalized_text)
        
        return final_text, validation_results
    
    def normalize_latex_for_display(self, text: str) -> str:
        """
        Fix common LLM LaTeX formatting issues for consistent display.
        Extracted from Q2LMS utils.py
        """
        if not text or not isinstance(text, str):
            return text
        
        # Fix degree symbols using simple string replacement
        text = text.replace('\\,^\\circ', '^{\\circ}')
        text = text.replace('^\\circ', '^{\\circ}')
        text = text.replace('\\,^\\degree', '^{\\circ}')
        text = text.replace('^\\degree', '^{\\circ}')
        
        # Fix degree symbols in numeric patterns
        text = re.sub(r'(\d+\.?\d*)\^\\circ', r'\1^{\\circ}', text)
        
        # Fix angle notation patterns - comprehensive handling
        text = text.replace('\\\\angle', '\\angle')
        
        # Fix angle notation in plain text (not wrapped in $...$) - add proper LaTeX wrapping
        # Handle positive and negative angles
        text = re.sub(r'(\d+\.?\d*)\s*\\angle\s*(-?\d+\.?\d*)\^{\\circ}', r'$\1 \\angle \2^{\\circ}$', text)
        
        # Fix angle notation already inside $...$ delimiters  
        text = re.sub(r'\$([\d.]+)\s*\\angle\s*([-\d.]+)\^{\\circ}\$', r'$\1 \\angle \2^{\\circ}$', text)
        
        # Handle cases where angle has no spaces (including negative angles)
        text = re.sub(r'(\d+\.?\d*)\\angle(-?\d+\.?\d*)\^{\\circ}', r'$\1 \\angle \2^{\\circ}$', text)
        
        # Fix Unicode degree inside LaTeX
        if '$' in text and '°' in text:
            parts = text.split('$')
            for i in range(1, len(parts), 2):
                parts[i] = parts[i].replace('°', '^{\\circ}')
            text = '$'.join(parts)
        
        # Fix subscripts and superscripts - add braces if missing
        text = re.sub(r'_([a-zA-Z0-9])(?![{])', r'_{\1}', text)
        text = re.sub(r'\^([a-zA-Z0-9])(?![{])', r'^{\1}', text)
        
        # Fix spacing issues carefully
        text = re.sub(r'\s{2,}\$', r' $', text)
        text = re.sub(r'\$\s+', r'$', text)
        
        # Only fix spacing after Omega symbols specifically
        text = re.sub(r'\$([^$]*\\Omega[^$]*)\$([a-zA-Z])', r'$\1$ \2', text)
        
        # Fix common symbols
        text = text.replace('\\ohm', '\\Omega')
        text = text.replace('\\micro', '\\mu')
        
        return text
    
    def _protect_latex_spaces(self, text: str) -> str:
        """
        Add proper spacing around LaTeX expressions for Streamlit compatibility.
        Extracted from Q2LMS utils.py
        """
        if not text:
            return text
        
        # Add space after LaTeX expressions that are followed by letters
        # This handles cases like "$0.707$times" -> "$0.707$ times"
        text = re.sub(r'\$([^$]+)\$([a-zA-Z])', r'$\1$ \2', text)
        
        # Add space before LaTeX expressions that are preceded by letters  
        # This handles cases like "frequency$f_c$" -> "frequency $f_c$"
        text = re.sub(r'([a-zA-Z])\$([^$]+)\$', r'\1 $\2$', text)
        
        return text
    
    def find_latex_expressions(self, text: str) -> List[Dict[str, Any]]:
        """
        Find all LaTeX expressions in text.
        Extracted from Q2LMS latex_converter.py
        """
        if not text:
            return []
        
        expressions = []
        for match in re.finditer(self.block_pattern, text):
            expressions.append({
                'type': 'block', 'full_match': match.group(0), 'content': match.group(1),
                'start': match.start(), 'end': match.end()
            })
        for match in re.finditer(self.inline_pattern, text):
            overlaps = any(expr['start'] <= match.start() <= expr['end'] for expr in expressions if expr['type'] == 'block')
            if not overlaps:
                expressions.append({
                    'type': 'inline', 'full_match': match.group(0), 'content': match.group(1),
                    'start': match.start(), 'end': match.end()
                })
        expressions.sort(key=lambda x: x['start'])
        return expressions
    
    def has_latex(self, text: str) -> bool:
        """Check if text contains LaTeX expressions"""
        return bool(re.search(self.combined_pattern, str(text) if text else ''))
    
    def convert_for_canvas(self, text: str) -> str:
        """
        Convert LaTeX delimiters to Canvas/QTI format.
        Extracted from Q2LMS latex_converter.py
        """
        if not text:
            return ""
        
        expressions = self.find_latex_expressions(text)
        
        if not expressions:
            return text 
        
        result_parts = []
        last_end = 0
        
        for expr in expressions:
            text_before = text[last_end:expr['start']]
            if text_before:
                spaced_text_before = self._add_space_before_latex(text_before) 
                result_parts.append(spaced_text_before)
            
            # Add the converted LaTeX expression for Canvas
            if expr['type'] == 'block':
                latex_output = f"{self.canvas_block_start}{expr['content']}{self.canvas_block_end}"
            else: # Inline math
                latex_output = f"{self.canvas_inline_start}{expr['content']}{self.canvas_inline_end}"
            
            result_parts.append(latex_output) 
            last_end = expr['end']
        
        remaining_text = text[last_end:]
        if remaining_text:
            result_parts.append(remaining_text)
        
        return ''.join(result_parts)
    
    def _add_space_before_latex(self, text_before: str) -> str:
        """Add appropriate spacing before LaTeX expressions"""
        if not text_before: 
            return text_before
        
        last_char = text_before[-1]
        if last_char.isalnum() or last_char in ')]}':
            no_space_patterns = [r'[=(<\[\{]$', r'[+\-*/^]$', r'[,:;]$']
            for pattern in no_space_patterns:
                if re.search(pattern, text_before):
                    return text_before
            return text_before + ' '
        return text_before


class MathValidationManager:
    """
    Mathematical validation system for Q2JSON.
    Enhanced version of Q2LMS validation with Q2JSON-specific rules.
    """
    
    def __init__(self):
        self.validation_rules = {
            'critical': [
                'unmatched_delimiters',
                'invalid_latex_syntax',
                'unicode_in_math'
            ],
            'warning': [
                'missing_units',
                'inconsistent_notation',
                'spacing_issues'
            ],
            'info': [
                'optimization_suggestions',
                'accessibility_improvements'
            ]
        }
    
    def validate_math_content(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive mathematical validation for Q2JSON.
        
        Args:
            text: Text to validate
            
        Returns:
            Dict with validation results and flagging information
        """
        if not text:
            return {'status': 'empty', 'issues': []}
        
        results = {
            'status': 'valid',
            'issues': [],
            'flags': {
                'critical': [],
                'warning': [],
                'info': []
            },
            'statistics': {
                'latex_expressions': 0,
                'inline_math': 0,
                'block_math': 0,
                'unicode_symbols': 0
            }
        }
        
        # Find all LaTeX expressions
        processor = Q2JSONLaTeXProcessor()
        expressions = processor.find_latex_expressions(text)
        
        results['statistics']['latex_expressions'] = len(expressions)
        results['statistics']['inline_math'] = sum(1 for expr in expressions if expr['type'] == 'inline')
        results['statistics']['block_math'] = sum(1 for expr in expressions if expr['type'] == 'block')
        
        # Validate each expression
        for expr in expressions:
            expr_issues = self._validate_single_expression(expr)
            for level, issues in expr_issues.items():
                results['flags'][level].extend(issues)
        
        # Global validations
        global_issues = self._validate_global_patterns(text)
        for level, issues in global_issues.items():
            results['flags'][level].extend(issues)
        
        # Check for Unicode symbols
        unicode_count = self._count_unicode_math_symbols(text)
        results['statistics']['unicode_symbols'] = unicode_count
        if unicode_count > 0:
            results['flags']['warning'].append({
                'type': 'unicode_symbols',
                'message': f'Found {unicode_count} Unicode mathematical symbols that should be converted to LaTeX',
                'suggestion': 'Use LaTeX equivalents for better compatibility'
            })
        
        # Set overall status
        if results['flags']['critical']:
            results['status'] = 'critical'
        elif results['flags']['warning']:
            results['status'] = 'warning'
        else:
            results['status'] = 'valid'
        
        return results
    
    def _validate_single_expression(self, expr: Dict[str, Any]) -> Dict[str, List]:
        """Validate a single LaTeX expression"""
        issues = {'critical': [], 'warning': [], 'info': []}
        content = expr['content']
        
        # Check for basic syntax issues
        if not content.strip():
            issues['critical'].append({
                'type': 'empty_expression',
                'message': 'Empty LaTeX expression found',
                'location': f"Position {expr['start']}-{expr['end']}"
            })
        
        # Check for unmatched braces
        brace_count = content.count('{') - content.count('}')
        if brace_count != 0:
            issues['critical'].append({
                'type': 'unmatched_braces',
                'message': f'Unmatched braces in LaTeX expression: {brace_count} extra {"opening" if brace_count > 0 else "closing"}',
                'content': content[:50] + '...' if len(content) > 50 else content
            })
        
        # Check for common LaTeX issues
        if '\\\\' in content:
            issues['warning'].append({
                'type': 'double_backslash',
                'message': 'Double backslashes found - may cause rendering issues',
                'content': content[:50] + '...' if len(content) > 50 else content
            })
        
        return issues
    
    def _validate_global_patterns(self, text: str) -> Dict[str, List]:
        """Validate global patterns in the entire text"""
        issues = {'critical': [], 'warning': [], 'info': []}
        
        # Check for unmatched dollar signs
        dollar_count = text.count('$')
        if dollar_count % 2 != 0:
            issues['critical'].append({
                'type': 'unmatched_delimiters',
                'message': 'Unmatched $ delimiters - odd number found',
                'count': dollar_count
            })
        
        # Check for mixed delimiter styles
        if '\\(' in text or '\\[' in text:
            issues['warning'].append({
                'type': 'mixed_delimiters',
                'message': 'Mixed LaTeX delimiter styles found - recommend using $ consistently',
                'suggestion': 'Use $...$ for inline and $$...$$ for display math'
            })
        
        return issues
    
    def _count_unicode_math_symbols(self, text: str) -> int:
        """Count Unicode mathematical symbols that should be LaTeX"""
        unicode_math_chars = 'αβγδεζηθικλμνξπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΠΡΣΤΥΦΧΨΩ±×÷√∞∫∑∏∂∇°²³⁴⁵⁶⁷⁸⁹⁰₀₁₂₃₄₅₆₇₈₉Ω'
        return sum(1 for char in text if char in unicode_math_chars)
    
    def get_validation_summary(self, validation_results: Dict[str, Any]) -> str:
        """Get a human-readable validation summary"""
        if validation_results['status'] == 'empty':
            return "No mathematical content to validate"
        
        status = validation_results['status']
        stats = validation_results['statistics']
        flags = validation_results['flags']
        
        summary = f"**Validation Status: {status.upper()}**\n\n"
        summary += f"📊 **Statistics:**\n"
        summary += f"- LaTeX expressions: {stats['latex_expressions']}\n"
        summary += f"- Inline math: {stats['inline_math']}\n"
        summary += f"- Block math: {stats['block_math']}\n"
        summary += f"- Unicode symbols: {stats['unicode_symbols']}\n\n"
        
        if flags['critical']:
            summary += f"🚨 **Critical Issues ({len(flags['critical'])}):**\n"
            for issue in flags['critical'][:3]:  # Show first 3
                summary += f"- {issue.get('message', 'Unknown issue')}\n"
            if len(flags['critical']) > 3:
                summary += f"- ... and {len(flags['critical']) - 3} more\n"
            summary += "\n"
        
        if flags['warning']:
            summary += f"⚠️ **Warnings ({len(flags['warning'])}):**\n"
            for issue in flags['warning'][:3]:  # Show first 3
                summary += f"- {issue.get('message', 'Unknown warning')}\n"
            if len(flags['warning']) > 3:
                summary += f"- ... and {len(flags['warning']) - 3} more\n"
            summary += "\n"
        
        return summary
