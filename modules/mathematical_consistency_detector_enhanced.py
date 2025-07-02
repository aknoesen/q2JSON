"""
Enhanced Mathematical Consistency Detector
Improved value extraction and contradiction detection for complex mathematical content
"""

import re
import json
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Any


@dataclass
class MathematicalContradiction:
    """Represents a mathematical contradiction found in question content"""
    question_index: int
    values_found: List[float]
    percentage_difference: float
    severity: str
    contexts: List[str]
    declared_answer: str


class MathematicalConsistencyDetectorEnhanced:
    """
    Enhanced mathematical consistency detector with improved value extraction
    and smarter intermediate filtering
    """
    
    def __init__(self):
        """Initialize the enhanced detector"""
        self.contradictions_found = []
        self.processing_stats = {
            'questions_analyzed': 0,
            'values_extracted': 0,
            'contradictions_found': 0
        }
        
        # More selective intermediate filtering
        self.basic_constants = {0.5, 0.4, 1.0, 2.0, 3.0, 4.0, 5.0}
        self.tolerance_threshold = 0.02  # 2% threshold (more sensitive)
        
    def detect_contradictions(self, questions_data: dict) -> List[MathematicalContradiction]:
        """
        Detect mathematical contradictions in questions data
        Enhanced with better value extraction and context analysis
        """
        
        self.contradictions_found = []
        self.processing_stats = {
            'questions_analyzed': 0,
            'values_extracted': 0,
            'contradictions_found': 0
        }
        
        questions = questions_data.get('questions', [])
        
        for question_index, question in enumerate(questions):
            self._analyze_question_enhanced(question, question_index)
        
        # Deduplicate contradictions
        self._deduplicate_contradictions()
        
        self.processing_stats['contradictions_found'] = len(self.contradictions_found)
        
        return self.contradictions_found
    
    def _analyze_question_enhanced(self, question: dict, question_index: int):
        """Enhanced question analysis with improved value extraction"""
        
        self.processing_stats['questions_analyzed'] += 1
        
        # Get declared answer
        declared_answer = question.get('correct_answer', '')
        if not declared_answer:
            return
        
        try:
            declared_value = float(declared_answer)
        except (ValueError, TypeError):
            return
        
        # Extract values from feedback with enhanced patterns
        feedback_correct = question.get('feedback_correct', '')
        feedback_incorrect = question.get('feedback_incorrect', '')
        
        all_feedback = feedback_correct + ' ' + feedback_incorrect
        
        if not all_feedback.strip():
            return
        
        # Enhanced value extraction
        extracted_values = self._extract_values_enhanced(all_feedback, declared_value)
        
        if not extracted_values:
            return
        
        self.processing_stats['values_extracted'] += len(extracted_values)
        
        # Check for contradictions
        for value, context in extracted_values:
            percentage_diff = abs(value - declared_value) / declared_value * 100
            
            if percentage_diff > self.tolerance_threshold * 100:  # Convert to percentage
                severity = self._determine_severity(percentage_diff)
                
                contradiction = MathematicalContradiction(
                    question_index=question_index,
                    values_found=[declared_value, value],
                    percentage_difference=percentage_diff,
                    severity=severity,
                    contexts=[context],
                    declared_answer=declared_answer
                )
                
                self.contradictions_found.append(contradiction)
    
    def _deduplicate_contradictions(self):
        """Remove duplicate contradictions (same question, same values)"""
        
        if not self.contradictions_found:
            return
        
        # Group by question index and values
        unique_contradictions = {}
        
        for contradiction in self.contradictions_found:
            # Create key based on question and values (rounded to avoid floating point issues)
            key = (
                contradiction.question_index,
                round(contradiction.values_found[0], 4),
                round(contradiction.values_found[1], 4)
            )
            
            if key not in unique_contradictions:
                unique_contradictions[key] = contradiction
            else:
                # Merge contexts if duplicate found
                existing = unique_contradictions[key]
                existing.contexts.extend(contradiction.contexts)
        
        self.contradictions_found = list(unique_contradictions.values())
    
    def _extract_values_enhanced(self, text: str, declared_value: float) -> List[Tuple[float, str]]:
        """
        Enhanced value extraction with better pattern recognition
        Returns list of (value, context) tuples
        """
        
        extracted_values = []
        
        # Enhanced patterns for final answers and calculation results
        final_answer_patterns = [
            # Final answer patterns
            (r'Final answer[:\s]*[A-Z_]*\s*[=≈]\s*(\d+\.\d+)', 'Final answer'),
            (r'[A-Z_]+\s*≈\s*(\d+\.\d+)\s*V', 'Approximation'),
            (r'[A-Z_]+\s*approx\s*(\d+\.\d+)', 'Approximation'),
            (r'[A-Z_]+\s*=\s*(\d+\.\d+)\s*V[.\s]', 'Calculation result'),
            
            # Calculation conclusion patterns
            (r'gives\s*[A-Z_]*\s*=\s*(\d+\.\d+)', 'Calculation gives'),
            (r'get\s*[A-Z_]*\s*=\s*(\d+\.\d+)', 'Calculation result'),
            (r'Calculation.*?(\d+\.\d+)\s*V', 'Calculation'),
            
            # Rounding patterns
            (r'Rounding.*?(\d+\.\d+)', 'Rounding result'),
            (r'three decimal places.*?(\d+\.\d+)', 'Rounded value'),
            
            # Context-specific patterns
            (r'My calculation.*?(\d+\.\d+)', 'Alternative calculation'),
        ]
        
        for pattern, context_type in final_answer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match)
                    
                    # Skip if it's obviously the declared value (exact match)
                    if abs(value - declared_value) < 0.001:
                        continue
                    
                    # Skip basic constants
                    if value in self.basic_constants:
                        continue
                    
                    # Skip very small values (likely intermediate)
                    if value < 0.1:
                        continue
                    
                    # Find the context around this value
                    context = self._get_value_context(text, match, 50)
                    
                    extracted_values.append((value, f"{context_type}: {context}"))
                    
                except ValueError:
                    continue
        
        return extracted_values
    
    def _get_value_context(self, text: str, value_str: str, context_length: int = 50) -> str:
        """Extract context around a specific value"""
        
        # Find the position of the value in the text
        pos = text.find(value_str)
        if pos == -1:
            return value_str
        
        # Extract context before and after
        start = max(0, pos - context_length)
        end = min(len(text), pos + len(value_str) + context_length)
        
        context = text[start:end].strip()
        
        # Clean up the context
        context = re.sub(r'\s+', ' ', context)
        
        return context
    
    def _determine_severity(self, percentage_difference: float) -> str:
        """Determine the severity of a contradiction based on percentage difference"""
        
        if percentage_difference >= 20:
            return "severe"
        elif percentage_difference >= 10:
            return "moderate"
        else:
            return "minor"
    
    def get_summary_stats(self) -> dict:
        """Get summary statistics of the analysis"""
        
        if not self.contradictions_found:
            return {
                'status': 'passed',
                'total_contradictions': 0,
                'questions_analyzed': self.processing_stats['questions_analyzed'],
                'values_extracted': self.processing_stats['values_extracted']
            }
        
        # Calculate severity breakdown
        by_severity = {}
        for contradiction in self.contradictions_found:
            severity = contradiction.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Calculate difference stats
        differences = [c.percentage_difference for c in self.contradictions_found]
        
        return {
            'status': 'issues_found',
            'total_contradictions': len(self.contradictions_found),
            'by_severity': by_severity,
            'avg_difference': sum(differences) / len(differences),
            'max_difference': max(differences),
            'questions_affected': len(set(c.question_index for c in self.contradictions_found)),
            'questions_analyzed': self.processing_stats['questions_analyzed'],
            'values_extracted': self.processing_stats['values_extracted']
        }
    
    def has_severe_contradictions(self) -> bool:
        """Check if any severe contradictions were found"""
        return any(c.severity == "severe" for c in self.contradictions_found)
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed report of all contradictions found"""
        
        if not self.contradictions_found:
            return ("✅ Mathematical Consistency Check: PASSED\n"
                   f"   Analyzed {self.processing_stats['questions_analyzed']} questions\n"
                   f"   Extracted {self.processing_stats['values_extracted']} values\n"
                   "   No mathematical contradictions detected")
        
        report = []
        report.append("🚨 Mathematical Consistency Check: ISSUES FOUND")
        report.append("=" * 60)
        
        stats = self.get_summary_stats()
        report.append(f"Questions analyzed: {stats['questions_analyzed']}")
        report.append(f"Values extracted: {stats['values_extracted']}")
        report.append(f"Contradictions found: {stats['total_contradictions']}")
        report.append("")
        
        # Individual contradictions
        for i, contradiction in enumerate(self.contradictions_found, 1):
            severity_icon = {"minor": "⚠️", "moderate": "🔶", "severe": "🚨"}
            icon = severity_icon.get(contradiction.severity, "⚠️")
            
            report.append(f"{icon} Contradiction #{i} ({contradiction.severity.upper()})")
            report.append(f"Question {contradiction.question_index + 1}")
            
            values = contradiction.values_found
            if len(values) >= 2:
                report.append(f"Declared answer: {values[0]}")
                report.append(f"Found in feedback: {values[1]}")
            
            report.append(f"Percentage difference: {contradiction.percentage_difference:.1f}%")
            
            # Show all contexts if multiple
            if len(contradiction.contexts) == 1:
                context = contradiction.contexts[0]
                report.append(f"Context: {context[:100]}...")
            else:
                report.append(f"Found in {len(contradiction.contexts)} contexts:")
                for j, context in enumerate(contradiction.contexts[:3], 1):  # Show max 3 contexts
                    report.append(f"  {j}. {context[:80]}...")
            
            report.append(f"Recommendation: Verify calculation: declared {values[0]} vs found {values[1]}")
            report.append("")
        
        return "\n".join(report)


# Test the enhanced detector
if __name__ == "__main__":
    print("Enhanced Mathematical Consistency Detector")
    print("Testing improved value extraction and contradiction detection")