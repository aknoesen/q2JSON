"""
Test script to demonstrate LaTeX corrections on MOSFET data
"""

import json
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from latex_corrector import LaTeXCorrector

def test_mosfet_corrections():
    """Test LaTeX corrector on MOSFET data and show specific corrections"""
    
    print("LaTeX Corrector - MOSFET Test Data Analysis")
    print("=" * 60)
    
    # Load the original MOSFET data
    with open('test_data/MosfetQQDebug.json', 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Create corrector and apply corrections
    corrector = LaTeXCorrector()
    result = corrector.correct_latex_in_questions(original_data)
    
    print(f"Processing Results:")
    print(f"  Status: {result['status']}")
    print(f"  Total corrections: {result['corrections_made']}")
    print(f"  Questions affected: {result['questions_affected']}")
    print(f"  Pattern statistics: {result['pattern_stats']}")
    
    print("\nDetailed Corrections Made:")
    print("-" * 40)
    
    # Show specific examples of corrections
    for i, question in enumerate(result['corrected_data']['questions']):
        original_question = original_data['questions'][i]
        
        # Check for changes in question text
        if question['question_text'] != original_question['question_text']:
            print(f"\nQuestion {i+1}: {question['title']}")
            print(f"  BEFORE: {original_question['question_text'][:100]}...")
            print(f"  AFTER:  {question['question_text'][:100]}...")
        
        # Check for changes in feedback
        if question.get('feedback_correct') != original_question.get('feedback_correct'):
            print(f"\nQuestion {i+1} Feedback:")
            print(f"  BEFORE: {original_question.get('feedback_correct', '')[:100]}...")
            print(f"  AFTER:  {question.get('feedback_correct', '')[:100]}...")
    
    # Show specific pattern examples
    print("\nPattern Examples Found and Corrected:")
    print("-" * 40)
    
    test_examples = [
        ("Original: mutext{m}", "Corrected: \\mu\\text{m}"),
        ("Original: text{V}", "Corrected: \\text{V}"),
        ("Original: gamma", "Corrected: \\gamma"),
        ("Original: phi_F", "Corrected: \\phi_F"),
        ("Original: 0.5,text{V}", "Corrected: 0.5\\,\\text{V}"),
        ("Original: sqrt{2.8}", "Corrected: \\sqrt{2.8}"),
        ("Original: times", "Corrected: \\times"),
        ("Original: approx", "Corrected: \\approx")
    ]
    
    for original, corrected in test_examples:
        print(f"  {original} → {corrected}")
    
    return result

if __name__ == "__main__":
    test_mosfet_corrections()
