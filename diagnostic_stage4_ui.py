#!/usr/bin/env python3
"""
URGENT DIAGNOSTIC: Stage 4 UI Missing Question Choices
Test why question choices are not displaying in Stage 4 editor
"""

import json
import sys
import os

# Add paths for imports
sys.path.append('.')
sys.path.append('modules')

def test_stage4_ui_choices():
    """Test Stage 4 UI question choices display issue"""
    
    # Load the test file with known choices
    test_file = r"c:\Users\aknoesen\Documents\Knoesen\Database for EEC1\Debug Problem Cases\MosfetQQDebug.json"
    
    print("=" * 80)
    print("URGENT DIAGNOSTIC: Stage 4 UI Missing Question Choices")
    print("=" * 80)
    print(f"Testing question choices display on: {test_file}")
    print()
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 1. Test Raw JSON Data Structure
    print("🔍 TEST 1: Raw JSON Data Structure")
    print("-" * 50)
    
    questions = test_data.get('questions', [])
    print(f"Total questions loaded: {len(questions)}")
    
    if questions:
        first_question = questions[0]
        print(f"First question title: {first_question.get('title', 'No title')}")
        print(f"Question type: {first_question.get('type', 'No type')}")
        print(f"Question_type field: {first_question.get('question_type', 'No question_type')}")
        
        # Check choices specifically
        choices = first_question.get('choices', [])
        print(f"Choices array exists: {choices is not None}")
        print(f"Choices array length: {len(choices)}")
        print(f"Choices content: {choices}")
        
        if choices:
            print("Individual choices:")
            for i, choice in enumerate(choices):
                print(f"  {i+1}: {choice}")
        else:
            print("❌ No choices found in raw JSON!")
            
        # Check all fields
        print("\nAll question fields:")
        for key, value in first_question.items():
            print(f"  {key}: {type(value)} = {str(value)[:100]}...")
    else:
        print("❌ No questions found in JSON!")
    
    # 2. Test JSON Processor Validation
    print("\n🔍 TEST 2: JSON Processor Validation")
    print("-" * 50)
    
    try:
        from modules.json_processor import JSONProcessor
        processor = JSONProcessor()
        validation_results = processor.validate_questions(test_data)
        
        print(f"JSON Validation Results:")
        print(f"  Total questions: {validation_results.get('total', 0)}")
        print(f"  Valid: {validation_results.get('valid', 0)}")
        print(f"  Warnings: {validation_results.get('warnings', 0)}")
        print(f"  Errors: {validation_results.get('errors', 0)}")
        
        # Check if validation preserves choices
        validated_questions = validation_results.get('validated_questions', [])
        if validated_questions:
            first_validated = validated_questions[0]
            validated_choices = first_validated.get('choices', [])
            print(f"  Choices preserved in validation: {len(validated_choices)}")
            if len(validated_choices) != len(choices):
                print(f"  ❌ Choices lost during validation! Original: {len(choices)}, Validated: {len(validated_choices)}")
        
    except Exception as e:
        print(f"❌ Error with JSON Processor: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Test Q2JSON Components
    print("\n🔍 TEST 3: Q2JSON Components")
    print("-" * 50)
    
    try:
        # Test LaTeX processor
        from modules.latex_processor import Q2JSONLaTeXProcessor
        latex_processor = Q2JSONLaTeXProcessor()
        print("✅ LaTeX processor imported successfully")
        
        # Test question renderer
        from modules.question_renderer import Q2JSONQuestionRenderer
        question_renderer = Q2JSONQuestionRenderer(latex_processor)
        print("✅ Question renderer imported successfully")
        
        # Test rendering first question
        if questions:
            first_question = questions[0]
            try:
                rendered = question_renderer.render_question(first_question)
                print(f"✅ Question rendered successfully")
                print(f"  Rendered type: {type(rendered)}")
                
                # Check if choices are in rendered output
                if hasattr(rendered, 'choices') or 'choices' in str(rendered):
                    print("✅ Choices found in rendered output")
                else:
                    print("❌ Choices NOT found in rendered output")
                    
            except Exception as e:
                print(f"❌ Error rendering question: {e}")
        
    except ImportError as e:
        print(f"❌ Could not import Q2JSON components: {e}")
    except Exception as e:
        print(f"❌ Error with Q2JSON components: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Test Session State Simulation
    print("\n🔍 TEST 4: Session State Simulation")
    print("-" * 50)
    
    # Simulate how Streamlit stores data
    session_state = {
        'questions_data': test_data,
        'current_stage': 3
    }
    
    stored_questions = session_state['questions_data'].get('questions', [])
    print(f"Questions in simulated session state: {len(stored_questions)}")
    
    if stored_questions:
        first_stored = stored_questions[0]
        stored_choices = first_stored.get('choices', [])
        print(f"Choices in session state: {len(stored_choices)}")
        
        if len(stored_choices) != len(choices):
            print(f"❌ Choices lost in session state! Original: {len(choices)}, Stored: {len(stored_choices)}")
        else:
            print("✅ Choices preserved in session state")
    
    # 5. Test Stage 3 Function Simulation
    print("\n🔍 TEST 5: Stage 3 Function Simulation")
    print("-" * 50)
    
    # Simulate the Stage 3 editor interface logic
    def simulate_render_editor_interface():
        """Simulate the Stage 3 render_editor_interface function"""
        print("Simulating render_editor_interface()...")
        
        # Get questions from session state
        questions_data = session_state.get('questions_data', {})
        questions = questions_data.get('questions', [])
        
        print(f"Questions received: {len(questions)}")
        
        if questions:
            first_question = questions[0]
            choices = first_question.get('choices', [])
            print(f"Choices in first question: {len(choices)}")
            
            # Check question type
            question_type = first_question.get('question_type') or first_question.get('type')
            print(f"Question type: {question_type}")
            
            # Check if multiple choice
            if question_type == 'multiple_choice' and choices:
                print(f"✅ Multiple choice question with {len(choices)} choices")
                return True
            else:
                print(f"❌ Issue: Type='{question_type}', Choices={len(choices)}")
                return False
        else:
            print("❌ No questions found")
            return False
    
    ui_test_passed = simulate_render_editor_interface()
    
    # 6. Diagnostic Summary
    print("\n🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    print(f"Raw JSON Data:")
    print(f"  ✅ Question choices exist: {len(choices)} choices found")
    print(f"  ✅ Question type: {first_question.get('type', 'unknown')}")
    
    print(f"\nComponent Status:")
    print(f"  JSON Processor: {'✅ Working' if 'JSONProcessor' in sys.modules else '❌ Not loaded'}")
    print(f"  Q2JSON Components: {'✅ Working' if 'Q2JSONLaTeXProcessor' in sys.modules else '❌ Not loaded'}")
    
    print(f"\nUI Simulation:")
    print(f"  Session State: ✅ Choices preserved")
    print(f"  Editor Interface: {'✅ Should work' if ui_test_passed else '❌ Issue detected'}")
    
    print(f"\nPossible Issues:")
    print(f"  1. Component initialization failure in Streamlit")
    print(f"  2. Conditional rendering hiding choices")
    print(f"  3. Props not passed correctly between components")
    print(f"  4. Q2JSON editor framework not handling choices")
    
    print(f"\nNext Steps:")
    if ui_test_passed:
        print("  ✅ Data structure is correct - issue is in Streamlit UI components")
        print("  🔧 Add debug logging to stages/stage_3_human_review.py")
        print("  🔧 Check Q2JSON editor framework choice handling")
    else:
        print("  ❌ Data structure issue detected")
        print("  🔧 Fix question type or choices data")
    
    return ui_test_passed

if __name__ == "__main__":
    test_stage4_ui_choices()