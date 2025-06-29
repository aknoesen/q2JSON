"""
Direct testing framework for JSON processing logic
Run Stage 3 functionality in isolation for rapid iteration
"""

import pytest
import json
import os
from pathlib import Path
import sys

# Add modules to path for testing
sys.path.append(str(Path(__file__).parent.parent))

from modules.json_processor import JSONProcessor
from modules.llm_repairs import repair_chatgpt_response, detect_llm_type


class TestJSONProcessor:
    """Test the core JSON processing functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.processor = JSONProcessor()
    
    def test_basic_functionality(self):
        """Test basic JSON processing with valid input"""
        valid_json = '''
        {
            "questions": [
                {
                    "type": "multiple_choice",
                    "title": "Test Question",
                    "question_text": "What is 2+2?",
                    "choices": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "points": 1,
                    "tolerance": 0.05,
                    "feedback_correct": "Correct!",
                    "feedback_incorrect": "Try again",
                    "image_file": [],
                    "topic": "Math",
                    "subtopic": "Addition",
                    "difficulty": "Easy"
                }
            ]
        }
        '''
        
        success, data, messages = self.processor.process_raw_json(valid_json)
        
        assert success == True
        assert data is not None
        assert len(data['questions']) == 1
        assert "Direct JSON parsing successful" in messages[0]
    
    def test_chatgpt_display_math_repair(self):
        """Test ChatGPT display math repair"""
        chatgpt_response = '''
        {
            "questions": [
                {
                    "type": "numerical",
                    "title": "Frequency Calculation",
                    "question_text": "Calculate the frequency",
                    "choices": [],
                    "correct_answer": "2.236",
                    "points": 2,
                    "tolerance": 0.05,
                    "feedback_correct": "Correct! The resonant frequency is calculated as follows: $$f_r = \\\\frac{3 \\\\times 10^8}{2 \\\\times 0.03 \\\\times \\\\sqrt{4.5}} \\\\approx 2.236 \\\\times 10^9\\\\,\\\\text{Hz} = 2.236\\\\,\\\\text{GHz}$$.",
                    "feedback_incorrect": "Check your calculation",
                    "image_file": [],
                    "topic": "Antennas",
                    "subtopic": "Frequency",
                    "difficulty": "Medium"
                }
            ]
        }
        '''
        
        success, data, messages = self.processor.process_raw_json(chatgpt_response, "chatgpt")
        
        assert success == True, f"Processing failed: {messages}"
        assert data is not None
        assert len(data['questions']) == 1
        assert "automatically repaired" in " ".join(messages)
    
    def test_invalid_json_structure(self):
        """Test handling of JSON without questions array"""
        invalid_structure = '''
        {
            "type": "multiple_choice",
            "title": "Single Question",
            "question_text": "This is not in a questions array"
        }
        '''
        
        success, data, messages = self.processor.process_raw_json(invalid_structure)
        
        assert success == False
        assert data is None
        assert "missing 'questions' array" in " ".join(messages)
    
    def test_completely_broken_json(self):
        """Test handling of completely malformed JSON"""
        broken_json = '''
        {
            "questions": [
                {
                    "type": "multiple_choice"
                    "missing_comma": "this will break"
                }
            }
        '''
        
        success, data, messages = self.processor.process_raw_json(broken_json)
        
        assert success == False
        assert data is None
        assert "JSON parsing error" in messages[0]
        assert "Auto-repair failed" in " ".join(messages)
    
    def test_question_validation(self):
        """Test question validation functionality"""
        test_data = {
            "questions": [
                {
                    "type": "multiple_choice",
                    "title": "Good Question",
                    "question_text": "What is this?",
                    "choices": ["A", "B", "C", "D"],
                    "correct_answer": "A"
                },
                {
                    "type": "multiple_choice",
                    "title": "Bad Question",
                    # Missing question_text
                    "choices": ["A", "B"]  # Wrong number of choices
                }
            ]
        }
        
        results = self.processor.validate_questions(test_data)
        
        assert results['total'] == 2
        assert results['valid'] == 1
        assert results['errors'] == 1
        assert len(results['question_analysis']) == 2
    
    def test_export_functionality(self):
        """Test JSON export in different formats"""
        test_data = {
            "questions": [
                {
                    "type": "true_false",
                    "title": "Test",
                    "question_text": "Is this a test?",
                    "correct_answer": "True"
                }
            ]
        }
        
        # Test different export formats
        standard = self.processor.export_json(test_data, "standard")
        compact = self.processor.export_json(test_data, "compact")
        pretty = self.processor.export_json(test_data, "pretty")
        
        # All should be valid JSON
        assert json.loads(standard)
        assert json.loads(compact)
        assert json.loads(pretty)
        
        # Compact should be shorter
        assert len(compact) < len(standard) < len(pretty)


class TestLLMRepairs:
    """Test LLM-specific repair functions"""
    
    def test_chatgpt_latex_repair(self):
        """Test ChatGPT LaTeX repair specifically"""
        problematic_json = '''
        {
            "questions": [
                {
                    "feedback_correct": "The formula is $$f = \\\\frac{c}{2L\\\\sqrt{\\\\varepsilon}}$$"
                }
            ]
        }
        '''
        
        repaired = repair_chatgpt_response(problematic_json)
        
        # Should not contain double backslashes or complex display math
        assert '\\\\frac' not in repaired
        assert '$$' not in repaired or '[Mathematical Formula]' in repaired
    
    def test_llm_detection(self):
        """Test automatic LLM type detection"""
        chatgpt_response = 'Some text with $$\\frac{1}{2}$$ math'
        claude_response = 'Some text about PowerShell preferences'
        copilot_response = 'I cannot provide that information due to safety'
        
        assert detect_llm_type(chatgpt_response) == 'chatgpt'
        assert detect_llm_type(claude_response) == 'claude'
        assert detect_llm_type(copilot_response) == 'copilot'


def run_manual_test_with_file(filepath: str):
    """
    Manual test function to process a specific JSON file
    Useful for testing with real LLM responses
    """
    processor = JSONProcessor()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Testing file: {filepath}")
        print(f"Content length: {len(content)} characters")
        
        success, data, messages = processor.process_raw_json(content, "chatgpt")
        
        print(f"Success: {success}")
        print("Messages:")
        for msg in messages:
            print(f"  - {msg}")
        
        if success and data:
            print(f"Questions loaded: {len(data['questions'])}")
            
            # Run validation
            validation = processor.validate_questions(data)
            print(f"Validation: {validation['valid']}/{validation['total']} valid")
            
            # Show export
            exported = processor.export_json(data)
            print(f"Export ready: {len(exported)} characters")
        
        return success, data, messages
        
    except Exception as e:
        print(f"Error: {e}")
        return False, None, [str(e)]


if __name__ == "__main__":
    # Run basic tests
    print("Running basic JSON processor tests...")
    
    # Example manual test with current ChatGPT response
    # Uncomment and modify path as needed:
    # run_manual_test_with_file("test_data/chatgpt_current_response.json")