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
                # Apply LaTeX corrections to the parsed data
                questions_data, latex_corrections = self._apply_latex_corrections_to_data(questions_data)
                if latex_corrections:
                    messages.append(f"🔧 Applied {len(latex_corrections)} LaTeX corrections to content")
                
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
                # Apply LaTeX corrections to the parsed data
                questions_data, latex_corrections = self._apply_latex_corrections_to_data(questions_data)
                if latex_corrections:
                    messages.append(f"🔧 Applied {len(latex_corrections)} LaTeX corrections to content")
                
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
            'latex_issues': []
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
                'latex_issues': []
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
        bare_math_patterns = [
            (r'\d+Ω', 'Use ${}\\,\\Omega$ for ohms'),
            (r'\d+°', 'Use ${}^\\circ$ for degrees'),
            (r'\w\d+', 'Use ${}$ for variables with subscripts'),
            (r'\d+\^\d+', 'Use ${}$ for superscripts'),
        ]
        
        import re
        for pattern, message in bare_math_patterns:
            matches = re.findall(pattern, text)
            if matches:
                issues.append(f"Field '{field_name}' may have bare math: {matches} - {message}")
        
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
    
    def _latex_auto_correct(self, text: str) -> Tuple[str, List[str]]:
        """
        Auto-correct common LaTeX syntax errors in text content
        
        Args:
            text: Text content to correct
            
        Returns:
            Tuple of (corrected_text, list_of_corrections_made)
        """
        corrections_made = []
        original_text = text
        
        # Import regex for pattern matching
        import re
        
        # Priority 1: Comma-text patterns (CRITICAL MISSING PATTERN)
        comma_text_patterns = [
            (r'(\d+(?:\.\d+)?),text\{', r'\1\\,\\text{'),  # 0.5,text{ → 0.5\,\text{
            (r'(\d+),text\{', r'\1\\,\\text{'),            # 5,text{ → 5\,\text{
        ]
        
        for pattern, replacement in comma_text_patterns:
            if re.search(pattern, text):
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    corrections_made.append(f"Fixed comma-text spacing: '{pattern}' → '{replacement}'")
                    text = new_text
        
        # Priority 2: Unescaped Greek letters (CRITICAL MISSING PATTERN)
        greek_letter_patterns = [
            # Common Greek letters used in MOSFET/electronics
            (r'\b(?<!\\)gamma\b', r'\\gamma'),         # gamma → \gamma
            (r'(?<!\\)(\d*)phi_F\b', r'\1\\phi_F'),    # 2phi_F → 2\phi_F, phi_F → \phi_F (enhanced)
            (r'\b(?<!\\)phi\b', r'\\phi'),             # phi → \phi
            (r'\b(?<!\\)alpha\b', r'\\alpha'),         # alpha → \alpha
            (r'\b(?<!\\)beta\b', r'\\beta'),           # beta → \beta
            (r'\b(?<!\\)theta\b', r'\\theta'),         # theta → \theta
            (r'\b(?<!\\)lambda\b', r'\\lambda'),       # lambda → \lambda
            (r'\b(?<!\\)sigma\b', r'\\sigma'),         # sigma → \sigma
            (r'\b(?<!\\)delta\b', r'\\delta'),         # delta → \delta
            (r'\b(?<!\\)epsilon\b', r'\\epsilon'),     # epsilon → \epsilon
            (r'\b(?<!\\)omega\b', r'\\omega'),         # omega → \omega
            (r'\b(?<!\\)Omega\b', r'\\Omega'),         # Omega → \Omega
            (r'\b(?<!\\)tau\b', r'\\tau'),             # tau → \tau
            (r'\b(?<!\\)rho\b', r'\\rho'),             # rho → \rho
        ]
        
        for pattern, replacement in greek_letter_patterns:
            if re.search(pattern, text):
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    corrections_made.append(f"Escaped Greek letter: '{pattern}' → '{replacement}'")
                    text = new_text
        
        # Priority 3: Unescaped mathematical operators (CRITICAL MISSING PATTERN)
        math_operator_patterns = [
            (r'\b(?<!\\)sqrt\{', r'\\sqrt{'),          # sqrt{ → \sqrt{
            (r'\b(?<!\\)times\b', r'\\times'),         # times → \times
            (r'\b(?<!\\)approx\b', r'\\approx'),       # approx → \approx
            (r'\b(?<!\\)frac\{', r'\\frac{'),          # frac{ → \frac{
            (r'\b(?<!\\)sum\b', r'\\sum'),             # sum → \sum
            (r'\b(?<!\\)int\b', r'\\int'),             # int → \int
            (r'\b(?<!\\)log\b', r'\\log'),             # log → \log
            (r'\b(?<!\\)sin\b', r'\\sin'),             # sin → \sin
            (r'\b(?<!\\)cos\b', r'\\cos'),             # cos → \cos
            (r'\b(?<!\\)tan\b', r'\\tan'),             # tan → \tan
            (r'\b(?<!\\)exp\b', r'\\exp'),             # exp → \exp
        ]
        
        for pattern, replacement in math_operator_patterns:
            if re.search(pattern, text):
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    corrections_made.append(f"Escaped math operator: '{pattern}' → '{replacement}'")
                    text = new_text
        
        # Priority 4: mutext pattern corrections (original corner case)
        mutext_patterns = [
            (r'(\d+)\s*mutext\{', r'\1\\,\\mu\\text{'), # 5 mutext{ → 5\,\mu\text{ (with or without space)
            (r'\bmutext\{', r'\\mu\\text{'),           # mutext{ → \mu\text{
            (r'\\mutext\{', r'\\mu\\text{'),          # \mutext{ → \mu\text{
        ]
        
        for pattern, replacement in mutext_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                if new_text != text:
                    corrections_made.append(f"Corrected mutext pattern: '{pattern}' → '{replacement}'")
                    text = new_text
        
        # Priority 5: Other common unit formatting errors
        unit_patterns = [
            (r'(\d+)\s*ohmtext\{', r'\1\\,\\Omega\\text{'),     # 5 ohmtext{ → 5\,\Omega\text{ (with or without space)
            (r'(\d+)\s*degreetext\{', r'\1^\\circ\\text{'),     # 5 degreetext{ → 5^\circ\text{ (with or without space)
            (r'\bohmtext\{', r'\\Omega\\text{'),       # ohmtext{ → \Omega\text{
            (r'\\ohmtext\{', r'\\Omega\\text{'),       # \ohmtext{ → \Omega\text{
            (r'\bdegreetext\{', r'^\\circ\\text{'),    # degreetext{ → ^\circ\text{
            (r'\\degreetext\{', r'^\\circ\\text{'),    # \degreetext{ → ^\circ\text{
        ]
        
        for pattern, replacement in unit_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                if new_text != text:
                    corrections_made.append(f"Corrected unit pattern: '{pattern}' → '{replacement}'")
                    text = new_text
        
        # Priority 6: Double backslash corrections (common LLM error)
        double_backslash_patterns = [
            (r'\\\\mu\b', r'\\mu'),           # \\mu → \mu
            (r'\\\\Omega\b', r'\\Omega'),     # \\Omega → \Omega
            (r'\\\\text\{', r'\\text{'),      # \\text{ → \text{
            (r'\\\\frac\{', r'\\frac{'),      # \\frac{ → \frac{
            (r'\\\\sqrt\{', r'\\sqrt{'),      # \\sqrt{ → \sqrt{
            (r'\\\\times\b', r'\\times'),     # \\times → \times
            (r'\\\\circ\b', r'\\circ'),       # \\circ → \circ
            (r'\\\\pi\b', r'\\pi'),           # \\pi → \pi
            (r'\\\\alpha\b', r'\\alpha'),     # \\alpha → \alpha
            (r'\\\\beta\b', r'\\beta'),       # \\beta → \beta
            (r'\\\\gamma\b', r'\\gamma'),     # \\gamma → \gamma
            (r'\\\\theta\b', r'\\theta'),     # \\theta → \theta
            (r'\\\\lambda\b', r'\\lambda'),   # \\lambda → \lambda
            (r'\\\\sigma\b', r'\\sigma'),     # \\sigma → \sigma
            (r'\\\\phi\b', r'\\phi'),         # \\phi → \phi
        ]
        
        for pattern, replacement in double_backslash_patterns:
            if re.search(pattern, text):
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    corrections_made.append(f"Fixed double backslash: '{pattern}' → '{replacement}'")
                    text = new_text
        
        # Priority 7: Missing math delimiters for common Unicode characters
        unicode_math_patterns = [
            (r'(?<!\$)\b(\d+)\s*°(?!\$)', r'$\1^\\circ$'),    # 5° → $5^\circ$
            (r'(?<!\$)\b(\d+)\s*Ω(?!\$)', r'$\1\\,\\Omega$'), # 5Ω → $5\,\Omega$
            (r'(?<!\$)\b(\d+)\s*μ(?!\$)', r'$\1\\,\\mu$'),    # 5μ → $5\,\mu$
            (r'(?<!\$)\b(\d+)\s*π(?!\$)', r'$\1\\pi$'),       # 5π → $5\pi$
            (r'(?<!\$)±(?!\$)', r'$\\pm$'),                   # ± → $\pm$
            (r'(?<!\$)≤(?!\$)', r'$\\leq$'),                  # ≤ → $\leq$
            (r'(?<!\$)≥(?!\$)', r'$\\geq$'),                  # ≥ → $\geq$
            (r'(?<!\$)∞(?!\$)', r'$\\infty$'),                # ∞ → $\infty$
        ]
        
        for pattern, replacement in unicode_math_patterns:
            if re.search(pattern, text):
                new_text = re.sub(pattern, replacement, text)
                if new_text != text:
                    corrections_made.append(f"Added math delimiters: '{pattern}' → '{replacement}'")
                    text = new_text
        
        return text, corrections_made
    
    def _apply_latex_corrections_to_data(self, questions_data: Dict) -> Tuple[Dict, List[str]]:
        """
        Apply LaTeX corrections to parsed question data
        
        Args:
            questions_data: Parsed questions dictionary
            
        Returns:
            Tuple of (corrected_data, list_of_corrections_made)
        """
        all_corrections = []
        
        if 'questions' not in questions_data:
            return questions_data, all_corrections
        
        for i, question in enumerate(questions_data['questions']):
            question_corrections = []
            
            # Fields to correct
            text_fields = ['title', 'question_text', 'feedback_correct', 'feedback_incorrect']
            
            for field in text_fields:
                if field in question and isinstance(question[field], str):
                    corrected_text, corrections = self._latex_auto_correct(question[field])
                    if corrections:
                        question[field] = corrected_text
                        question_corrections.extend(corrections)
            
            # Handle choices array
            if 'choices' in question and isinstance(question['choices'], list):
                for j, choice in enumerate(question['choices']):
                    if isinstance(choice, str):
                        corrected_choice, corrections = self._latex_auto_correct(choice)
                        if corrections:
                            question['choices'][j] = corrected_choice
                            question_corrections.extend(corrections)
            
            # Handle correct_answer if it's a string
            if 'correct_answer' in question and isinstance(question['correct_answer'], str):
                corrected_answer, corrections = self._latex_auto_correct(question['correct_answer'])
                if corrections:
                    question['correct_answer'] = corrected_answer
                    question_corrections.extend(corrections)
            
            if question_corrections:
                all_corrections.append(f"Question {i+1}: {len(question_corrections)} LaTeX corrections")
        
        return questions_data, all_corrections