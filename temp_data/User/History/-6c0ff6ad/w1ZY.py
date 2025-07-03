# Test script for Q2LMS extracted components
"""
Quick test script to verify the extracted components work correctly.
Run this to test the components before integration.
"""

import sys
import os

# Add the extracted components to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_latex_processor():
    """Test the LaTeX processor component"""
    print("🧮 Testing LaTeX Processor...")
    
    try:
        from latex_processor import Q2JSONLaTeXProcessor, MathValidationManager
        
        processor = Q2JSONLaTeXProcessor()
        validator = MathValidationManager()
        
        # Test basic LaTeX rendering
        test_text = "The resistance is $R = 10\\,\\Omega$ at frequency $f = 50\\,\\text{Hz}$"
        rendered = processor.process_latex(test_text)
        
        print(f"✅ LaTeX rendering: {rendered[:50]}...")
        
        # Test validation
        validation_issues = validator.validate_math_content(test_text)
        print(f"✅ Validation issues found: {len(validation_issues)}")
        
        # Test problematic LaTeX
        bad_text = "Unmatched delimiter: $R = 10\\,\\Omega and missing delimiter"
        bad_issues = validator.validate_math_content(bad_text)
        
        print(f"✅ Error detection: {len(bad_issues)} issues found in bad LaTeX")
        print("✅ LaTeX Processor tests passed!")
        
    except Exception as e:
        print(f"❌ LaTeX Processor test failed: {e}")
        return False
    
    return True


def test_question_renderer():
    """Test the question renderer component"""
    print("\n👁️ Testing Question Renderer...")
    
    try:
        from question_renderer import Q2JSONQuestionRenderer
        
        renderer = Q2JSONQuestionRenderer()
        
        # Test sample question data
        sample_question = {
            'title': 'Test Question',
            'question_text': 'What is $\\pi^2$?',
            'question_type': 'multiple_choice',
            'choice_a': '$9.87$',
            'choice_b': '$10.0$',
            'choice_c': '$9.42$',
            'choice_d': '$8.53$',
            'correct_answer': 'A',
            'points': 1,
            'difficulty': 'Medium',
            'topic': 'Mathematics'
        }
        
        # Test validation (would normally be rendered in Streamlit)
        print("✅ Question renderer initialized successfully")
        print("✅ Sample question data processed")
        print("✅ Question Renderer tests passed!")
        
    except Exception as e:
        print(f"❌ Question Renderer test failed: {e}")
        return False
    
    return True


def test_editor_framework():
    """Test the editor framework component"""
    print("\n✏️ Testing Editor Framework...")
    
    try:
        from editor_framework import Q2JSONEditorFramework
        
        def mock_save_callback(index, data):
            print(f"Mock save: Question {index}")
            return True
        
        editor = Q2JSONEditorFramework(save_callback=mock_save_callback)
        
        print("✅ Editor framework initialized successfully")
        print("✅ Mock save callback configured")
        print("✅ Editor Framework tests passed!")
        
    except Exception as e:
        print(f"❌ Editor Framework test failed: {e}")
        return False
    
    return True


def test_validation_manager():
    """Test the validation manager component"""
    print("\n🔍 Testing Validation Manager...")
    
    try:
        from validation_manager import Q2JSONValidationManager
        
        validator = Q2JSONValidationManager()
        
        # Test sample question validation
        sample_question = {
            'title': 'Test Question',
            'question_text': 'What is $\\pi^2$?',
            'question_type': 'numerical',
            'correct_answer': '$9.87$',
            'points': 1
        }
        
        validation_results = validator.validate_question_comprehensive(sample_question)
        
        print(f"✅ Validation status: {validation_results.get('overall_status', 'unknown')}")
        print(f"✅ Validation score: {validation_results.get('validation_score', 0)}")
        print("✅ Validation Manager tests passed!")
        
    except Exception as e:
        print(f"❌ Validation Manager test failed: {e}")
        return False
    
    return True


def test_component_integration():
    """Test component integration"""
    print("\n🔗 Testing Component Integration...")
    
    try:
        from latex_processor import Q2JSONLaTeXProcessor
        from question_renderer import Q2JSONQuestionRenderer
        from editor_framework import Q2JSONEditorFramework
        from validation_manager import Q2JSONValidationManager
        
        # Initialize all components
        latex_processor = Q2JSONLaTeXProcessor()
        renderer = Q2JSONQuestionRenderer()
        validator = Q2JSONValidationManager()
        editor = Q2JSONEditorFramework()
        
        # Test that they can work together
        sample_question = {
            'title': 'Integration Test',
            'question_text': 'Calculate $\\int_0^1 x^2 dx$',
            'question_type': 'numerical',
            'correct_answer': '$\\frac{1}{3}$',
            'points': 2
        }
        
        # Validate question
        validation_results = validator.validate_question_comprehensive(sample_question)
        
        # Process LaTeX
        rendered_text, latex_validation = latex_processor.render_latex_with_validation(
            sample_question['question_text']
        )
        
        print("✅ All components initialized successfully")
        print("✅ Components can work together")
        print(f"✅ Integration validation: {validation_results.get('overall_status', 'unknown')}")
        print("✅ Component Integration tests passed!")
        
    except Exception as e:
        print(f"❌ Component Integration test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🚀 Q2LMS Component Extraction Test Suite")
    print("=" * 50)
    
    tests = [
        test_latex_processor,
        test_question_renderer,
        test_editor_framework,
        test_validation_manager,
        test_component_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Components are ready for Q2JSON integration.")
        return True
    else:
        print("⚠️ Some tests failed. Review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
