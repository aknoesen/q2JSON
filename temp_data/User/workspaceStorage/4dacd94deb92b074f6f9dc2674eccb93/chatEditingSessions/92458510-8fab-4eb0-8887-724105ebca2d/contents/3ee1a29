# Q2JSON Validation Manager Component
"""
Q2JSONValidationManager - Comprehensive validation and flagging system

Extracted and enhanced from Q2LMS codebase for Q2JSON Stage 4 integration.
Provides comprehensive question validation, mathematical content checking,
QTI compliance verification, and automated flagging system.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import math
import html
from dataclasses import dataclass

try:
    from .latex_processor import Q2JSONLaTeXProcessor, MathValidationManager
except ImportError:
    from latex_processor import Q2JSONLaTeXProcessor, MathValidationManager


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'structure', 'content', 'math', 'qti', 'accessibility'
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ValidationResult:
    """Represents validation results for a question."""
    is_valid: bool
    issues: List[ValidationIssue]
    score: float  # 0-100 quality score
    flags: List[str]  # Auto-generated flags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'message': issue.message,
                    'field': issue.field,
                    'suggestion': issue.suggestion,
                    'auto_fixable': issue.auto_fixable
                }
                for issue in self.issues
            ],
            'score': self.score,
            'flags': self.flags
        }


class Q2JSONValidationManager:
    """
    Advanced validation manager extracted from Q2LMS with enhanced QTI compliance.
    
    Features:
    - Comprehensive question structure validation
    - Mathematical content validation with LaTeX support
    - QTI compliance checking
    - Accessibility validation
    - Auto-flagging system for quality assurance
    - Batch validation capabilities
    - Custom validation rules
    """
    
    def __init__(self, 
                 latex_processor: Optional[Q2JSONLaTeXProcessor] = None,
                 custom_rules: Optional[Dict[str, Any]] = None):
        """Initialize the validation manager."""
        self.latex_processor = latex_processor or Q2JSONLaTeXProcessor()
        self.math_validator = MathValidationManager()
        self.custom_rules = custom_rules or {}
        
        # Define supported question types
        self.supported_types = {
            'multiple_choice', 'true_false', 'essay', 'short_answer',
            'numerical', 'matching', 'fill_blank', 'ordering', 'hotspot',
            'drag_drop', 'graphical', 'upload'
        }
        
        # Define required fields per question type
        self.required_fields = {
            'multiple_choice': ['question_text', 'options', 'correct_answers'],
            'true_false': ['question_text', 'correct_answer'],
            'essay': ['question_text'],
            'short_answer': ['question_text', 'correct_answers'],
            'numerical': ['question_text', 'correct_answer'],
            'matching': ['question_text', 'left_items', 'right_items', 'correct_matches'],
            'fill_blank': ['question_text', 'blanks'],
            'ordering': ['question_text', 'items', 'correct_order']
        }
        
        # Define validation weights for scoring
        self.validation_weights = {
            'structure': 30,
            'content': 25,
            'math': 20,
            'qti': 15,
            'accessibility': 10
        }
        
        # Initialize validators
        self.validators = {
            'structure': self._validate_structure,
            'content': self._validate_content,
            'math': self._validate_math,
            'qti': self._validate_qti_compliance,
            'accessibility': self._validate_accessibility
        }
        
        # Auto-flagging rules
        self.flag_rules = {
            'needs_review': self._flag_needs_review,
            'math_heavy': self._flag_math_heavy,
            'accessibility_issues': self._flag_accessibility_issues,
            'qti_non_compliant': self._flag_qti_non_compliant,
            'difficult_content': self._flag_difficult_content,
            'incomplete': self._flag_incomplete
        }
    
    def validate_question(self, question: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single question comprehensively.
        
        Args:
            question: Question data to validate
            
        Returns:
            ValidationResult with all issues and flags
        """
        all_issues = []
        category_scores = {}
        
        # Run all validators
        for category, validator in self.validators.items():
            try:
                issues = validator(question)
                all_issues.extend(issues)
                
                # Calculate category score
                error_count = sum(1 for issue in issues if issue.severity == 'error')
                warning_count = sum(1 for issue in issues if issue.severity == 'warning')
                
                # Score: 100 - (errors * 20) - (warnings * 5)
                category_score = max(0, 100 - (error_count * 20) - (warning_count * 5))
                category_scores[category] = category_score
                
            except Exception as e:
                # If validator fails, add error and score 0
                all_issues.append(ValidationIssue(
                    severity='error',
                    category='system',
                    message=f"Validator error in {category}: {str(e)}",
                    auto_fixable=False
                ))
                category_scores[category] = 0
        
        # Calculate overall score
        overall_score = sum(
            score * (self.validation_weights.get(category, 0) / 100)
            for category, score in category_scores.items()
        )
        
        # Generate flags
        flags = []
        for flag_name, flag_rule in self.flag_rules.items():
            try:
                if flag_rule(question, all_issues):
                    flags.append(flag_name)
            except Exception:
                pass  # Ignore flag rule errors
        
        # Determine overall validity
        has_errors = any(issue.severity == 'error' for issue in all_issues)
        is_valid = not has_errors
        
        return ValidationResult(
            is_valid=is_valid,
            issues=all_issues,
            score=overall_score,
            flags=flags
        )
    
    def validate_question_set(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a set of questions and provide summary statistics.
        
        Args:
            questions: List of questions to validate
            
        Returns:
            Dictionary with validation summary and individual results
        """
        individual_results = []
        total_issues = 0
        total_score = 0
        flag_counts = {}
        category_issues = {}
        
        for i, question in enumerate(questions):
            result = self.validate_question(question)
            individual_results.append({
                'question_index': i,
                'result': result.to_dict()
            })
            
            total_issues += len(result.issues)
            total_score += result.score
            
            # Count flags
            for flag in result.flags:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
            
            # Count issues by category
            for issue in result.issues:
                category = issue.category
                category_issues[category] = category_issues.get(category, 0) + 1
        
        # Calculate summary statistics
        avg_score = total_score / len(questions) if questions else 0
        valid_count = sum(1 for result in individual_results if result['result']['is_valid'])
        invalid_count = len(questions) - valid_count
        
        return {
            'summary': {
                'total_questions': len(questions),
                'valid_questions': valid_count,
                'invalid_questions': invalid_count,
                'total_issues': total_issues,
                'average_score': avg_score,
                'flag_counts': flag_counts,
                'category_issues': category_issues
            },
            'individual_results': individual_results,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _validate_structure(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate question structure and required fields."""
        issues = []
        
        # Check if question is a dictionary
        if not isinstance(question, dict):
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Question must be a dictionary/object',
                field='root',
                suggestion='Ensure question data is properly formatted as JSON object'
            ))
            return issues
        
        # Check question type
        question_type = question.get('type', 'multiple_choice')
        if question_type not in self.supported_types:
            issues.append(ValidationIssue(
                severity='warning',
                category='structure',
                message=f'Unsupported question type: {question_type}',
                field='type',
                suggestion=f'Use one of: {", ".join(self.supported_types)}'
            ))
        
        # Check required fields
        required = self.required_fields.get(question_type, ['question_text'])
        for field in required:
            if field not in question:
                issues.append(ValidationIssue(
                    severity='error',
                    category='structure',
                    message=f'Missing required field: {field}',
                    field=field,
                    suggestion=f'Add {field} field for {question_type} questions',
                    auto_fixable=True
                ))
            elif not question[field]:
                issues.append(ValidationIssue(
                    severity='error',
                    category='structure',
                    message=f'Required field is empty: {field}',
                    field=field,
                    suggestion=f'Provide content for {field}',
                    auto_fixable=False
                ))
        
        # Type-specific validation
        if question_type == 'multiple_choice':
            issues.extend(self._validate_multiple_choice_structure(question))
        elif question_type == 'numerical':
            issues.extend(self._validate_numerical_structure(question))
        elif question_type == 'matching':
            issues.extend(self._validate_matching_structure(question))
        elif question_type == 'fill_blank':
            issues.extend(self._validate_fill_blank_structure(question))
        elif question_type == 'ordering':
            issues.extend(self._validate_ordering_structure(question))
        
        # Check optional but recommended fields
        recommended_fields = ['title', 'points', 'difficulty', 'category']
        for field in recommended_fields:
            if field not in question or not question[field]:
                issues.append(ValidationIssue(
                    severity='info',
                    category='structure',
                    message=f'Recommended field missing: {field}',
                    field=field,
                    suggestion=f'Consider adding {field} for better organization',
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_content(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate question content quality and completeness."""
        issues = []
        
        # Check question text quality
        question_text = question.get('question_text', '')
        if question_text:
            # Length checks
            if len(question_text.strip()) < 10:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='content',
                    message='Question text is very short',
                    field='question_text',
                    suggestion='Consider providing more detailed question text'
                ))
            elif len(question_text.strip()) > 2000:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='content',
                    message='Question text is very long',
                    field='question_text',
                    suggestion='Consider breaking into multiple questions or using more concise language'
                ))
            
            # Check for placeholder text
            placeholders = ['lorem ipsum', 'sample text', 'placeholder', 'todo', 'fix me']
            text_lower = question_text.lower()
            for placeholder in placeholders:
                if placeholder in text_lower:
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='content',
                        message=f'Placeholder text detected: {placeholder}',
                        field='question_text',
                        suggestion='Replace placeholder text with actual question content'
                    ))
            
            # Check for unclear language
            unclear_phrases = ['this', 'that', 'the above', 'the following', 'it']
            for phrase in unclear_phrases:
                if f' {phrase} ' in text_lower and text_lower.count(phrase) > 2:
                    issues.append(ValidationIssue(
                        severity='info',
                        category='content',
                        message=f'Potentially unclear reference: "{phrase}" used frequently',
                        field='question_text',
                        suggestion='Consider using more specific references'
                    ))
        
        # Check options quality (for MCQ)
        if question.get('type') == 'multiple_choice':
            options = question.get('options', [])
            if options:
                # Check for similar options
                option_similarities = self._check_option_similarity(options)
                for sim in option_similarities:
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='content',
                        message=f'Options {sim["indices"]} are very similar',
                        field='options',
                        suggestion='Ensure options are distinct and meaningful'
                    ))
                
                # Check option lengths
                option_lengths = [len(str(opt)) for opt in options]
                if max(option_lengths) > 3 * min(option_lengths):
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='content',
                        message='Option lengths vary significantly',
                        field='options',
                        suggestion='Try to keep option lengths relatively consistent'
                    ))
        
        # Check for bias or sensitive content
        sensitive_terms = self._check_sensitive_content(question_text)
        for term in sensitive_terms:
            issues.append(ValidationIssue(
                severity='warning',
                category='content',
                message=f'Potentially sensitive content detected: {term}',
                field='question_text',
                suggestion='Review content for potential bias or sensitivity issues'
            ))
        
        return issues
    
    def _validate_math(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate mathematical content in question."""
        issues = []
        
        # Check all text fields for math content
        text_fields = ['question_text', 'title', 'general_feedback']
        for field in text_fields:
            if field in question and question[field]:
                math_issues = self.math_validator.validate_math_content(question[field])
                for math_issue in math_issues:
                    issues.append(ValidationIssue(
                        severity=math_issue['severity'],
                        category='math',
                        message=f'{field}: {math_issue["message"]}',
                        field=field,
                        suggestion=math_issue.get('suggestion'),
                        auto_fixable=math_issue.get('auto_fixable', False)
                    ))
        
        # Check options for math content
        if 'options' in question:
            for i, option in enumerate(question['options']):
                if option:
                    math_issues = self.math_validator.validate_math_content(str(option))
                    for math_issue in math_issues:
                        issues.append(ValidationIssue(
                            severity=math_issue['severity'],
                            category='math',
                            message=f'Option {i + 1}: {math_issue["message"]}',
                            field=f'options[{i}]',
                            suggestion=math_issue.get('suggestion', ''),
                            auto_fixable=math_issue.get('auto_fixable', False)
                        ))
        
        # Numerical question specific validation
        if question.get('type') == 'numerical':
            issues.extend(self._validate_numerical_math(question))
        
        return issues
    
    def _validate_qti_compliance(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate QTI compliance."""
        issues = []
        
        # Check QTI-specific requirements
        question_type = question.get('type', 'multiple_choice')
        
        # QTI identifier requirements
        if 'identifier' in question:
            identifier = question['identifier']
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', identifier):
                issues.append(ValidationIssue(
                    severity='error',
                    category='qti',
                    message='QTI identifier must start with letter and contain only letters, numbers, hyphens, and underscores',
                    field='identifier',
                    suggestion='Use a valid QTI identifier format'
                ))
        
        # Response processing validation
        if question_type == 'multiple_choice':
            correct_answers = question.get('correct_answers', [])
            if not correct_answers:
                issues.append(ValidationIssue(
                    severity='error',
                    category='qti',
                    message='Multiple choice questions must have at least one correct answer',
                    field='correct_answers',
                    suggestion='Specify correct answer indices'
                ))
            
            # Check if correct answers are valid indices
            options = question.get('options', [])
            for answer in correct_answers:
                if isinstance(answer, int) and (answer < 0 or answer >= len(options)):
                    issues.append(ValidationIssue(
                        severity='error',
                        category='qti',
                        message=f'Correct answer index {answer} is out of range',
                        field='correct_answers',
                        suggestion=f'Use indices 0-{len(options) - 1}'
                    ))
        
        # Media file validation
        media_fields = self._extract_media_references(question)
        for field, media_refs in media_fields.items():
            for media_ref in media_refs:
                if not self._validate_media_reference(media_ref):
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='qti',
                        message=f'Invalid media reference in {field}: {media_ref}',
                        field=field,
                        suggestion='Ensure media files exist and are accessible'
                    ))
        
        # Check for unsupported HTML tags
        html_issues = self._validate_html_content(question)
        issues.extend(html_issues)
        
        return issues
    
    def _validate_accessibility(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate accessibility requirements."""
        issues = []
        
        # Check for alt text on images
        text_content = self._get_all_text_content(question)
        img_tags = re.findall(r'<img[^>]*>', text_content, re.IGNORECASE)
        
        for img_tag in img_tags:
            if 'alt=' not in img_tag.lower():
                issues.append(ValidationIssue(
                    severity='warning',
                    category='accessibility',
                    message='Image found without alt text',
                    suggestion='Add alt text to images for screen readers',
                    auto_fixable=True
                ))
        
        # Check color contrast (basic check for color-only indicators)
        color_indicators = ['red', 'green', 'blue', 'yellow', 'color:', 'background-color:']
        for indicator in color_indicators:
            if indicator in text_content.lower():
                issues.append(ValidationIssue(
                    severity='info',
                    category='accessibility',
                    message='Color-based formatting detected',
                    suggestion='Ensure content is not solely dependent on color for meaning'
                ))
                break
        
        # Check for proper heading structure
        headings = re.findall(r'<h([1-6])[^>]*>', text_content, re.IGNORECASE)
        if headings:
            heading_levels = [int(h) for h in headings]
            if heading_levels and min(heading_levels) > 2:
                issues.append(ValidationIssue(
                    severity='info',
                    category='accessibility',
                    message='Consider using proper heading hierarchy starting from h1 or h2',
                    suggestion='Use sequential heading levels for better screen reader navigation'
                ))
        
        # Check for table headers
        table_tags = re.findall(r'<table[^>]*>.*?</table>', text_content, re.IGNORECASE | re.DOTALL)
        for table in table_tags:
            if '<th' not in table.lower() and '<thead' not in table.lower():
                issues.append(ValidationIssue(
                    severity='warning',
                    category='accessibility',
                    message='Table found without proper headers',
                    suggestion='Add table headers (th elements) for accessibility'
                ))
        
        # Check text complexity (basic readability)
        question_text = question.get('question_text', '')
        if question_text:
            complexity_score = self._calculate_text_complexity(question_text)
            if complexity_score > 15:  # Rough threshold
                issues.append(ValidationIssue(
                    severity='info',
                    category='accessibility',
                    message='Question text may be complex for some readers',
                    suggestion='Consider simplifying language or providing additional context'
                ))
        
        return issues
    
    def _validate_multiple_choice_structure(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate multiple choice specific structure."""
        issues = []
        
        options = question.get('options', [])
        correct_answers = question.get('correct_answers', [])
        
        # Check minimum options
        if len(options) < 2:
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Multiple choice questions need at least 2 options',
                field='options',
                suggestion='Add more answer options'
            ))
        
        # Check maximum options
        if len(options) > 10:
            issues.append(ValidationIssue(
                severity='warning',
                category='structure',
                message='Too many options may be overwhelming',
                field='options',
                suggestion='Consider reducing to 4-6 options'
            ))
        
        # Check correct answers format
        if not isinstance(correct_answers, list):
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='correct_answers must be a list',
                field='correct_answers',
                suggestion='Format correct_answers as [0, 1, ...] for option indices',
                auto_fixable=True
            ))
        
        return issues
    
    def _validate_numerical_structure(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate numerical question structure."""
        issues = []
        
        correct_answer = question.get('correct_answer')
        
        # Check if correct answer is numeric
        try:
            float(correct_answer)
        except (TypeError, ValueError):
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Numerical question must have numeric correct_answer',
                field='correct_answer',
                suggestion='Provide a valid number for correct_answer'
            ))
        
        # Check tolerance
        tolerance = question.get('tolerance', 0)
        try:
            tolerance_val = float(tolerance)
            if tolerance_val < 0:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='structure',
                    message='Tolerance should not be negative',
                    field='tolerance',
                    suggestion='Use positive tolerance value or 0 for exact match'
                ))
        except (TypeError, ValueError):
            issues.append(ValidationIssue(
                severity='warning',
                category='structure',
                message='Tolerance should be numeric',
                field='tolerance',
                suggestion='Provide numeric tolerance value'
            ))
        
        return issues
    
    def _validate_matching_structure(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate matching question structure."""
        issues = []
        
        left_items = question.get('left_items', [])
        right_items = question.get('right_items', [])
        correct_matches = question.get('correct_matches', {})
        
        # Check item counts
        if len(left_items) < 2:
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Matching questions need at least 2 left items',
                field='left_items',
                suggestion='Add more items to match'
            ))
        
        if len(right_items) < 2:
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Matching questions need at least 2 right items',
                field='right_items',
                suggestion='Add more items to match'
            ))
        
        # Check correct matches format
        if not isinstance(correct_matches, dict):
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='correct_matches must be a dictionary',
                field='correct_matches',
                suggestion='Format as {"0": 1, "1": 0, ...} mapping left to right indices'
            ))
        
        return issues
    
    def _validate_fill_blank_structure(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate fill-in-the-blank structure."""
        issues = []
        
        question_text = question.get('question_text', '')
        blanks = question.get('blanks', [])
        
        # Count blank placeholders
        blank_count = question_text.count('{{blank}}') + question_text.count('_____')
        
        if blank_count == 0:
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='Fill-in-blank question needs blank placeholders in question text',
                field='question_text',
                suggestion='Use {{blank}} or _____ to indicate blanks'
            ))
        
        if len(blanks) != blank_count:
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message=f'Mismatch: {blank_count} blanks in text but {len(blanks)} blank definitions',
                field='blanks',
                suggestion='Ensure each blank placeholder has a corresponding definition'
            ))
        
        return issues
    
    def _validate_ordering_structure(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate ordering question structure."""
        issues = []
        
        items = question.get('items', [])
        correct_order = question.get('correct_order', [])
        
        if len(items) < 3:
            issues.append(ValidationIssue(
                severity='warning',
                category='structure',
                message='Ordering questions typically need at least 3 items',
                field='items',
                suggestion='Add more items to make ordering meaningful'
            ))
        
        if len(correct_order) != len(items):
            issues.append(ValidationIssue(
                severity='error',
                category='structure',
                message='correct_order length must match items length',
                field='correct_order',
                suggestion='Provide ordering for all items'
            ))
        
        return issues
    
    def _validate_numerical_math(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate mathematical aspects of numerical questions."""
        issues = []
        
        correct_answer = question.get('correct_answer')
        tolerance = question.get('tolerance', 0)
        
        try:
            answer_val = float(correct_answer)
            tolerance_val = float(tolerance)
            
            # Check for reasonable values
            if abs(answer_val) > 1e10:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='math',
                    message='Very large numerical answer may cause precision issues',
                    field='correct_answer',
                    suggestion='Consider using scientific notation or scaling units'
                ))
            
            if tolerance_val > abs(answer_val) * 0.5:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='math',
                    message='Tolerance is very large relative to answer',
                    field='tolerance',
                    suggestion='Review tolerance value for appropriateness'
                ))
            
        except (TypeError, ValueError):
            pass  # Already caught in structure validation
        
        return issues
    
    def _check_option_similarity(self, options: List[str]) -> List[Dict[str, Any]]:
        """Check for similar options in multiple choice questions."""
        similarities = []
        
        for i, opt1 in enumerate(options):
            for j, opt2 in enumerate(options[i + 1:], i + 1):
                similarity = self._calculate_text_similarity(str(opt1), str(opt2))
                if similarity > 0.8:  # 80% similarity threshold
                    similarities.append({
                        'indices': [i, j],
                        'similarity': similarity
                    })
        
        return similarities
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple implementation)."""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _check_sensitive_content(self, text: str) -> List[str]:
        """Check for potentially sensitive content."""
        # Basic list of potentially sensitive terms
        sensitive_patterns = [
            r'\b(he|she)\s+is\s+(stupid|dumb|ugly)',
            r'\b(men|women)\s+are\s+(better|worse)',
            r'\b(race|gender|religion)\s+based',
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text_lower):
                found_terms.append(pattern)
        
        return found_terms
    
    def _extract_media_references(self, question: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract media file references from question."""
        media_refs = {}
        
        text_content = self._get_all_text_content(question)
        
        # Find image references
        img_matches = re.findall(r'src=["\']([^"\']+)["\']', text_content, re.IGNORECASE)
        if img_matches:
            media_refs['images'] = img_matches
        
        # Find video references
        video_matches = re.findall(r'<video[^>]+src=["\']([^"\']+)["\']', text_content, re.IGNORECASE)
        if video_matches:
            media_refs['videos'] = video_matches
        
        # Find audio references
        audio_matches = re.findall(r'<audio[^>]+src=["\']([^"\']+)["\']', text_content, re.IGNORECASE)
        if audio_matches:
            media_refs['audio'] = audio_matches
        
        return media_refs
    
    def _validate_media_reference(self, media_ref: str) -> bool:
        """Validate media reference (basic check)."""
        # Basic validation - check if it looks like a valid URL or file path
        if media_ref.startswith(('http://', 'https://', 'data:', '/')):
            return True
        
        # Check if it has a valid file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.mp3', '.wav', '.pdf']
        return any(media_ref.lower().endswith(ext) for ext in valid_extensions)
    
    def _validate_html_content(self, question: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate HTML content for QTI compliance."""
        issues = []
        
        text_content = self._get_all_text_content(question)
        
        # Check for potentially problematic HTML tags
        problematic_tags = ['script', 'iframe', 'object', 'embed', 'form']
        for tag in problematic_tags:
            if f'<{tag}' in text_content.lower():
                issues.append(ValidationIssue(
                    severity='error',
                    category='qti',
                    message=f'Potentially unsafe HTML tag: {tag}',
                    suggestion=f'Remove or replace {tag} tags for QTI compliance'
                ))
        
        # Check for unclosed tags (basic check)
        open_tags = re.findall(r'<(\w+)', text_content)
        close_tags = re.findall(r'</(\w+)', text_content)
        
        for tag in open_tags:
            if tag.lower() not in ['img', 'br', 'hr', 'input', 'meta', 'link']:  # Self-closing tags
                if open_tags.count(tag) > close_tags.count(tag):
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='qti',
                        message=f'Potentially unclosed HTML tag: {tag}',
                        suggestion='Ensure all HTML tags are properly closed'
                    ))
        
        return issues
    
    def _get_all_text_content(self, question: Dict[str, Any]) -> str:
        """Get all text content from question for analysis."""
        text_parts = []
        
        # Text fields
        text_fields = ['question_text', 'title', 'general_feedback']
        for field in text_fields:
            if field in question and question[field]:
                text_parts.append(str(question[field]))
        
        # Options
        if 'options' in question:
            for option in question['options']:
                if option:
                    text_parts.append(str(option))
        
        # Other list fields
        list_fields = ['left_items', 'right_items', 'items']
        for field in list_fields:
            if field in question and isinstance(question[field], list):
                for item in question[field]:
                    if item:
                        text_parts.append(str(item))
        
        return ' '.join(text_parts)
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score (simple implementation)."""
        if not text:
            return 0
        
        # Simple metrics
        sentences = text.count('.') + text.count('!') + text.count('?')
        if sentences == 0:
            sentences = 1
        
        words = len(text.split())
        if words == 0:
            return 0
        
        # Average words per sentence
        words_per_sentence = words / sentences
        
        # Average syllables per word (approximation)
        vowels = sum(1 for char in text.lower() if char in 'aeiou')
        syllables_per_word = max(1, vowels / words)
        
        # Simple complexity score
        complexity = (words_per_sentence * 0.39) + (syllables_per_word * 11.8) - 15.59
        
        return max(0, complexity)
    
    # Flag rules
    def _flag_needs_review(self, question: Dict[str, Any], issues: List[ValidationIssue]) -> bool:
        """Flag if question needs manual review."""
        return any(issue.severity == 'error' for issue in issues)
    
    def _flag_math_heavy(self, question: Dict[str, Any], issues: List[ValidationIssue]) -> bool:
        """Flag if question is math-heavy."""
        text_content = self._get_all_text_content(question)
        math_indicators = ['$', '\\', 'equation', 'formula', 'calculate', 'solve']
        return sum(1 for indicator in math_indicators if indicator in text_content.lower()) >= 3
    
    def _flag_accessibility_issues(self, question: Dict[str, Any], issues: List[ValidationIssue]) -> bool:
        """Flag if question has accessibility issues."""
        return any(issue.category == 'accessibility' and issue.severity in ['error', 'warning'] 
                  for issue in issues)
    
    def _flag_qti_non_compliant(self, question: Dict[str, Any], issues: List[ValidationIssue]) -> bool:
        """Flag if question is not QTI compliant."""
        return any(issue.category == 'qti' and issue.severity == 'error' for issue in issues)
    
    def _flag_difficult_content(self, question: Dict[str, Any], issues: List[ValidationIssue]) -> bool:
        """Flag if content appears difficult."""
        question_text = question.get('question_text', '')
        complexity = self._calculate_text_complexity(question_text)
        return complexity > 12 or question.get('difficulty', '').lower() == 'hard'
    
    def _flag_incomplete(self, question: Dict[str, Any], issues: List[ValidationIssue]) -> bool:
        """Flag if question appears incomplete."""
        structural_errors = [issue for issue in issues 
                           if issue.category == 'structure' and issue.severity == 'error']
        return len(structural_errors) > 0
    
    def get_auto_fix_suggestions(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get automatic fix suggestions for a question."""
        validation_result = self.validate_question(question)
        suggestions = []
        
        for issue in validation_result.issues:
            if issue.auto_fixable:
                suggestions.append({
                    'field': issue.field,
                    'issue': issue.message,
                    'suggestion': issue.suggestion,
                    'severity': issue.severity
                })
        
        return suggestions
    
    def apply_auto_fixes(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic fixes to a question."""
        fixed_question = question.copy()
        
        # Add missing recommended fields with defaults
        if 'points' not in fixed_question:
            fixed_question['points'] = 1.0
        
        if 'difficulty' not in fixed_question:
            fixed_question['difficulty'] = 'Medium'
        
        if 'category' not in fixed_question:
            fixed_question['category'] = 'General'
        
        if 'tags' not in fixed_question:
            fixed_question['tags'] = []
        
        # Fix common structure issues
        question_type = fixed_question.get('type', 'multiple_choice')
        
        if question_type == 'multiple_choice':
            if 'correct_answers' not in fixed_question:
                fixed_question['correct_answers'] = [0]
            elif not isinstance(fixed_question['correct_answers'], list):
                fixed_question['correct_answers'] = [fixed_question['correct_answers']]
        
        return fixed_question

    def validate_question_comprehensive(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive question validation (compatibility method for tests).
        
        Args:
            question: Question dictionary to validate
            
        Returns:
            Dictionary with validation results
        """
        result = self.validate_question(question)
        
        return {
            'overall_status': 'valid' if result.is_valid else 'invalid',
            'validation_score': result.score,
            'issues': [issue.to_dict() if hasattr(issue, 'to_dict') else {
                'severity': getattr(issue, 'severity', 'unknown'),
                'category': getattr(issue, 'category', 'unknown'),
                'message': getattr(issue, 'message', str(issue))
            } for issue in result.issues],
            'flags': result.flags,
            'is_valid': result.is_valid
        }


# Streamlit integration helpers
def st_validate_question(question: Dict[str, Any], 
                        validator: Optional[Q2JSONValidationManager] = None) -> None:
    """Streamlit helper to display validation results."""
    import streamlit as st
    
    if validator is None:
        validator = Q2JSONValidationManager()
    
    result = validator.validate_question(question)
    
    # Display overall status
    if result.is_valid:
        st.success(f"✅ Question is valid (Score: {result.score:.1f}/100)")
    else:
        st.error(f"❌ Question has validation issues (Score: {result.score:.1f}/100)")
    
    # Display flags
    if result.flags:
        st.info(f"🏷️ Flags: {', '.join(result.flags)}")
    
    # Display issues by category
    issues_by_category = {}
    for issue in result.issues:
        if issue.category not in issues_by_category:
            issues_by_category[issue.category] = []
        issues_by_category[issue.category].append(issue)
    
    for category, issues in issues_by_category.items():
        with st.expander(f"{category.title()} Issues ({len(issues)})"):
            for issue in issues:
                if issue.severity == 'error':
                    st.error(f"**{issue.field or 'General'}**: {issue.message}")
                elif issue.severity == 'warning':
                    st.warning(f"**{issue.field or 'General'}**: {issue.message}")
                else:
                    st.info(f"**{issue.field or 'General'}**: {issue.message}")
                
                if issue.suggestion:
                    st.caption(f"💡 Suggestion: {issue.suggestion}")


def st_validate_question_set(questions: List[Dict[str, Any]],
                           validator: Optional[Q2JSONValidationManager] = None) -> None:
    """Streamlit helper to display validation results for question set."""
    import streamlit as st
    
    if validator is None:
        validator = Q2JSONValidationManager()
    
    results = validator.validate_question_set(questions)
    summary = results['summary']
    
    # Display summary
    st.subheader("Validation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Questions", summary['total_questions'])
    with col2:
        st.metric("Valid Questions", summary['valid_questions'])
    with col3:
        st.metric("Invalid Questions", summary['invalid_questions'])
    with col4:
        st.metric("Total Issues", summary['total_issues'])
    
    # Average score
    st.metric("Average Quality Score", f"{summary['average_score']:.1f}/100")
    
    # Flag distribution
    if summary['flag_counts']:
        st.subheader("Common Flags")
        for flag, count in summary['flag_counts'].items():
            st.write(f"- {flag}: {count} questions")
    
    # Category issues
    if summary['category_issues']:
        st.subheader("Issues by Category")
        for category, count in summary['category_issues'].items():
            st.write(f"- {category}: {count} issues")
    
    # Individual results
    with st.expander("Individual Question Results"):
        for result in results['individual_results']:
            idx = result['question_index']
            question_result = result['result']
            
            if question_result['is_valid']:
                st.success(f"Question {idx + 1}: Valid (Score: {question_result['score']:.1f})")
            else:
                st.error(f"Question {idx + 1}: {len(question_result['issues'])} issues (Score: {question_result['score']:.1f})")
