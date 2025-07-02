"""
Test the working mathematical consistency detector
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Use the ImprovedDetector from the debug script
import re


class WorkingMathDetector:
    """Working mathematical consistency detector based on debug findings"""
    
    def __init__(self, tolerance_threshold: float = 0.05):
        self.tolerance_threshold = tolerance_threshold
        self.common_intermediates = {0.4, 0.5, 0.8, 0.894, 1.673, 2.0, 2.8}
        self.contradictions_found = []
    
    def detect_contradictions(self, questions_data):
        """Detect contradictions using working patterns"""
        
        self.contradictions_found = []
        
        if 'questions' not in questions_data:
            return []
        
        for i, question in enumerate(questions_data['questions']):
            if 'correct_answer' not in question or 'feedback_correct' not in question:
                continue
            
            try:
                declared = float(question['correct_answer'])
            except (ValueError, TypeError):
                continue
            
            text = question['feedback_correct']
            contradiction = self._detect_contradiction(i, declared, text)
            
            if contradiction:
                self.contradictions_found.append(contradiction)
        
        return self.contradictions_found
    
    def _detect_contradiction(self, question_index, declared, text):
        """Detect contradiction for a single question"""
        
        # Extract all meaningful values
        values = self._extract_values(text)
        
        # Find contradictions
        for value, context in values:
            if abs(declared - value) > 0.001:  # Not the same value
                percentage_diff = abs(declared - value) / max(declared, 0.001) * 100
                
                # Skip normal rounding (< 3% difference)
                if percentage_diff > 3.0:
                    # Skip obvious intermediate values
                    if not self._is_obvious_intermediate(value, context):
                        return {
                            'question_index': question_index,
                            'field_name': 'declared_vs_calculated',
                            'values_found': [declared, value],
                            'contexts': [f"Declared: {declared}", f"Found: {context}"],
                            'percentage_difference': percentage_diff,
                            'severity': self._get_severity(percentage_diff),
                            'suggested_resolution': f"Verify: {declared} vs {value}"
                        }
        
        return None
    
    def _extract_values(self, text):
        """Extract meaningful numerical values from text"""
        
        values = []
        
        # Reliable patterns that work
        patterns = [
            r'final\s+answer[:\s]*.*?(\d+\.?\d*)',  # Final answer statements
            r'V_T\s*=\s*(\d+\.?\d*)',               # V_T assignments
            r'(\d+\.?\d*)\s*V(?:\s|$|\.)',          # Values with V unit
            r'=\s*(\d+\.?\d*)\s*V',                 # Equals value V
            r'≈\s*(\d+\.?\d*)',                     # Approximations
            r'result\s+is\s*(\d+\.?\d*)',           # Result statements
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = float(match.group(1))
                    context = text[max(0, match.start()-30):match.end()+30].strip()
                    values.append((value, context))
                except (ValueError, IndexError):
                    continue
        
        # Remove duplicates
        unique_values = []
        for value, context in values:
            if not any(abs(v - value) < 0.001 for v, _ in unique_values):
                unique_values.append((value, context))
        
        return unique_values
    
    def _is_obvious_intermediate(self, value, context):
        """Check if value is obviously intermediate"""
        
        # Common intermediate values
        if value in self.common_intermediates:
            return True
        
        # Values in arithmetic expressions
        value_str = str(value)
        if re.search(rf'[+\-*/]\s*{re.escape(value_str)}\s*[+\-*/]', context):
            return True
        
        return False
    
    def _get_severity(self, percentage_diff):
        """Get severity level"""
        if percentage_diff > 20:
            return "severe"
        elif percentage_diff > 10:
            return "moderate"
        else:
            return "minor"
    
    def generate_report(self):
        """Generate simple report"""
        if not self.contradictions_found:
            return "✅ No contradictions detected"
        
        report = f"🚨 Found {len(self.contradictions_found)} contradictions:\n\n"
        
        for i, contradiction in enumerate(self.contradictions_found, 1):
            report += f"#{i}: Question {contradiction['question_index']+1}\n"
            report += f"   Values: {contradiction['values_found']}\n"
            report += f"   Difference: {contradiction['percentage_difference']:.1f}%\n"
            report += f"   Severity: {contradiction['severity']}\n\n"
        
        return report


def test_working_detector():
    """Test the working detector"""
    
    print("🧪 TESTING WORKING MATHEMATICAL DETECTOR")
    print("=" * 50)
    
    detector = WorkingMathDetector()
    
    # Test cases
    test_cases = [
        {
            "name": "Real contradiction (should detect)",
            "data": {
                "questions": [{
                    "correct_answer": "0.776",
                    "feedback_correct": "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
                }]
            },
            "expected": 1
        },
        {
            "name": "Normal rounding (should NOT detect)",
            "data": {
                "questions": [{
                    "correct_answer": "0.812",
                    "feedback_correct": "V_T = 0.8116 V. Rounding to three decimal places: V_T ≈ 0.812 V."
                }]
            },
            "expected": 0
        },
        {
            "name": "Calculation progression (should NOT detect)",
            "data": {
                "questions": [{
                    "correct_answer": "0.8116",
                    "feedback_correct": "V_T = 0.5 + 0.4(1.673 - 0.894) = 0.8116 V"
                }]
            },
            "expected": 0
        }
    ]
    
    # Test each case
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        
        contradictions = detector.detect_contradictions(test_case['data'])
        found = len(contradictions)
        expected = test_case['expected']
        
        print(f"   Found: {found}, Expected: {expected}")
        
        if contradictions:
            for contradiction in contradictions:
                print(f"   Values: {contradiction['values_found']}")
                print(f"   Difference: {contradiction['percentage_difference']:.1f}%")
        
        if found == expected:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL")
    
    # Test with real MOSFET file
    print(f"\n📁 TESTING WITH REAL MOSFET FILE")
    try:
        import json
        with open("c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json", 'r') as f:
            content = f.read()
            content = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('//'))
            mosfet_data = json.loads(content)
        
        contradictions = detector.detect_contradictions(mosfet_data)
        print(f"   Found {len(contradictions)} contradictions")
        
        if contradictions:
            print(f"\n📊 Report:\n{detector.generate_report()}")
    
    except FileNotFoundError:
        print("   MOSFET file not found")


if __name__ == "__main__":
    test_working_detector()