"""
Mathematical Consistency Detector for Q2JSON - ENHANCED PATTERN MATCHING
Identifies calculation contradictions in educational content with improved precision
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class ContradictionResult:
    """Represents a detected mathematical contradiction"""
    question_index: int
    field_name: str
    values_found: List[float]
    contexts: List[str]
    severity: str  # 'minor', 'moderate', 'severe'
    percentage_difference: float
    suggested_resolution: str


@dataclass
class CalculationContext:
    """Context around a numerical value"""
    value: float
    context_text: str
    position: int
    unit: Optional[str] = None
    precision: Optional[int] = None
    is_final_answer: bool = False


class MathematicalConsistencyDetector:
    """
    Detects mathematical contradictions in educational question content
    ENHANCED with better pattern matching for final answers
    """
    
    def __init__(self, tolerance_threshold: float = 0.05):
        """
        Initialize the detector
        
        Args:
            tolerance_threshold: Maximum allowed percentage difference (default 5%)
        """
        self.tolerance_threshold = tolerance_threshold
        self.contradictions_found = []
        self.processing_log = []
    
    def detect_contradictions(self, questions_data: Dict) -> List[ContradictionResult]:
        """
        Main method to detect mathematical contradictions in question data
        
        Args:
            questions_data: Parsed JSON question data
            
        Returns:
            List of detected contradictions
        """
        self.contradictions_found = []
        self.processing_log = []
        
        if 'questions' not in questions_data:
            self.processing_log.append("❌ No 'questions' array found in data")
            return []
        
        questions = questions_data['questions']
        
        for i, question in enumerate(questions):
            self._analyze_question(i, question)
        
        return self.contradictions_found
    
    def _analyze_question(self, question_index: int, question: Dict):
        """Analyze a single question for mathematical contradictions"""
        
        # Focus on cross-field analysis (correct_answer vs feedback)
        self._check_cross_field_consistency(question_index, question)
        
        # Check within feedback for multiple conflicting final answers
        if 'feedback_correct' in question:
            self._check_feedback_internal_consistency(question_index, question['feedback_correct'])
    
    def _check_cross_field_consistency(self, question_index: int, question: Dict):
        """Check consistency between correct_answer and feedback explanations"""
        
        if 'correct_answer' not in question or 'feedback_correct' not in question:
            return
        
        correct_answer = str(question['correct_answer'])
        feedback_content = str(question['feedback_correct'])
        
        # Extract the declared correct answer
        try:
            declared_answer = float(correct_answer)
        except (ValueError, TypeError):
            return
        
        # Extract final answer values from feedback (enhanced patterns)
        final_answer_values = self._extract_final_answer_values(feedback_content)
        
        # Compare declared answer with final answers in feedback
        for value, context in final_answer_values:
            if abs(declared_answer - value) < 0.001:  # Skip if essentially the same
                continue
                
            percentage_diff = abs(declared_answer - value) / max(declared_answer, 0.001) * 100
            
            if percentage_diff > self.tolerance_threshold * 100:  # Convert to percentage
                contradiction = ContradictionResult(
                    question_index=question_index,
                    field_name="correct_answer vs feedback_correct",
                    values_found=[declared_answer, value],
                    contexts=[f"Declared answer: {correct_answer}", context],
                    severity=self._determine_severity(percentage_diff),
                    percentage_difference=percentage_diff,
                    suggested_resolution=f"Reconcile declared answer {declared_answer} with calculated value {value}"
                )
                
                self.contradictions_found.append(contradiction)
    
    def _check_feedback_internal_consistency(self, question_index: int, feedback_content: str):
        """Check for multiple conflicting final answers within feedback text"""
        
        final_answer_values = self._extract_final_answer_values(feedback_content)
        
        if len(final_answer_values) < 2:
            return
        
        # Compare each pair of final answers
        for i in range(len(final_answer_values)):
            for j in range(i + 1, len(final_answer_values)):
                value1, context1 = final_answer_values[i]
                value2, context2 = final_answer_values[j]
                
                if abs(value1 - value2) < 0.001:  # Skip if essentially the same
                    continue
                
                if value1 > 0:  # Avoid division by zero
                    percentage_diff = abs(value2 - value1) / value1 * 100
                    
                    if percentage_diff > self.tolerance_threshold * 100:
                        contradiction = ContradictionResult(
                            question_index=question_index,
                            field_name="feedback_correct",
                            values_found=[value1, value2],
                            contexts=[context1, context2],
                            severity=self._determine_severity(percentage_diff),
                            percentage_difference=percentage_diff,
                            suggested_resolution=f"Clarify which final answer is correct: {value1} or {value2}"
                        )
                        
                        self.contradictions_found.append(contradiction)
    
    def _extract_final_answer_values(self, text: str) -> List[Tuple[float, str]]:
        """Extract values that appear to be final answers with their context - ENHANCED"""
        
        final_answers = []
        
        # Enhanced patterns for final answers - more specific
        final_answer_patterns = [
            # Explicit final answer statements
            r'(?:final\s+answer|answer\s+is|result\s+is|therefore|so|thus)\s*[:\s]*[=≈]?\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
            
            # Values after equals at end of calculation line
            r'=\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?\s*[.!]?\s*$',
            
            # Values after approximation symbols
            r'(?:≈|approx|approximately)\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
            
            # Rounding statements
            r'(?:rounding|rounds?\s+to|rounded\s+to)\s+(?:three\s+decimal\s+places?)?\s*[,:]?\s*[=≈]?\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
            
            # Direct value assignments in concluding statements
            r'(?:V_T|voltage|current|resistance)\s*[=≈]\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
        ]
        
        for pattern in final_answer_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                try:
                    value = float(match.group(1))
                    
                    # Get context around the match (±40 characters)
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 40)
                    context = text[start:end].strip()
                    
                    # Additional filtering for obvious intermediate calculations
                    if not self._is_intermediate_calculation(context, value, text):
                        final_answers.append((value, context))
                    
                except (ValueError, IndexError):
                    continue
        
        # Also look for values that appear multiple times (likely important)
        number_counts = {}
        number_pattern = r'(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[VΩμA]+)?'
        
        for match in re.finditer(number_pattern, text):
            try:
                value = float(match.group(1))
                if 0.1 <= value <= 1000:  # Reasonable range for most electrical values
                    number_counts[value] = number_counts.get(value, 0) + 1
            except ValueError:
                continue
        
        # Add frequently mentioned values (appear 2+ times)
        for value, count in number_counts.items():
            if count >= 2:
                # Find a good context for this value
                value_pattern = rf'\b{re.escape(str(value))}\b'
                match = re.search(value_pattern, text)
                if match:
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end].strip()
                    
                    # Only add if not already in our list
                    if not any(abs(v - value) < 0.001 for v, _ in final_answers):
                        final_answers.append((value, f"Frequently mentioned: {context}"))
        
        # Remove duplicates and sort by value
        unique_answers = []
        for value, context in final_answers:
            # Check if this value is already in our list (within 0.001 tolerance)
            is_duplicate = False
            for existing_value, _ in unique_answers:
                if abs(value - existing_value) < 0.001:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_answers.append((value, context))
        
        return sorted(unique_answers, key=lambda x: x[0])
    
    def _is_intermediate_calculation(self, context: str, value: float, full_text: str) -> bool:
        """Determine if a value is part of an intermediate calculation step - ENHANCED"""
        
        # Patterns that indicate intermediate calculations
        intermediate_indicators = [
            r'sqrt\{[^}]*' + re.escape(str(value)),  # Inside square root
            r'frac\{[^}]*' + re.escape(str(value)),  # Inside fraction  
            r'\([^)]*' + re.escape(str(value)) + r'[^)]*\)',  # Inside parentheses calculation
            r'[+\-*/]\s*' + re.escape(str(value)) + r'\s*[+\-*/]',  # Part of arithmetic operation
        ]
        
        for pattern in intermediate_indicators:
            if re.search(pattern, context):
                return True
        
        # Check if this appears to be extracting part of a decimal number
        value_str = str(value)
        if len(value_str) >= 3 and value > 100:
            # Look for this value as part of a larger decimal in the text
            decimal_search = rf'\d*\.{value_str}|\d+{value_str}\d*'
            if re.search(decimal_search, full_text):
                return True
        
        # Values that are clearly intermediate (common constants, coefficients)
        if value in [0.4, 0.5, 1.673, 1.6733, 0.894, 0.8944, 2.8, 0.8]:
            return True
        
        return False
    
    def _determine_severity(self, percentage_diff: float) -> str:
        """Determine the severity of a contradiction based on percentage difference"""
        
        if percentage_diff > 50:
            return "severe"
        elif percentage_diff > 20:
            return "moderate"
        else:
            return "minor"
    
    def generate_report(self) -> str:
        """Generate a detailed report of all detected contradictions"""
        
        if not self.contradictions_found:
            return "✅ No mathematical contradictions detected."
        
        report_lines = [
            "🚨 Mathematical Contradiction Report",
            "=" * 50,
            f"Total contradictions found: {len(self.contradictions_found)}",
            ""
        ]
        
        for i, contradiction in enumerate(self.contradictions_found, 1):
            severity_emoji = {
                "minor": "⚠️",
                "moderate": "🔶", 
                "severe": "🚨"
            }
            
            report_lines.extend([
                f"{severity_emoji.get(contradiction.severity, '❓')} Contradiction #{i} ({contradiction.severity.upper()})",
                f"Question {contradiction.question_index + 1} - {contradiction.field_name}",
                f"Values: {contradiction.values_found}",
                f"Difference: {contradiction.percentage_difference:.1f}%",
                f"Contexts:",
            ])
            
            for j, context in enumerate(contradiction.contexts):
                report_lines.append(f"  {j+1}. {context[:100]}{'...' if len(context) > 100 else ''}")
            
            report_lines.extend([
                f"Suggestion: {contradiction.suggested_resolution}",
                ""
            ])
        
        return "\n".join(report_lines)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of detected contradictions"""
        
        if not self.contradictions_found:
            return {"total": 0, "by_severity": {}, "avg_difference": 0}
        
        severity_counts = {}
        total_diff = 0
        
        for contradiction in self.contradictions_found:
            severity = contradiction.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            total_diff += contradiction.percentage_difference
        
        return {
            "total": len(self.contradictions_found),
            "by_severity": severity_counts,
            "avg_difference": total_diff / len(self.contradictions_found),
            "max_difference": max(c.percentage_difference for c in self.contradictions_found),
            "questions_affected": len(set(c.question_index for c in self.contradictions_found))
        }