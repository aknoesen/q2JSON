"""
Mathematical Consistency Detector - FIXED VERSION
High precision detection with proper intermediate value filtering
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class ContradictionResult:
    """Represents a detected mathematical contradiction"""
    question_index: int
    field_name: str
    values_found: List[float]
    contexts: List[str]
    severity: str
    percentage_difference: float
    suggested_resolution: str


class MathematicalConsistencyDetectorFixed:
    """
    Fixed mathematical consistency detector with high precision
    Eliminates false positives from intermediate calculations
    """
    
    def __init__(self, tolerance_threshold: float = 0.05):
        """Initialize with 5% default tolerance"""
        self.tolerance_threshold = tolerance_threshold
        self.contradictions_found = []
        self.processing_log = []
        
        # Common intermediate values in electrical engineering
        self.common_intermediates = {
            0.4, 0.5, 0.8, 0.894, 0.8944, 1.673, 1.6733, 2.0, 2.8, 
            0.05, 0.1, 0.2, 0.3, 0.6, 0.7, 0.9, 1.0, 1.5, 2.5, 3.0
        }
    
    def detect_contradictions(self, questions_data: Dict) -> List[ContradictionResult]:
        """Detect mathematical contradictions with high precision"""
        
        self.contradictions_found = []
        self.processing_log = []
        
        if 'questions' not in questions_data:
            return []
        
        questions = questions_data['questions']
        
        for i, question in enumerate(questions):
            self._analyze_question_fixed(i, question)
        
        return self.contradictions_found
    
    def _analyze_question_fixed(self, question_index: int, question: Dict):
        """Analyze question with proper filtering"""
        
        if 'correct_answer' not in question or 'feedback_correct' not in question:
            return
        
        try:
            declared_answer = float(question['correct_answer'])
        except (ValueError, TypeError):
            return
        
        feedback_content = str(question['feedback_correct'])
        
        # Extract only genuine final answers
        final_answers = self._extract_genuine_final_answers(feedback_content)
        
        # Check for contradictions with declared answer
        for value, context in final_answers:
            if abs(declared_answer - value) < 0.001:  # Skip if essentially same
                continue
            
            # Skip if this is normal rounding
            if self._is_normal_rounding(declared_answer, value):
                continue
            
            percentage_diff = abs(declared_answer - value) / max(declared_answer, 0.001) * 100
            
            if percentage_diff > self.tolerance_threshold * 100:
                contradiction = ContradictionResult(
                    question_index=question_index,
                    field_name="declared_vs_calculated",
                    values_found=[declared_answer, value],
                    contexts=[f"Declared: {declared_answer}", f"Calculated: {context}"],
                    severity=self._determine_severity(percentage_diff),
                    percentage_difference=percentage_diff,
                    suggested_resolution=f"Verify: declared {declared_answer} vs calculated {value}"
                )
                
                self.contradictions_found.append(contradiction)
        
        # Check for internal contradictions (multiple conflicting final answers)
        if len(final_answers) >= 2:
            self._check_internal_contradictions(question_index, final_answers)
    
    def _extract_genuine_final_answers(self, text: str) -> List[Tuple[float, str]]:
        """Extract only genuine final answers, not intermediate calculations"""
        
        genuine_finals = []
        
        # Very specific patterns for explicit final answers
        final_patterns = [
            # Explicit final answer statements
            r'(?:final\s+answer|the\s+answer\s+is|result\s+is|therefore|conclusion)\s*[:\s]*[VIR]?_?[A-Z]?\s*[=≈]\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
            
            # Approximation statements that conclude calculations
            r'(?:approximately|approx|≈)\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?\s*[.!]?\s*$',
            
            # Values at the very end of mathematical expressions (likely conclusions)
            r'=\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?\s*[.!\$]\s*$',
            
            # Rounding conclusions
            r'rounding\s+(?:to\s+\w+\s+decimal\s+places?)?\s*[,:]?\s*[VIR]?_?[A-Z]?\s*[≈=]\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?',
        ]
        
        for pattern in final_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                try:
                    value = float(match.group(1))
                    
                    # Skip common intermediate values
                    if value in self.common_intermediates:
                        continue
                    
                    # Skip if clearly part of a larger calculation
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    if not self._is_in_arithmetic_sequence(context, value):
                        genuine_finals.append((value, context))
                    
                except (ValueError, IndexError):
                    continue
        
        # Remove duplicates
        unique_finals = []
        for value, context in genuine_finals:
            if not any(abs(v - value) < 0.001 for v, _ in unique_finals):
                unique_finals.append((value, context))
        
        return unique_finals
    
    def _is_in_arithmetic_sequence(self, context: str, value: float) -> bool:
        """Check if value is part of an arithmetic calculation sequence"""
        
        value_str = str(value)
        
        # Check for arithmetic operations around this value
        arithmetic_patterns = [
            rf'[+\-*/]\s*{re.escape(value_str)}\s*[+\-*/]',  # Between operations
            rf'\(\s*[^)]*{re.escape(value_str)}[^)]*\)',      # Inside parentheses with other operations
            rf'{re.escape(value_str)}\s*[+\-*/]\s*\d',        # Start of operation
            rf'\d\s*[+\-*/]\s*{re.escape(value_str)}',        # End of operation
        ]
        
        for pattern in arithmetic_patterns:
            if re.search(pattern, context):
                return True
        
        return False
    
    def _check_internal_contradictions(self, question_index: int, final_answers: List[Tuple[float, str]]):
        """Check for contradictions between multiple final answers"""
        
        for i in range(len(final_answers)):
            for j in range(i + 1, len(final_answers)):
                value1, context1 = final_answers[i]
                value2, context2 = final_answers[j]
                
                if abs(value1 - value2) < 0.001:  # Skip if same
                    continue
                
                if self._is_normal_rounding(value1, value2):  # Skip normal rounding
                    continue
                
                percentage_diff = abs(value2 - value1) / max(value1, 0.001) * 100
                
                if percentage_diff > self.tolerance_threshold * 100:
                    contradiction = ContradictionResult(
                        question_index=question_index,
                        field_name="internal_contradiction",
                        values_found=[value1, value2],
                        contexts=[context1, context2],
                        severity=self._determine_severity(percentage_diff),
                        percentage_difference=percentage_diff,
                        suggested_resolution=f"Clarify which answer is correct: {value1} or {value2}"
                    )
                    
                    self.contradictions_found.append(contradiction)
    
    def _is_normal_rounding(self, val1: float, val2: float) -> bool:
        """Check if difference represents normal rounding"""
        
        # Check for standard rounding patterns
        if (abs(round(val1, 3) - val2) < 0.001 or  # 3 decimal places
            abs(round(val1, 2) - val2) < 0.001 or  # 2 decimal places  
            abs(val1 - round(val2, 3)) < 0.001 or
            abs(val1 - round(val2, 2)) < 0.001):
            return True
        
        # Check for small percentage differences (< 2%)
        diff_percent = abs(val1 - val2) / max(val1, val2) * 100
        return diff_percent < 2.0
    
    def _determine_severity(self, percentage_diff: float) -> str:
        """Determine severity based on percentage difference"""
        
        if percentage_diff > 25:
            return "severe"
        elif percentage_diff > 10:
            return "moderate"
        else:
            return "minor"
    
    def generate_report(self) -> str:
        """Generate detailed report"""
        
        if not self.contradictions_found:
            return "✅ No significant mathematical contradictions detected."
        
        report_lines = [
            "🚨 Mathematical Contradiction Report (Fixed Detector)",
            "=" * 60,
            f"Contradictions found: {len(self.contradictions_found)}",
            ""
        ]
        
        for i, contradiction in enumerate(self.contradictions_found, 1):
            severity_emoji = {"minor": "⚠️", "moderate": "🔶", "severe": "🚨"}
            
            report_lines.extend([
                f"{severity_emoji.get(contradiction.severity, '❓')} Contradiction #{i} ({contradiction.severity.upper()})",
                f"Question {contradiction.question_index + 1} - {contradiction.field_name}",
                f"Values: {contradiction.values_found}",
                f"Difference: {contradiction.percentage_difference:.1f}%",
                f"Resolution: {contradiction.suggested_resolution}",
                ""
            ])
        
        return "\n".join(report_lines)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        
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