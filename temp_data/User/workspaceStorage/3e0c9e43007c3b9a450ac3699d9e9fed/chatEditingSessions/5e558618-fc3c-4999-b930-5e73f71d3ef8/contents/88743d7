"""
Core JSON processing and validation logic (Stage 3)
Extracted from main app for direct testing and iteration
"""

import json
import re
import time
from typing import Dict, List, Tuple, Optional, Any
from .llm_repairs import get_repair_function


class JSONProcessor:
    """
    Core JSON processing logic equivalent to Stage 3 functionality
    Handles parsing, validation, repair, and export of educational questions
    """
    
    def __init__(self):
        self.repair_attempts = []
        self.validation_results = {}
        self.processing_log = []
    



    
    def process_raw_json(self, raw_json: str, llm_type: str = "auto") -> Tuple[bool, Optional[Dict], List[str]]:
        """Main processing function"""
        messages = []
        # Apply simple preprocessing to extract JSON from markdown blocks and fix
        preprocessed_json = self._simple_preprocess(raw_json)
        
        # Add message if preprocessing made changes to the input
        if preprocessed_json != raw_json:
            messages.append("✅ Preprocessing applied - cleaned LLM response")  # This line needs proper indent
        
        try:
            # Parse the preprocessed JSON instead of raw JSON
            questions_data = json.loads(preprocessed_json)
            # Parse the preprocessed JSON instead of raw JSON
            # Add message if preprocessing made changes to the input
            
            if self._validate_questions_structure(questions_data):
                messages.append("✅ Direct JSON parsing successful")
                return True, questions_data, messages
            else:
                messages.append("❌ Valid JSON but missing 'questions' array")
                return False, None, messages
                
        except json.JSONDecodeError as e:
            messages.append(f"❌ JSON parsing error: {str(e)}")
        
        # Step 2: Attempt automatic repair
        messages.append("🔧 Attempting automatic repair...")

        # Use preprocessed JSON for repair instead of raw JSON
        try:
            repaired_json = self.auto_repair_json(preprocessed_json, llm_type)
            questions_data = json.loads(repaired_json)
            
            if self._validate_questions_structure(questions_data):
                messages.append("✅ JSON automatically repaired!")
                return True, questions_data, messages
            else:
                messages.append("❌ Repaired JSON missing 'questions' array")
                return False, None, messages
                
        except json.JSONDecodeError as e2:
            messages.append(f"❌ Auto-repair failed: {str(e2)}")
            return False, None, messages
        except Exception as e3:
            messages.append(f"❌ Repair function error: {str(e3)}")
            return False, None, messages
    
    def auto_repair_json(self, raw_json: str, llm_type: str = "auto") -> str:
        """
        Attempt automatic JSON repair using LLM-specific strategies
        
        Args:
            raw_json: Raw JSON string to repair
            llm_type: LLM type for specific repair strategy
            
        Returns:
            Repaired JSON string
        """
        # Get appropriate repair function
        repair_func = get_repair_function(llm_type)
        
        # Apply repair
        repaired = repair_func(raw_json)
        
        # Log repair attempt
        self.repair_attempts.append({
            'llm_type': llm_type,
            'original_length': len(raw_json),
            'repaired_length': len(repaired),
            'changes_made': len(raw_json) != len(repaired)
        })
        
        return repaired
    
    def _validate_questions_structure(self, questions_data: Dict) -> bool:
        """
        Validate that JSON has proper questions array structure
        
        Args:
            questions_data: Parsed JSON data
            
        Returns:
            True if valid structure, False otherwise
        """
        if not isinstance(questions_data, dict):
            return False
            
        if 'questions' not in questions_data:
            return False
            
        if not isinstance(questions_data['questions'], list):
            return False
            
        if len(questions_data['questions']) == 0:
            return False
            
        return True
    
    def validate_questions(self, questions_data: Dict) -> Dict:
        """
        Comprehensive validation of question content and structure
        Three-tier validation: Structure, LaTeX, Mathematical Consistency
        
        Args:
            questions_data: Parsed questions data
            
        Returns:
            Dictionary with validation results
        """
        questions = questions_data.get('questions', [])
        
        validation_results = {
            'total': len(questions),
            'valid': 0,
            'warnings': 0,
            'errors': 0,
            'issues': [],
            'question_analysis': [],
            'unicode_violations': [],
            'latex_issues': [],
            'mathematical_consistency': {}  # New: Mathematical consistency results
        }
        
        required_fields = ['type', 'title', 'question_text']
        
        for i, question in enumerate(questions):
            q_analysis = {
                'index': i + 1,
                'title': question.get('title', f'Question {i+1}'),
                'type': question.get('type', 'unknown'),
                'status': 'valid',
                'issues': [],
                'unicode_violations': [],
                'latex_issues': [],
                'mathematical_issues': []  # New: Mathematical consistency issues
            }
            
            # Check required fields
            for field in required_fields:
                if field not in question or not question[field]:
                    q_analysis['issues'].append(f"Missing {field}")
                    q_analysis['status'] = 'error'
            
            # Validate Unicode compliance (CRITICAL requirement)
            unicode_issues = self._check_unicode_violations(question)
            if unicode_issues:
                q_analysis['unicode_violations'].extend(unicode_issues)
                q_analysis['status'] = 'error'
                validation_results['unicode_violations'].extend(unicode_issues)
            
            # Validate LaTeX formatting
            latex_issues = self._check_latex_formatting(question)
            if latex_issues:
                q_analysis['latex_issues'].extend(latex_issues)
                if q_analysis['status'] == 'valid':
                    q_analysis['status'] = 'warning'
                validation_results['latex_issues'].extend(latex_issues)
            
            # Phase 3: Mathematical consistency validation for numerical questions
            if question.get('type') == 'numerical':
                mathematical_issues = self._check_mathematical_consistency_single(question)
                if mathematical_issues:
                    q_analysis['mathematical_issues'].extend(mathematical_issues)
                    if q_analysis['status'] == 'valid':
                        q_analysis['status'] = 'warning'
            
            # Validate question type specific requirements
            q_type = question.get('type')
            if q_type == 'multiple_choice':
                if 'choices' not in question:
                    q_analysis['issues'].append("Missing choices array")
                    q_analysis['status'] = 'error'
                elif len(question.get('choices', [])) != 4:
                    q_analysis['issues'].append(f"Expected 4 choices, found {len(question.get('choices', []))}")
                    q_analysis['status'] = 'warning'
            
            elif q_type == 'numerical':
                if 'correct_answer' in question:
                    try:
                        float(str(question['correct_answer']))
                    except (ValueError, TypeError):
                        q_analysis['issues'].append("Correct answer is not numeric")
                        q_analysis['status'] = 'error'
            
            elif q_type == 'true_false':
                if 'correct_answer' in question:
                    if str(question['correct_answer']).lower() not in ['true', 'false']:
                        q_analysis['issues'].append("Correct answer must be 'True' or 'False'")
                        q_analysis['status'] = 'error'
            
            # Count status
            if q_analysis['status'] == 'valid':
                validation_results['valid'] += 1
            elif q_analysis['status'] == 'warning':
                validation_results['warnings'] += 1
            else:
                validation_results['errors'] += 1
            
            validation_results['question_analysis'].append(q_analysis)
        
        # Phase 3: Complete mathematical consistency analysis
        mathematical_analysis = self._detect_mathematical_consistency(questions_data)
        validation_results['mathematical_consistency'] = mathematical_analysis
        
        self.validation_results = validation_results
        return validation_results
    
    def _check_unicode_violations(self, question: Dict) -> List[str]:
        """
        Check for forbidden Unicode characters as per preamble requirements
        
        Args:
            question: Question dictionary to check
            
        Returns:
            List of Unicode violation descriptions
        """
        violations = []
        
        # Define forbidden Unicode characters
        forbidden_unicode = {
            'Ω': '$\\Omega$',
            '°': '$^\\circ$',
            '²': '$^2$',
            '³': '$^3$',
            'μ': '$\\mu$',
            'π': '$\\pi$',
            '±': '$\\pm$',
            '≤': '$\\leq$',
            '≥': '$\\geq$',
            '∞': '$\\infty$',
            'α': '$\\alpha$',
            'β': '$\\beta$',
            'γ': '$\\gamma$',
            'θ': '$\\theta$',
            'λ': '$\\lambda$',
            'σ': '$\\sigma$',
            '×': '$\\times$',
            '÷': '$\\div$',
            '√': '$\\sqrt{}$',
        }
        
        # Check all string fields in the question
        fields_to_check = ['title', 'question_text', 'feedback_correct', 'feedback_incorrect']
        
        # Add choices if they exist
        if 'choices' in question and isinstance(question['choices'], list):
            fields_to_check.extend([f'choice_{i}' for i in range(len(question['choices']))])
            
        for field in fields_to_check:
            if field.startswith('choice_'):
                # Extract choice index and get value
                choice_idx = int(field.split('_')[1])
                if choice_idx < len(question.get('choices', [])):
                    text = str(question['choices'][choice_idx])
                else:
                    continue
            else:
                text = str(question.get(field, ''))
            
            if text:
                for unicode_char, latex_equiv in forbidden_unicode.items():
                    if unicode_char in text:
                        violations.append(
                            f"Field '{field}' contains forbidden Unicode '{unicode_char}' - use {latex_equiv}"
                        )
        
        return violations
    
    def _check_latex_formatting(self, question: Dict) -> List[str]:
        """
        Check for proper LaTeX formatting in mathematical content
        
        Args:
            question: Question dictionary to check
            
        Returns:
            List of LaTeX formatting issues
        """
        issues = []
        
        # Fields that should contain LaTeX math
        math_fields = ['question_text', 'feedback_correct', 'feedback_incorrect', 'choices']
        
        for field in math_fields:
            if field == 'choices' and 'choices' in question:
                # Check each choice
                for i, choice in enumerate(question['choices']):
                    choice_issues = self._analyze_latex_in_text(str(choice), f'choice_{i+1}')
                    issues.extend(choice_issues)
            else:
                text = str(question.get(field, ''))
                if text:
                    field_issues = self._analyze_latex_in_text(text, field)
                    issues.extend(field_issues)
        
        return issues
    
    def _analyze_latex_in_text(self, text: str, field_name: str) -> List[str]:
        """
        Analyze text for LaTeX formatting issues
        
        Args:
            text: Text to analyze
            field_name: Name of the field being analyzed
            
        Returns:
            List of LaTeX issues found
        """
        issues = []
        
        # Check for display math ($$...$$) which can cause JSON issues
        if '$$' in text:
            issues.append(f"Field '{field_name}' contains display math ($$...$$) - use inline math ($...$)")
        
        # Check for unmatched dollar signs
        dollar_count = text.count('$')
        if dollar_count % 2 != 0:
            issues.append(f"Field '{field_name}' has unmatched $ delimiters")
        
        # Check for double backslashes in LaTeX (common ChatGPT issue)
        problematic_patterns = [
            '\\\\frac', '\\\\text', '\\\\sqrt', '\\\\times', '\\\\circ',
            '\\\\mu', '\\\\pi', '\\\\omega', '\\\\Omega', '\\\\alpha'
        ]
        
        for pattern in problematic_patterns:
            if pattern in text:
                correct_pattern = pattern.replace('\\\\', '\\')
                issues.append(f"Field '{field_name}' contains '{pattern}' - should be '{correct_pattern}'")
        
        # Check for bare mathematical expressions (should be in $ delimiters)
        # Look for patterns like "10Ω" or "90°" that should be "$10\\,\\Omega$" or "$90^\\circ$"
        # PHASE 2.5 FIX: Precision validation - Allow educational content, detect real LaTeX errors
        
        import re
        
        def is_educational_pattern(text_to_check):
            """Check if text contains legitimate educational patterns that should be allowed"""
            educational_patterns = {
                'chemical_formulas': r'\b[A-Z][a-z]?_?\d*\b',  # SiO_2, Si, etc.
                'mathematical_vars': r'\b[A-Z][A-Z]?_?[0-9]+\b',  # T0, V_T0, etc.
                'decimal_parts': r'\b0\d*',  # 05 in 0.05, etc.
                'calculation_values': r'\b[0-9]{3,5}\b',  # 673, 894, 779, 31156, 81156 (intermediate calculations)
                'unit_notation': r'\\text\{[^}]+\}',  # \text{V}, \text{A} (proper LaTeX)
                'latex_wrapped_content': r'\$[^$]*\$',  # Already in LaTeX delimiters
                'subscript_notation': r'_\d+',  # _2 in chemical formulas like SiO_2
                'chemical_interfaces': r'\b[A-Z][a-z]*-[A-Z][a-z]*\b',  # Si-SiO interface notation
                'variable_subscripts': r'\b[gmT]\d+\b',  # g_m0, T0, etc.
                'latex_commands': r'\\[a-zA-Z]+\{[^}]*\}',  # Proper LaTeX commands like \text{}, \times
            }
            
            for pattern_name, pattern in educational_patterns.items():
                if re.search(pattern, text_to_check):
                    return True
            return False
        
        def has_real_latex_syntax_errors(text_to_check):
            """Check for actual LaTeX syntax errors that should be flagged"""
            import re
            
            # Check for LaTeX syntax errors with simplified patterns
            latex_errors = []
            
            # 1. Check for text{} without backslash (but allow \text{})
            text_pattern = r'text\{[^}]+\}'
            if re.search(text_pattern, text_to_check):
                # Check if it's properly escaped
                escaped_text_pattern = r'\\text\{[^}]+\}'
                text_matches = re.findall(text_pattern, text_to_check)
                escaped_matches = re.findall(escaped_text_pattern, text_to_check)
                if len(text_matches) > len(escaped_matches):
                    latex_errors.append('missing_backslash_text')
            
            # 2. Check for times without backslash (but allow \times)
            if re.search(r'\btimes\b', text_to_check) and not re.search(r'\\times\b', text_to_check):
                latex_errors.append('missing_backslash_times')
            
            # 3. Check for unescaped % in math content
            percent_matches = re.findall(r'\d+%', text_to_check)
            escaped_percent_matches = re.findall(r'\d+\\%', text_to_check)
            if len(percent_matches) > len(escaped_percent_matches):
                latex_errors.append('unescaped_percent')
            
            # 4. Check for invalid mutext command
            if re.search(r'mutext\{[^}]+\}', text_to_check):
                latex_errors.append('invalid_mutext')
            
            # 5. Check for common math commands without backslash
            math_commands = ['frac', 'sqrt', 'alpha', 'beta', 'gamma', 'theta', 'lambda', 'sigma', 'omega', 'Omega']
            for cmd in math_commands:
                if re.search(rf'\b{cmd}\{{', text_to_check) and not re.search(rf'\\{cmd}\{{', text_to_check):
                    latex_errors.append(f'missing_backslash_{cmd}')
            
            if latex_errors:
                return True, latex_errors[0]  # Return first error found
            return False, None
        
        def is_within_latex_context(text, match_pos):
            """Check if a match is within LaTeX delimiters"""
            # Find all LaTeX blocks in the text
            latex_blocks = []
            for match in re.finditer(r'\$[^$]*\$', text):
                latex_blocks.append((match.start(), match.end()))
            
            # Check if match_pos is within any LaTeX block
            for start, end in latex_blocks:
                if start <= match_pos < end:
                    return True
            return False
        
        def extract_problematic_matches(text_to_check, pattern):
            """Extract matches that are NOT educational patterns and NOT within proper LaTeX"""
            problematic_matches = []
            
            for match in re.finditer(pattern, text_to_check):
                match_text = match.group()
                match_pos = match.start()
                
                # Skip if it's an educational pattern (Phase 2 preservation)
                if is_educational_pattern(match_text):
                    continue
                    
                # Skip if it's within proper LaTeX delimiters and not an error
                if is_within_latex_context(text_to_check, match_pos):
                    continue
                
                problematic_matches.append(match_text)
            
            return problematic_matches
        
        # PHASE 2.5: First check for real LaTeX syntax errors (restore error detection)
        has_syntax_error, error_type = has_real_latex_syntax_errors(text)
        if has_syntax_error:
            if error_type == 'missing_backslash_text':
                matches = re.findall(r'text\{[^}]+\}', text)
                escaped_matches = re.findall(r'\\text\{[^}]+\}', text)
                if len(matches) > len(escaped_matches):
                    issues.append(f"Field '{field_name}' has LaTeX syntax error: missing backslash - use \\text{{}} not text{{}}")
            elif error_type == 'missing_backslash_times':
                issues.append(f"Field '{field_name}' has LaTeX syntax error: missing backslash - use \\times not times")
            elif error_type == 'unescaped_percent':
                matches = re.findall(r'\d+%', text)
                issues.append(f"Field '{field_name}' has LaTeX syntax error: {matches} - use \\% in math mode")
            elif error_type == 'invalid_mutext':
                matches = re.findall(r'mutext\{[^}]+\}', text)
                issues.append(f"Field '{field_name}' has LaTeX syntax error: {matches} - use \\mu\\text{{}} not mutext{{}}")
            elif 'missing_backslash_' in error_type:
                cmd = error_type.replace('missing_backslash_', '')
                issues.append(f"Field '{field_name}' has LaTeX syntax error: missing backslash - use \\{cmd}{{}} not {cmd}{{}}")
        
        # Apply bare math validation with educational content awareness (Phase 2 preservation)
        bare_math_patterns = [
            (r'\d+Ω', 'Use ${}\\,\\Omega$ for ohms'),
            (r'\d+°', 'Use ${}^\\circ$ for degrees'),
            (r'\w\d+', 'Use ${}$ for variables with subscripts'),
            (r'\d+\^\d+', 'Use ${}$ for superscripts'),
        ]
        
        for pattern, message in bare_math_patterns:
            # PHASE 2.5: Only flag matches that are NOT educational patterns
            problematic_matches = extract_problematic_matches(text, pattern)
            
            if problematic_matches:
                issues.append(f"Field '{field_name}' may have bare math: {problematic_matches} - {message}")
        
        return issues
    def export_json(self, questions_data: Dict, format_type: str = "standard", 
                   filename_prefix: str = "q2json_questions") -> str:
        """
        Export validated questions in specified format
        
        Args:
            questions_data: Validated questions data
            format_type: Export format ("standard", "compact", "pretty")
            filename_prefix: Prefix for filename generation
            
        Returns:
            JSON string ready for download/export
        """
        if format_type == "compact":
            return json.dumps(questions_data, separators=(',', ':'), ensure_ascii=False)
        elif format_type == "pretty":
            return json.dumps(questions_data, indent=4, ensure_ascii=False)
        else:  # standard
            return json.dumps(questions_data, indent=2, ensure_ascii=False)
    
    def get_processing_summary(self) -> Dict:
        """
        Get summary of processing attempts and results
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'repair_attempts': len(self.repair_attempts),
            'last_repair_details': self.repair_attempts[-1] if self.repair_attempts else None,
            'validation_results': self.validation_results,
            'processing_log': self.processing_log
        }
    
    def _simple_preprocess(self, raw_text: str) -> str:
        """
        Simple preprocessing to fix most common issues
        """
        text = raw_text.strip()
        
        # 1. Extract from markdown blocks (simple approach)
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end > start:
                text = text[start:end].strip()
        
        # 2. Find JSON block (simple approach)
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace >= 0 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1]
        
        # 3. Basic fixes
        text = text.replace('"', '"').replace('"', '"')  # Smart quotes
        text = text.replace('\\_', '_')  # Remove unnecessary escape from underscores
    
        # 4. Remove comments (# lines) that break JSON
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove lines that start with # (comments)
            if not line.strip().startswith('#'):
                cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)

        # 5. Balance brackets FIRST (for arrays)
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        if open_brackets > close_brackets:
            text += ']' * (open_brackets - close_brackets)

        # 6. Balance braces SECOND (for objects)
        open_braces = text.count('{')
        close_braces = text.count('}')
        if open_braces > close_braces:
            text += '}' * (open_braces - close_braces)

        return text
    
    def _detect_mathematical_consistency(self, questions_data: Dict) -> Dict:
        """
        Phase 3: Mathematical consistency detection based on main_enhanced.py logic
        Detects contradictions like 0.776 vs 0.812 in Question 8
        """
        mathematical_results = {
            'total_checked': 0,
            'contradictions_found': 0,
            'contradictions': [],
            'numerical_questions': 0
        }
        
        questions = questions_data.get('questions', [])
        
        for i, question in enumerate(questions):
            if question.get('type') == 'numerical':
                mathematical_results['numerical_questions'] += 1
                mathematical_results['total_checked'] += 1
                
                # Extract declared answer
                try:
                    declared_answer = float(question.get('correct_answer', '0'))
                except (ValueError, TypeError):
                    continue
                
                # Check feedback for contradictory values
                feedback_text = question.get('feedback_correct', '')
                if feedback_text:
                    contradictory_values = self._extract_mathematical_values(
                        feedback_text, declared_answer
                    )
                    
                    for value, context in contradictory_values:
                        difference_percent = abs(value - declared_answer) / declared_answer * 100
                        
                        # Use 2% threshold for educational content sensitivity (from CLI)
                        if difference_percent > 2.0:
                            contradiction = {
                                'question_index': i + 1,
                                'question_title': question.get('title', f'Question {i+1}'),
                                'declared_answer': declared_answer,
                                'found_value': value,
                                'difference_percent': round(difference_percent, 1),
                                'severity': self._classify_mathematical_severity(difference_percent),
                                'context': context
                            }
                            
                            mathematical_results['contradictions'].append(contradiction)
                            mathematical_results['contradictions_found'] += 1
        
        return mathematical_results
    
    def _extract_mathematical_values(self, text: str, declared_value: float) -> List[Tuple[float, str]]:
        """
        Extract mathematical values using enhanced patterns from main_enhanced.py
        Based on patterns that successfully find 0.812 in Question 8
        """
        extracted_values = []
        
        # Enhanced patterns based on CLI success (from mathematical_consistency_detector_enhanced.py)
        final_answer_patterns = [
            # Approximation patterns (finds "approx 0.812")
            (r'[A-Z_]*\s*≈\s*(\d+\.\d+)', 'Approximation'),
            (r'[A-Z_]*\s*approx\s*(\d+\.\d+)', 'Approximation'),
            (r'approx\s*(\d+\.\d+)', 'Approximation'),
            
            # Unit patterns (finds "0.812,text{V}")
            (r'(\d+\.\d+),text\{[VvAa]\}', 'Value with units'),
            (r'(\d+\.\d+)\s*V[.\s]', 'Voltage value'),
            (r'(\d+\.\d+)\s*text\{V\}', 'LaTeX voltage'),
            
            # Calculation result patterns
            (r'[A-Z_]*\s*=\s*(\d+\.\d+)', 'Calculation result'),
            (r'get\s*[A-Z_]*\s*=\s*(\d+\.\d+)', 'Calculation gives'),
            (r'gives.*?(\d+\.\d+)', 'Calculation gives'),
            
            # Rounding patterns (finds calculation endpoints)
            (r'Rounding.*?(\d+\.\d+)', 'Rounding result'),
            (r'three decimal places.*?(\d+\.\d+)', 'Rounded value'),
            
            # Alternative calculation patterns
            (r'My calculation.*?(\d+\.\d+)', 'Alternative calculation'),
        ]
        
        # Basic constants to skip (from CLI logic)
        basic_constants = {0.5, 0.4, 1.0, 2.0, 3.0, 4.0, 5.0, 0.8, 0.9, 1.6, 1.7}
        
        for pattern, context_type in final_answer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match)
                    
                    # Skip if it's exactly the declared value
                    if abs(value - declared_value) < 0.001:
                        continue
                    
                    # Skip basic constants
                    if value in basic_constants:
                        continue
                    
                    # Skip very small values (likely intermediate calculations)
                    if value < 0.1:
                        continue
                    
                    # Get context around this value
                    context = self._get_mathematical_context(text, match, 50)
                    
                    extracted_values.append((value, f"{context_type}: {context}"))
                    
                except ValueError:
                    continue
        
        return extracted_values
    
    def _get_mathematical_context(self, text: str, value_str: str, context_length: int = 50) -> str:
        """Get context around a mathematical value for better understanding"""
        try:
            value_pos = text.find(value_str)
            if value_pos == -1:
                return "Context not found"
            
            start = max(0, value_pos - context_length)
            end = min(len(text), value_pos + len(value_str) + context_length)
            
            context = text[start:end].strip()
            
            # Clean up context for display
            context = re.sub(r'\s+', ' ', context)
            if len(context) > 100:
                context = context[:97] + "..."
            
            return context
        except:
            return "Context extraction failed"
    
    def _classify_mathematical_severity(self, difference_percent: float) -> str:
        """Classify mathematical contradiction severity (from CLI logic)"""
        if difference_percent <= 10.0:
            return "Minor"
        elif difference_percent <= 25.0:
            return "Major" 
        else:
            return "Severe"
    
    def _check_mathematical_consistency_single(self, question: Dict) -> List[str]:
        """
        Check mathematical consistency for a single question
        Returns list of mathematical issues found
        """
        issues = []
        
        # Only check numerical questions
        if question.get('type') != 'numerical':
            return issues
        
        try:
            declared_answer = float(question.get('correct_answer', '0'))
        except (ValueError, TypeError):
            return issues
        
        # Check feedback for contradictory values
        feedback_text = question.get('feedback_correct', '')
        if feedback_text:
            contradictory_values = self._extract_mathematical_values(
                feedback_text, declared_answer
            )
            
            for value, context in contradictory_values:
                difference_percent = abs(value - declared_answer) / declared_answer * 100
                
                # Use 2% threshold for educational content sensitivity
                if difference_percent > 2.0:
                    severity = self._classify_mathematical_severity(difference_percent)
                    issues.append(
                        f"Mathematical inconsistency: declared answer {declared_answer} "
                        f"vs found {value} ({difference_percent:.1f}% difference, {severity}) "
                        f"in {context[:50]}..."
                    )
        
        return issues