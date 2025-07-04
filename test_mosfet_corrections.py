"""
Test LaTeX Corrector on MosfetQQDebug.json
Shows before/after corrections for the actual test file
"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from latex_corrector import LaTeXCorrector

def test_mosfet_file():
    """Test the LaTeX corrector on the actual MOSFET test file"""
    
    corrector = LaTeXCorrector()
    
    # Load the original MOSFET test data
    print("Loading MosfetQQDebug.json...")
    with open('test_data/MosfetQQDebug.json', 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"Found {len(original_data['questions'])} questions")
    print()
    
    # Apply corrections
    print("Applying LaTeX corrections...")
    results = corrector.correct_latex_in_questions(original_data)
    
    print("=" * 80)
    print("LATEX CORRECTION RESULTS")
    print("=" * 80)
    print(f"Status: {results['status']}")
    print(f"Total corrections made: {results['corrections_made']}")
    print(f"Questions affected: {results['questions_affected']}")
    print()
    
    # Show pattern statistics
    print("Pattern Statistics:")
    print("-" * 40)
    for pattern, count in results['pattern_stats'].items():
        print(f"  {pattern}: {count} corrections")
    print()
    
    # Show specific corrections made
    corrected_data = results['corrected_data']
    original_questions = original_data['questions']
    corrected_questions = corrected_data['questions']
    
    corrections_found = []
    
    for i, (orig_q, corr_q) in enumerate(zip(original_questions, corrected_questions)):
        question_corrections = []
        
        # Check each field for changes
        fields_to_check = ['title', 'question_text', 'feedback_correct', 'feedback_incorrect']
        
        for field in fields_to_check:
            if field in orig_q and field in corr_q:
                orig_text = orig_q[field]
                corr_text = corr_q[field]
                
                if orig_text != corr_text:
                    question_corrections.append({
                        'field': field,
                        'original': orig_text,
                        'corrected': corr_text
                    })
        
        if question_corrections:
            corrections_found.append({
                'question_index': i,
                'title': orig_q.get('title', f'Question {i+1}'),
                'corrections': question_corrections
            })
    
    # Display corrections
    print("DETAILED CORRECTIONS:")
    print("=" * 80)
    
    for correction_info in corrections_found:
        print(f"\n📝 Question {correction_info['question_index'] + 1}: {correction_info['title']}")
        print("-" * 60)
        
        for correction in correction_info['corrections']:
            print(f"\n🔧 Field: {correction['field']}")
            print(f"   BEFORE: {correction['original'][:100]}...")
            print(f"   AFTER:  {correction['corrected'][:100]}...")
            
            # Show specific changes
            orig_text = correction['original']
            corr_text = correction['corrected']
            
            # Find some specific pattern changes
            changes = []
            if 'mutext{' in orig_text and '\\mu\\text{' in corr_text:
                changes.append('mutext{} → \\mu\\text{}')
            if ',text{' in orig_text and '\\,\\text{' in corr_text:
                changes.append(',text{} → \\,\\text{}')
            if 'gamma(' in orig_text and '\\gamma(' in corr_text:
                changes.append('gamma → \\gamma')
            if 'phi_F' in orig_text and '\\phi_F' in corr_text:
                changes.append('phi_F → \\phi_F')
            if 'sqrt{' in orig_text and '\\sqrt{' in corr_text:
                changes.append('sqrt{} → \\sqrt{}')
            if 'times' in orig_text and '\\times' in corr_text:
                changes.append('times → \\times')
            if 'approx' in orig_text and '\\approx' in corr_text:
                changes.append('approx → \\approx')
            
            if changes:
                print(f"   CHANGES: {', '.join(changes)}")
    
    # Show summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully processed {len(original_data['questions'])} questions")
    print(f"✅ Made {results['corrections_made']} total corrections")
    print(f"✅ Affected {results['questions_affected']} questions")
    print(f"✅ Most common issues fixed:")
    
    for pattern, count in sorted(results['pattern_stats'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {pattern}: {count} fixes")
    
    return results

if __name__ == "__main__":
    test_mosfet_file()
