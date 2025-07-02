"""
Enhanced LaTeX Correction Debug Test
Analyzes real-world patterns from MosfetCornerCasePhase2.json
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.json_processor import JSONProcessor
import json

def test_real_world_patterns():
    """Test with actual problematic patterns from the MOSFET file"""
    processor = JSONProcessor()
    
    print("=== Real-World LaTeX Pattern Analysis ===\n")
    
    # Test cases from actual file
    real_patterns = [
        # 1. Comma-text patterns (MISSING from current implementation)
        ("$0.5,text{V}$", "$0.5\\,\\text{V}$", "Comma-text spacing"),
        ("$0.4,text{V}^{1/2}$", "$0.4\\,\\text{V}^{1/2}$", "Comma-text with exponent"),
        ("$0.8,text{V}$", "$0.8\\,\\text{V}$", "Basic comma-text"),
        ("$5,text{mS}$", "$5\\,\\text{mS}$", "Comma-text with units"),
        
        # 2. Unescaped Greek letters (MISSING from current implementation)
        ("$gamma$", "$\\gamma$", "Unescaped gamma"),
        ("gamma(sqrt{2phi_F + V_{SB}}", "\\gamma(\\sqrt{2\\phi_F + V_{SB}}", "Complex gamma-phi"),
        ("$2phi_F$", "$2\\phi_F$", "Unescaped phi with subscript"),
        ("phi_F", "\\phi_F", "Bare phi"),
        
        # 3. Mathematical operators (MISSING)
        ("times", "\\times", "Unescaped times"),
        ("sqrt{2phi_F}", "\\sqrt{2\\phi_F}", "Unescaped sqrt with phi"),
        ("approx", "\\approx", "Unescaped approx"),
        
        # 4. Existing patterns (should work)
        ("\\\\mu", "\\mu", "Double backslash mu"),
        ("5μ", "$5\\,\\mu$", "Unicode mu"),
        ("mutext{F}", "\\mu\\text{F}", "mutext pattern"),
    ]
    
    print("Testing individual patterns:")
    print("-" * 60)
    
    failed_patterns = []
    for i, (input_text, expected, description) in enumerate(real_patterns, 1):
        corrected, corrections = processor._latex_auto_correct(input_text)
        
        success = expected in corrected or corrected == expected
        status = "✅ PASS" if success else "❌ FAIL"
        
        print(f"{i:2}. {description:<30} {status}")
        print(f"    Input:    '{input_text}'")
        print(f"    Expected: '{expected}'")
        print(f"    Got:      '{corrected}'")
        print(f"    Corrections: {corrections}")
        print()
        
        if not success:
            failed_patterns.append((description, input_text, expected, corrected))
    
    # Test with actual JSON content
    print("=== Testing with Real JSON Content ===\n")
    
    # Problematic question text from the file
    problematic_text = "A MOSFET has a threshold voltage ($V_{T0}$) of $0.5,text{V}$ when $V_{SB} = 0,text{V}$. If the body effect coefficient ($gamma$) is $0.4,text{V}^{1/2}$, the surface potential at strong inversion ($2phi_F$) is $0.8,text{V}$, and the source-to-body voltage ($V_{SB}$) is $2,text{V}$, calculate the new threshold voltage ($V_T$). Use the formula: $V_T = V_{T0} + gamma(sqrt{2phi_F + V_{SB}} - sqrt{2phi_F})$."
    
    print("Original problematic text:")
    print(f"'{problematic_text}'\n")
    
    corrected_text, corrections = processor._latex_auto_correct(problematic_text)
    
    print("After correction:")
    print(f"'{corrected_text}'\n")
    
    print(f"Corrections applied: {len(corrections)}")
    for correction in corrections:
        print(f"  - {correction}")
    
    # Check specific issues
    print("\n=== Specific Issue Analysis ===")
    issues_found = []
    
    if ",text{" in corrected_text:
        issues_found.append("❌ Comma-text patterns still present")
    else:
        print("✅ Comma-text patterns fixed")
    
    if "gamma" in corrected_text and "\\gamma" not in corrected_text:
        issues_found.append("❌ Unescaped gamma still present")
    else:
        print("✅ Gamma properly escaped")
    
    if "phi_F" in corrected_text and "\\phi_F" not in corrected_text:
        issues_found.append("❌ Unescaped phi still present")
    else:
        print("✅ Phi properly escaped")
    
    if "sqrt{" in corrected_text and "\\sqrt{" not in corrected_text:
        issues_found.append("❌ Unescaped sqrt still present")
    else:
        print("✅ Sqrt properly escaped")
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Failed individual patterns: {len(failed_patterns)}")
    print(f"Critical issues found: {len(issues_found)}")
    
    if failed_patterns:
        print("\nFailed patterns:")
        for description, input_text, expected, got in failed_patterns:
            print(f"  - {description}: '{input_text}' → expected '{expected}', got '{got}'")
    
    if issues_found:
        print("\nCritical issues:")
        for issue in issues_found:
            print(f"  {issue}")
    
    return len(failed_patterns) == 0 and len(issues_found) == 0

if __name__ == '__main__':
    success = test_real_world_patterns()
    if success:
        print("\n🎉 All real-world patterns handled correctly!")
    else:
        print("\n🚨 Critical patterns missing - implementation needs enhancement!")
