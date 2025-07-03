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
