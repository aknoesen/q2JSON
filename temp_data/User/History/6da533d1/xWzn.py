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
        
        # Initialize validator
        self.validator = MathValidationManager(self)
        
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
        
        # Initialize validator for use by render_latex_with_validation
        self.validator = MathValidationManager(self)
    
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

    def _process_display_math(self, text: str) -> str:
        """Process display math expressions ($$...$$)."""
        def replace_display_math(match):
            latex_expr = match.group(1).strip()
            validation_result = self.validate_latex_expression(latex_expr)
            
            if validation_result.is_valid:
                return self._render_math_expression(latex_expr, display=True)
            else:
                # Return with error indication
                return f'<span class="math-error" title="LaTeX Error: {"; ".join(validation_result.errors)}">$$${latex_expr}$$$</span>'
        
        return self.latex_patterns['display_math'].sub(replace_display_math, text)
    
    def _process_inline_math(self, text: str) -> str:
        """Process inline math expressions ($...$)."""
        def replace_inline_math(match):
            latex_expr = match.group(1).strip()
            validation_result = self.validate_latex_expression(latex_expr)
            
            if validation_result.is_valid:
                return self._render_math_expression(latex_expr, display=False)
            else:
                # Return with error indication
                return f'<span class="math-error" title="LaTeX Error: {"; ".join(validation_result.errors)}">${latex_expr}$</span>'
        
        return self.latex_patterns['inline_math'].sub(replace_inline_math, text)
    
    def _process_text_commands(self, text: str) -> str:
        """Process LaTeX text commands outside of math mode."""
        # Handle common text formatting commands
        text_commands = {
            r'\\textbf\{([^}]+)\}': r'<strong>\1</strong>',
            r'\\textit\{([^}]+)\}': r'<em>\1</em>',
            r'\\underline\{([^}]+)\}': r'<u>\1</u>',
            r'\\texttt\{([^}]+)\}': r'<code>\1</code>',
        }
        
        for pattern, replacement in text_commands.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _render_math_expression(self, latex_expr: str, display: bool = False) -> str:
        """Render a LaTeX mathematical expression."""
        if self.renderer == 'katex':
            return self._render_katex(latex_expr, display)
        elif self.renderer == 'mathjax':
            return self._render_mathjax(latex_expr, display)
        else:
            return self._render_plain(latex_expr, display)
    
    def _render_katex(self, latex_expr: str, display: bool = False) -> str:
        """Render expression for KaTeX."""
        display_mode = 'true' if display else 'false'
        escaped_latex = html.escape(latex_expr)
        
        return f'''
        <span class="katex-expression" 
              data-latex="{escaped_latex}" 
              data-display="{display_mode}">
            {f"$${latex_expr}$$" if display else f"${latex_expr}$"}
        </span>
        '''
    
    def _render_mathjax(self, latex_expr: str, display: bool = False) -> str:
        """Render expression for MathJax."""
        if display:
            return f'\\[{latex_expr}\\]'
        else:
            return f'\\({latex_expr}\\)'
    
    def _render_plain(self, latex_expr: str, display: bool = False) -> str:
        """Render expression as plain text with basic formatting."""
        # Simple text representation
        processed = latex_expr
        
        # Replace common commands with Unicode
        replacements = {
            r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
            r'\\epsilon': 'ε', r'\\pi': 'π', r'\\sigma': 'σ', r'\\omega': 'ω',
            r'\\infty': '∞', r'\\sum': '∑', r'\\int': '∫', r'\\pm': '±',
            r'\\times': '×', r'\\div': '÷', r'\\leq': '≤', r'\\geq': '≥',
            r'\\neq': '≠', r'\\approx': '≈', r'\\sqrt': '√'
        }
        
        for latex_cmd, unicode_char in replacements.items():
            processed = re.sub(latex_cmd + r'\b', unicode_char, processed)
        
        # Handle fractions
        processed = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', processed)
        
        # Handle superscripts and subscripts
        processed = re.sub(r'\^\{([^}]+)\}', r'^(\1)', processed)
        processed = re.sub(r'_\{([^}]+)\}', r'_(\1)', processed)
        
        if display:
            return f'<div class="math-display">{processed}</div>'
        else:
            return f'<span class="math-inline">{processed}</span>'
    
    def validate_latex_expression(self, latex_expr: str) -> MathValidationResult:
        """
        Validate a LaTeX mathematical expression.
        
        Args:
            latex_expr: LaTeX expression to validate
            
        Returns:
            MathValidationResult with validation details
        """
        errors = []
        warnings = []
        suggestions = []
        
        if not latex_expr.strip():
            errors.append("Empty LaTeX expression")
            return MathValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                processed_expression=latex_expr,
                render_html=""
            )
        
        # Check for balanced braces
        brace_errors = self._check_balanced_braces(latex_expr)
        errors.extend(brace_errors)
        
        # Check for valid commands
        command_issues = self._check_latex_commands(latex_expr)
        errors.extend(command_issues['errors'])
        warnings.extend(command_issues['warnings'])
        suggestions.extend(command_issues['suggestions'])
        
        # Check for common syntax issues
        syntax_issues = self._check_syntax_issues(latex_expr)
        errors.extend(syntax_issues['errors'])
        warnings.extend(syntax_issues['warnings'])
        suggestions.extend(syntax_issues['suggestions'])
        
        # Generate processed expression and HTML
        processed_expression = self._normalize_expression(latex_expr)
        render_html = self._render_math_expression(processed_expression) if not errors else ""
        
        return MathValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            processed_expression=processed_expression,
            render_html=render_html
        )
    
    def _check_balanced_braces(self, latex_expr: str) -> List[str]:
        """Check for balanced braces in LaTeX expression."""
        errors = []
        stack = []
        brace_pairs = {'(': ')', '[': ']', '{': '}'}
        
        for i, char in enumerate(latex_expr):
            if char in brace_pairs:
                stack.append((char, i))
            elif char in brace_pairs.values():
                if not stack:
                    errors.append(f"Unmatched closing brace '{char}' at position {i}")
                else:
                    opening, pos = stack.pop()
                    expected = brace_pairs[opening]
                    if char != expected:
                        errors.append(f"Mismatched braces: '{opening}' at {pos} and '{char}' at {i}")
        
        # Check for unclosed braces
        for opening, pos in stack:
            errors.append(f"Unclosed brace '{opening}' at position {pos}")
        
        return errors
    
    def _check_latex_commands(self, latex_expr: str) -> Dict[str, List[str]]:
        """Check LaTeX commands for validity."""
        errors = []
        warnings = []
        suggestions = []
        
        # Find all LaTeX commands
        commands = self.latex_patterns['latex_command'].findall(latex_expr)
        
        for command_name, _ in commands:
            if command_name not in self.valid_commands:
                if self.strict_mode:
                    errors.append(f"Unknown LaTeX command: \\{command_name}")
                else:
                    warnings.append(f"Unknown LaTeX command: \\{command_name}")
                
                # Suggest similar commands
                similar = self._find_similar_commands(command_name)
                if similar:
                    suggestions.append(f"Did you mean: {', '.join(f'\\{cmd}' for cmd in similar[:3])}?")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _check_syntax_issues(self, latex_expr: str) -> Dict[str, List[str]]:
        """Check for common LaTeX syntax issues."""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for empty groups
        if re.search(r'\{\s*\}', latex_expr):
            warnings.append("Empty braces found")
        
        # Check for double superscripts/subscripts without braces
        if re.search(r'\^[^{]\^', latex_expr):
            errors.append("Double superscript without braces")
        if re.search(r'_[^{]_', latex_expr):
            errors.append("Double subscript without braces")
        
        # Check for missing arguments to commands that require them
        required_arg_commands = ['frac', 'sqrt', 'overline', 'underline', 'text']
        for cmd in required_arg_commands:
            pattern = f'\\\\{cmd}(?!\\{{)'
            if re.search(pattern, latex_expr):
                errors.append(f"Command \\{cmd} requires an argument")
        
        # Check for invalid character sequences
        if re.search(r'[{}](?:\s*[{}])+', latex_expr):
            warnings.append("Multiple consecutive braces may cause rendering issues")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _find_similar_commands(self, command: str) -> List[str]:
        """Find similar LaTeX commands using simple string matching."""
        similar = []
        command_lower = command.lower()
        
        for valid_cmd in self.valid_commands:
            # Simple similarity: commands that start with same letters or contain the command
            if (valid_cmd.startswith(command_lower[:3]) or 
                command_lower in valid_cmd or 
                valid_cmd in command_lower):
                similar.append(valid_cmd)
        
        return sorted(similar)[:5]  # Return top 5 matches
    
    def _normalize_expression(self, latex_expr: str) -> str:
        """Normalize LaTeX expression for consistent rendering."""
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', latex_expr.strip())
        
        # Standardize spacing around operators
        normalized = re.sub(r'\s*([+\-*/^])\s*', r' \1 ', normalized)
        
        # Ensure proper spacing in fractions
        normalized = re.sub(r'\\frac\s*\{', r'\\frac{', normalized)
        
        return normalized
    
    def extract_math_expressions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all mathematical expressions from text.
        
        Args:
            text: Text containing LaTeX expressions
            
        Returns:
            List of dictionaries with expression details
        """
        expressions = []
        
        # Find display math
        for match in self.latex_patterns['display_math'].finditer(text):
            expressions.append({
                'type': 'display',
                'expression': match.group(1),
                'start': match.start(),
                'end': match.end(),
                'full_match': match.group(0)
            })
        
        # Find inline math
        for match in self.latex_patterns['inline_math'].finditer(text):
            expressions.append({
                'type': 'inline',
                'expression': match.group(1),
                'start': match.start(),
                'end': match.end(),
                'full_match': match.group(0)
            })
        
        # Sort by position
        expressions.sort(key=lambda x: x['start'])
        
        return expressions

    def get_renderer_config(self) -> Dict[str, Any]:
        """Get configuration for the current renderer."""
        return self.renderer_config.get(self.renderer, {})
    
    def generate_css(self) -> str:
        """Generate CSS for mathematical expressions."""
        return """
        .katex-expression {
            font-family: 'KaTeX_Main', 'Times New Roman', serif;
        }
        
        .math-display {
            display: block;
            text-align: center;
            margin: 1em 0;
            font-size: 1.1em;
        }
        
        .math-inline {
            display: inline;
            font-size: 1em;
        }
        
        .math-error {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
            border: 1px solid #f8bbd9;
        }
        
        .latex-warning {
            color: #f57c00;
            background-color: #fff3e0;
            padding: 2px 4px;
            border-radius: 3px;
            border: 1px solid #ffcc80;
        }
        """
    
    def generate_javascript(self) -> str:
        """Generate JavaScript for renderer initialization."""
        if self.renderer == 'katex':
            return self._generate_katex_js()
        elif self.renderer == 'mathjax':
            return self._generate_mathjax_js()
        else:
            return ""
    
    def _generate_katex_js(self) -> str:
        """Generate KaTeX initialization JavaScript."""
        config = json.dumps(self.renderer_config['katex'])
        
        return f"""
        // Initialize KaTeX rendering
        document.addEventListener('DOMContentLoaded', function() {{
            const mathElements = document.querySelectorAll('.katex-expression');
            
            mathElements.forEach(function(element) {{
                const latex = element.getAttribute('data-latex');
                const displayMode = element.getAttribute('data-display') === 'true';
                
                try {{
                    katex.render(latex, element, {{
                        displayMode: displayMode,
                        throwOnError: false,
                        strict: {str(self.strict_mode).lower()},
                        trust: false
                    }});
                }} catch (error) {{
                    console.error('KaTeX rendering error:', error);
                    element.innerHTML = '<span class="math-error">' + latex + '</span>';
                }}
            }});
        }});
        """
    
    def _generate_mathjax_js(self) -> str:
        """Generate MathJax initialization JavaScript."""
        config = json.dumps(self.renderer_config['mathjax'])
        
        return f"""
        // MathJax configuration
        window.MathJax = {config};
        
        // Re-render MathJax when content changes
        function renderMathJax() {{
            if (window.MathJax && window.MathJax.typesetPromise) {{
                window.MathJax.typesetPromise();
            }}
        }}
        """
    
    def process_latex(self, text: str) -> str:
        """
        Process LaTeX content (compatibility method for tests).
        
        Args:
            text: Text containing LaTeX expressions
            
        Returns:
            Processed text with rendered mathematical expressions
        """
        return self.process_text(text)
    
    def validate_math_content(self, text: str) -> List[Dict[str, Any]]:
        """
        Validate mathematical content in text (compatibility method for tests).
        
        Args:
            text: Text to validate
            
        Returns:
            List of validation issues
        """
        if not text:
            return []
        
        expressions = self.latex_processor.extract_math_expressions(text)
        issues = []
        
        for expr in expressions:
            validation = self.latex_processor.validate_latex_expression(expr['expression'])
            
            if not validation.is_valid:
                for error in validation.errors:
                    issues.append({
                        'type': 'error',
                        'severity': 'error',
                        'message': error,
                        'expression': expr['expression'],
                        'position': {'start': expr['start'], 'end': expr['end']},
                        'suggestion': '',
                        'auto_fixable': False
                    })
            
            for warning in validation.warnings:
                issues.append({
                    'type': 'warning',
                    'severity': 'warning',
                    'message': warning,
                    'expression': expr['expression'],
                    'position': {'start': expr['start'], 'end': expr['end']},
                    'suggestion': '',
                    'auto_fixable': False
                })
        
        return issues

class MathValidationManager:
    """
    Manager for comprehensive mathematical validation across question types.
    """
    
    def __init__(self, latex_processor: Optional[Q2JSONLaTeXProcessor] = None):
        """Initialize the math validation manager."""
        self.latex_processor = latex_processor or Q2JSONLaTeXProcessor()
    
    def validate_question_math(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all mathematical content in a question.
        
        Args:
            question: Question dictionary
            
        Returns:
            Validation result with detailed math analysis
        """
        validation_result = {
            'has_math': False,
            'math_expressions': [],
            'validation_summary': {
                'total_expressions': 0,
                'valid_expressions': 0,
                'invalid_expressions': 0,
                'warnings': 0
            },
            'issues': [],
            'suggestions': []
        }
        
        # Fields to check for mathematical content
        math_fields = [
            'question_text', 'title', 'general_feedback',
            'options', 'correct_answers', 'explanation'
        ]
        
        for field in math_fields:
            if field in question:
                field_result = self._validate_field_math(question[field], field)
                
                if field_result['has_math']:
                    validation_result['has_math'] = True
                    validation_result['math_expressions'].extend(field_result['expressions'])
                    validation_result['issues'].extend(field_result['issues'])
                    validation_result['suggestions'].extend(field_result['suggestions'])
        
        # Update summary
        validation_result['validation_summary']['total_expressions'] = len(validation_result['math_expressions'])
        validation_result['validation_summary']['valid_expressions'] = sum(
            1 for expr in validation_result['math_expressions'] if expr['is_valid']
        )
        validation_result['validation_summary']['invalid_expressions'] = (
            validation_result['validation_summary']['total_expressions'] - 
            validation_result['validation_summary']['valid_expressions']
        )
        validation_result['validation_summary']['warnings'] = sum(
            len(expr['warnings']) for expr in validation_result['math_expressions']
        )
        
        return validation_result
    
    def _validate_field_math(self, field_value: Any, field_name: str) -> Dict[str, Any]:
        """Validate mathematical content in a specific field."""
        result = {
            'has_math': False,
            'expressions': [],
            'issues': [],
            'suggestions': []
        }
        
        if isinstance(field_value, str):
            result.update(self._validate_text_math(field_value, field_name))
        elif isinstance(field_value, list):
            for i, item in enumerate(field_value):
                if isinstance(item, str):
                    item_result = self._validate_text_math(item, f"{field_name}[{i}]")
                    if item_result['has_math']:
                        result['has_math'] = True
                        result['expressions'].extend(item_result['expressions'])
                        result['issues'].extend(item_result['issues'])
                        result['suggestions'].extend(item_result['suggestions'])
        
        return result
    
    def _validate_text_math(self, text: str, context: str) -> Dict[str, Any]:
        """Validate mathematical expressions in text."""
        result = {
            'has_math': False,
            'expressions': [],
            'issues': [],
            'suggestions': []
        }
        
        # Extract mathematical expressions
        expressions = self.latex_processor.extract_math_expressions(text)
        
        if expressions:
            result['has_math'] = True
            
            for expr in expressions:
                # Validate each expression
                validation = self.latex_processor.validate_latex_expression(expr['expression'])
                
                expr_result = {
                    'context': context,
                    'type': expr['type'],
                    'expression': expr['expression'],
                    'position': {'start': expr['start'], 'end': expr['end']},
                    'is_valid': validation.is_valid,
                    'errors': validation.errors,
                    'warnings': validation.warnings,
                    'suggestions': validation.suggestions
                }
                
                result['expressions'].append(expr_result)
                
                # Add issues with context
                for error in validation.errors:
                    result['issues'].append({
                        'severity': 'error',
                        'message': f"Math error in {context}: {error}",
                        'expression': expr['expression'],
                        'type': 'math_syntax'
                    })
                
                for warning in validation.warnings:
                    result['issues'].append({
                        'severity': 'warning',
                        'message': f"Math warning in {context}: {warning}",
                        'expression': expr['expression'],
                        'type': 'math_style'
                    })
                
                result['suggestions'].extend(validation.suggestions)
        
        return result
    
    def generate_math_report(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive mathematical content report."""
        report = {
            'summary': {
                'total_questions': len(questions),
                'questions_with_math': 0,
                'total_expressions': 0,
                'valid_expressions': 0,
                'invalid_expressions': 0,
                'common_issues': {}
            },
            'question_details': [],
            'recommendations': []
        }
        
        issue_counts = {}
        
        for i, question in enumerate(questions):
            validation = self.validate_question_math(question)
            
            if validation['has_math']:
                report['summary']['questions_with_math'] += 1
            
            report['summary']['total_expressions'] += validation['validation_summary']['total_expressions']
            report['summary']['valid_expressions'] += validation['validation_summary']['valid_expressions']
            report['summary']['invalid_expressions'] += validation['validation_summary']['invalid_expressions']
            
            # Count issues
            for issue in validation['issues']:
                issue_type = issue.get('type', 'unknown')
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            # Add question details if it has math or issues
            if validation['has_math'] or validation['issues']:
                report['question_details'].append({
                    'question_number': i + 1,
                    'question_title': question.get('title', f'Question {i + 1}'),
                    'validation': validation
                })
        
        report['summary']['common_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Generate recommendations
        if report['summary']['invalid_expressions'] > 0:
            report['recommendations'].append(
                "Review and fix mathematical expressions with syntax errors before publishing."
            )
        
        if issue_counts.get('math_style', 0) > 0:
            report['recommendations'].append(
                "Consider standardizing mathematical notation for consistency."
            )
        
        if report['summary']['questions_with_math'] > 0:
            report['recommendations'].append(
                "Ensure mathematical content renders correctly in your target platform."
            )
        
        return report


# Convenience functions for easy integration
def process_latex_text(text: str, renderer: str = 'katex') -> str:
    """Process text containing LaTeX expressions."""
    processor = Q2JSONLaTeXProcessor(renderer=renderer)
    return processor.process_text(text)


def validate_math_expression(expression: str) -> MathValidationResult:
    """Validate a single mathematical expression."""
    processor = Q2JSONLaTeXProcessor()
    return processor.validate_latex_expression(expression)


def validate_question_math(question: Dict[str, Any]) -> Dict[str, Any]:
    """Validate mathematical content in a question."""
    validator = MathValidationManager()
    return validator.validate_question_math(question)
