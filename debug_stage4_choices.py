#!/usr/bin/env python3
"""
Q2JSON Stage 4 UI Diagnostic Script
Test for missing question choices issue

This script tests the question renderer with MOSFET question data
to verify that choices are properly displayed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extracted_components.question_renderer import Q2JSONQuestionRenderer
from extracted_components.latex_processor import Q2JSONLaTeXProcessor
from extracted_components.editor_framework import Q2JSONEditorFramework
from extracted_components.validation_manager import Q2JSONValidationManager
import json

def test_mosfet_question_rendering():
    """Test MOSFET question rendering with choices field."""
    
    # Create the test question data (from the description)
    test_question = {
        "type": "multiple_choice",
        "title": "MOSFET Drain Current Effects",
        "question_text": "Which of the following effects can cause a reduction in MOSFET drain current?",
        "choices": [
            "Drain-Induced Barrier Lowering (DIBL)",
            "Velocity Saturation", 
            "Hot Electron Effects", 
            "Channel Length Modulation"
        ],
        "correct_answers": [1],  # Velocity Saturation
        "points": 2,
        "feedback_correct": "Correct! Velocity saturation reduces the effective mobility of carriers.",
        "feedback_incorrect": "Think about which effects directly reduce carrier mobility or current."
    }
    
    print("=== Q2JSON STAGE 4 UI DIAGNOSTIC TEST ===")
    print("Testing MOSFET question with 'choices' field...")
    print()
    
    # Test 1: Question Renderer
    print("1. Testing Question Renderer...")
    latex_processor = Q2JSONLaTeXProcessor()
    renderer = Q2JSONQuestionRenderer(latex_processor)
    
    try:
        html_output = renderer.render_question(
            test_question, 
            show_answers=True, 
            show_feedback=True,
            question_number=1
        )
        print("   ✅ Question renderer executed successfully")
        print(f"   📄 HTML output length: {len(html_output)} characters")
        
        # Check if choices were rendered
        if "options absent" in html_output.lower():
            print("   ❌ ERROR: 'options absent' found in output")
        else:
            print("   ✅ No 'options absent' error found")
            
        # Check if all choices are present
        choices_found = 0
        for choice in test_question["choices"]:
            if choice in html_output:
                choices_found += 1
        
        print(f"   📊 Choices found in output: {choices_found}/{len(test_question['choices'])}")
        
        if choices_found == len(test_question["choices"]):
            print("   ✅ All choices successfully rendered")
        else:
            print("   ❌ Some choices missing from rendered output")
            
    except Exception as e:
        print(f"   ❌ Question renderer failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: Editor Framework
    print("2. Testing Editor Framework...")
    validation_manager = Q2JSONValidationManager(latex_processor)
    editor = Q2JSONEditorFramework(latex_processor, renderer, validation_manager)
    
    try:
        # Test the multiple choice editor function
        edited_question = editor._edit_multiple_choice(test_question.copy())
        print("   ✅ Editor framework executed successfully")
        
        # Check if choices were preserved
        if 'options' in edited_question or 'choices' in edited_question:
            print("   ✅ Choices/options preserved in edited question")
        else:
            print("   ❌ No choices/options found in edited question")
            
    except Exception as e:
        print(f"   ❌ Editor framework failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Data Structure Analysis
    print("3. Data Structure Analysis...")
    print(f"   Original question keys: {list(test_question.keys())}")
    print(f"   Has 'choices': {'choices' in test_question}")
    print(f"   Has 'options': {'options' in test_question}")
    print(f"   Number of choices: {len(test_question.get('choices', []))}")
    print(f"   Choice content: {test_question.get('choices', [])}")
    
    print()
    print("=== DIAGNOSTIC COMPLETE ===")

if __name__ == "__main__":
    test_mosfet_question_rendering()
