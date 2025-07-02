"""
Test the integrated Q2JSON pipeline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import Q2JSONPipeline
import json
import tempfile


def test_integration():
    """Test the complete integrated pipeline"""
    
    print("🧪 TESTING INTEGRATED Q2JSON PIPELINE")
    print("=" * 50)
    
    # Test 1: Basic functionality
    print(f"\n🧪 Test 1: Basic Pipeline")
    
    # Create test data with a known contradiction
    test_data = {
        "questions": [
            {
                "correct_answer": "0.776",
                "feedback_correct": "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
            },
            {
                "correct_answer": "0.812",
                "feedback_correct": "V_T = 0.8116 V. Rounding to three decimal places: V_T ≈ 0.812 V."
            }
        ]
    }
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_input:
        json.dump(test_data, temp_input, indent=2)
        temp_input_path = temp_input.name
    
    try:
        # Test the pipeline
        pipeline = Q2JSONPipeline()
        
        results = pipeline.process_file(
            input_file=temp_input_path,
            output_file=None,  # Don't save output for test
            check_math=True,
            fix_latex=False,  # Skip LaTeX for this test
            verbose=True
        )
        
        # Verify results
        print(f"\n✅ Pipeline Status: {results['status']}")
        
        math_results = results['mathematical_validation']
        print(f"📊 Math Validation: {math_results.get('status', 'unknown')}")
        
        if math_results.get('total_contradictions', 0) > 0:
            print(f"🚨 Found {math_results['total_contradictions']} contradictions (expected)")
        else:
            print(f"✅ No contradictions found")
    
    finally:
        # Clean up
        if os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
    
    # Test 2: MOSFET file (if available)
    print(f"\n🧪 Test 2: Real MOSFET File")
    
    mosfet_file = "c:/Users/aknoesen/Downloads/MosfetCornerCasePhase2.json"
    
    if os.path.exists(mosfet_file):
        print(f"📁 Processing: {mosfet_file}")
        
        results = pipeline.process_file(
            input_file=mosfet_file,
            output_file=None,
            check_math=True,
            fix_latex=False,
            verbose=False  # Quiet for real file test
        )
        
        print(f"✅ MOSFET file processed: {results['status']}")
        
        math_results = results['mathematical_validation']
        print(f"📊 Contradictions found: {math_results.get('total_contradictions', 0)}")
    
    else:
        print(f"⏭️ MOSFET file not found - skipping")
    
    print(f"\n🎯 INTEGRATION TEST COMPLETED")


if __name__ == "__main__":
    test_integration()