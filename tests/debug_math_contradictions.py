"""
Debug analyzer for mathematical consistency detection
Shows exactly what patterns are being flagged as contradictions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import re
from modules.mathematical_consistency_detector import MathematicalConsistencyDetector


def debug_pattern_extraction(text: str, question_num: int):
    """Debug what patterns are being extracted from feedback text"""
    
    print(f"\n=== DEBUGGING QUESTION {question_num} ===")
    print(f"Feedback text: {text[:200]}...")
    print()
    
    # Show all numbers found
    all_numbers = []
    number_pattern = r'(\d+\.?\d*)'
    for match in re.finditer(number_pattern, text):
        try:
            value = float(match.group(1))
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].strip()
            all_numbers.append((value, context, match.start()))
        except ValueError:
            continue
    
    print(f"📊 ALL NUMBERS FOUND ({len(all_numbers)}):")
    for i, (value, context, pos) in enumerate(all_numbers):
        print(f"  {i+1:2d}. {value:8.4f} at pos {pos:3d}: ...{context}...")
    
    # Show what the detector considers "final answers"
    detector = MathematicalConsistencyDetector()
    final_answers = detector._extract_final_answer_values(text)
    
    print(f"\n🎯 FINAL ANSWERS DETECTED ({len(final_answers)}):")
    for i, (value, context) in enumerate(final_answers):
        print(f"  {i+1}. {value:8.4f}: {context[:80]}...")
    
    return all_numbers, final_answers


def analyze_contradictions_in_detail():
    """Load the MOSFET file and analyze each contradiction in detail"""
    
    print("🔍 DETAILED CONTRADICTION ANALYSIS")
    print("=" * 60)
    
    # Load test data
    test_file_path = "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json"
    
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = '\n'.join(line for line in content.split('\n') if not line.strip().startswith('//'))
            test_data = json.loads(content)
    except FileNotFoundError:
        print("❌ Could not find test file")
        return
    
    print(f"✅ Loaded {len(test_data['questions'])} questions\n")
    
    # Analyze each question's feedback
    for i, question in enumerate(test_data['questions']):
        if 'feedback_correct' in question:
            correct_answer = question.get('correct_answer', 'N/A')
            print(f"Question {i+1} - Declared Answer: {correct_answer}")
            
            all_nums, final_answers = debug_pattern_extraction(
                question['feedback_correct'], i+1
            )
    
    # Run the detector and show each contradiction
    detector = MathematicalConsistencyDetector(tolerance_threshold=0.05)
    contradictions = detector.detect_contradictions(test_data)
    
    print(f"\n🚨 CONTRADICTIONS ANALYSIS ({len(contradictions)} total)")
    print("=" * 60)
    
    for i, contradiction in enumerate(contradictions, 1):
        print(f"\nContradiction #{i}:")
        print(f"  Question: {contradiction.question_index + 1}")
        print(f"  Type: {contradiction.field_name}")
        print(f"  Values: {contradiction.values_found}")
        print(f"  Difference: {contradiction.percentage_difference:.1f}%")
        print(f"  Severity: {contradiction.severity}")
        print(f"  Context 1: {contradiction.contexts[0][:100]}...")
        if len(contradiction.contexts) > 1:
            print(f"  Context 2: {contradiction.contexts[1][:100]}...")
        
        # Analyze if this should be a contradiction
        val1, val2 = contradiction.values_found[0], contradiction.values_found[1]
        
        # Check for normal rounding
        if abs(val1 - val2) < 0.1 and min(val1, val2) > 0.1:
            ratio = max(val1, val2) / min(val1, val2)
            if ratio < 1.1:  # Less than 10% difference
                print(f"  🤔 ANALYSIS: Likely normal rounding ({val1:.3f} vs {val2:.3f})")
        
        # Check for intermediate vs final
        if any(v in [0.4, 0.5, 0.8, 2.0, 2.8] for v in contradiction.values_found):
            print(f"  🤔 ANALYSIS: Contains common intermediate values")
        
        # Check percentage reasonableness
        if contradiction.percentage_difference < 10:
            print(f"  ✅ ANALYSIS: Small difference - likely acceptable")
        elif contradiction.percentage_difference > 50:
            print(f"  🚨 ANALYSIS: Large difference - likely real error")
        else:
            print(f"  🔶 ANALYSIS: Medium difference - needs review")


def test_specific_patterns():
    """Test specific patterns that should or shouldn't trigger contradictions"""
    
    print(f"\n🧪 PATTERN TESTING")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Normal calculation progression",
            "text": "V_T = 0.5 + 0.4(1.673 - 0.894) = 0.5 + 0.4(0.779) = 0.5 + 0.3116 = 0.8116 V",
            "declared_answer": "0.8116",
            "should_contradict": False
        },
        {
            "name": "Normal rounding",
            "text": "The calculation gives V_T = 0.8116 V. Rounding to three decimal places, V_T ≈ 0.812 V.",
            "declared_answer": "0.812",
            "should_contradict": False
        },
        {
            "name": "Real contradiction",
            "text": "The calculation gives V_T = 0.8116 V. However, the final answer is V_T = 0.776 V.",
            "declared_answer": "0.776",
            "should_contradict": True
        },
        {
            "name": "Intermediate steps only",
            "text": "Using gamma = 0.4 and phi_F = 0.5, we calculate sqrt(2.8) = 1.673",
            "declared_answer": "1.673",
            "should_contradict": False
        }
    ]
    
    detector = MathematicalConsistencyDetector(tolerance_threshold=0.05)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Text: {test_case['text']}")
        print(f"   Declared: {test_case['declared_answer']}")
        print(f"   Should contradict: {test_case['should_contradict']}")
        
        # Create mock data
        mock_data = {
            "questions": [{
                "correct_answer": test_case["declared_answer"],
                "feedback_correct": test_case["text"]
            }]
        }
        
        contradictions = detector.detect_contradictions(mock_data)
        has_contradiction = len(contradictions) > 0
        
        if has_contradiction == test_case["should_contradict"]:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL - Expected: {test_case['should_contradict']}, Got: {has_contradiction}")
            
            if contradictions:
                for contradiction in contradictions:
                    print(f"      Found: {contradiction.values_found} ({contradiction.percentage_difference:.1f}%)")


if __name__ == "__main__":
    analyze_contradictions_in_detail()
    test_specific_patterns()