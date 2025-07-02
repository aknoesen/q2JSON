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

        class TestProcessRawJSON:
            """Comprehensive tests for the process_raw_json method"""
            
            def setup_method(self):
                """Setup for each test method"""
                self.processor = JSONProcessor()
            
            def test_valid_json_direct_parsing(self):
                """Test direct parsing of valid JSON"""
                valid_json = '''
                {
                    "questions": [
                        {
                            "type": "multiple_choice",
                            "title": "Basic Test",
                            "question_text": "What is $2 + 2$?",
                            "choices": ["3", "4", "5", "6"],
                            "correct_answer": "4"
                        }
                    ]
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(valid_json)
                
                assert success == True
                assert data is not None
                assert len(data['questions']) == 1
                assert "Direct JSON parsing successful" in messages[-1]
                assert data['questions'][0]['type'] == 'multiple_choice'
            
            def test_json_with_latex_corrections(self):
                """Test JSON that needs LaTeX auto-corrections"""
                json_with_latex_issues = '''
                {
                    "questions": [
                        {
                            "type": "numerical",
                            "title": "MOSFET Question",
                            "question_text": "Calculate the threshold voltage",
                            "correct_answer": "0.776",
                            "feedback_correct": "Using gamma = 0.4 and phi_F = 0.8, we get 0.776,text{V}"
                        }
                    ]
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(json_with_latex_issues)
                
                assert success == True
                assert data is not None
                # Check that LaTeX corrections were applied
                latex_correction_message = next((msg for msg in messages if "LaTeX corrections" in msg), None)
                assert latex_correction_message is not None
                # Verify the correction was applied
                feedback = data['questions'][0]['feedback_correct']
                assert '\\gamma' in feedback
                assert '\\phi_F' in feedback
                assert '\\,\\text{' in feedback
            
            def test_markdown_wrapped_json(self):
                """Test extraction from markdown code blocks"""
                markdown_json = '''
                Here's the JSON response:
                
                ```json
                {
                    "questions": [
                        {
                            "type": "true_false",
                            "title": "Markdown Test",
                            "question_text": "Is this wrapped in markdown?",
                            "correct_answer": "True"
                        }
                    ]
                }
                ```
                
                End of response.
                '''
                
                success, data, messages = self.processor.process_raw_json(markdown_json)
                
                assert success == True
                assert data is not None
                assert "Preprocessing applied" in messages[0]
                assert data['questions'][0]['title'] == 'Markdown Test'
            
            def test_preprocessing_fixes(self):
                """Test various preprocessing fixes"""
                problematic_json = '''
                # This is a comment that breaks JSON
                {
                    "questions": [
                        {
                            "type": "multiple_choice",
                            "title": "Smart Quotes Test",
                            "question_text": "What about "smart quotes" and \\_underscores?",
                            "choices": ["A", "B", "C", "D"],
                            "correct_answer": "A"
                        }
                    ]
                # Another comment
                '''
                
                success, data, messages = self.processor.process_raw_json(problematic_json)
                
                assert success == True
                assert data is not None
                assert "Preprocessing applied" in messages[0]
                # Verify smart quotes were fixed
                question_text = data['questions'][0]['question_text']
                assert '"smart quotes"' in question_text
                assert '\\_' not in question_text  # Unnecessary escapes removed
            
            def test_unbalanced_braces_repair(self):
                """Test automatic repair of unbalanced braces"""
                unbalanced_json = '''
                {
                    "questions": [
                        {
                            "type": "numerical",
                            "title": "Missing Brace",
                            "question_text": "This JSON is missing closing braces",
                            "correct_answer": "42"
                        }
                    ]
                # Missing closing brace
                '''
                
                success, data, messages = self.processor.process_raw_json(unbalanced_json)
                
                assert success == True
                assert data is not None
                assert "Preprocessing applied" in messages[0]
                assert data['questions'][0]['correct_answer'] == "42"
            
            def test_llm_repair_needed(self):
                """Test scenario requiring LLM-specific repair"""
                chatgpt_problematic = '''
                {
                    "questions": [
                        {
                            "type": "numerical",
                            "title": "Display Math Issue",
                            "question_text": "Calculate frequency",
                            "correct_answer": "2.236",
                            "feedback_correct": "The formula is $$f = \\\\frac{c}{\\\\lambda}$$ which gives us the answer"
                        }
                    ]
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(chatgpt_problematic, "chatgpt")
                
                assert success == True
                assert data is not None
                repair_message = next((msg for msg in messages if "automatically repaired" in msg), None)
                assert repair_message is not None
                # Verify display math was handled
                feedback = data['questions'][0]['feedback_correct']
                assert '$$' not in feedback or '[Mathematical Formula]' in feedback
            
            def test_invalid_json_structure(self):
                """Test handling of valid JSON but wrong structure"""
                wrong_structure = '''
                {
                    "data": [
                        {
                            "type": "multiple_choice",
                            "title": "Wrong Root Key",
                            "question_text": "This is not under 'questions' key"
                        }
                    ]
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(wrong_structure)
                
                assert success == False
                assert data is None
                assert "missing 'questions' array" in " ".join(messages)
            
            def test_empty_questions_array(self):
                """Test handling of empty questions array"""
                empty_questions = '''
                {
                    "questions": []
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(empty_questions)
                
                assert success == False
                assert data is None
                assert "missing 'questions' array" in " ".join(messages)
            
            def test_completely_malformed_json(self):
                """Test handling of completely broken JSON"""
                malformed_json = '''
                {
                    "questions": [
                        {
                            "type": "multiple_choice"
                            "missing": "comma here will break everything"
                            "also": "no closing brace"
                '''
                
                success, data, messages = self.processor.process_raw_json(malformed_json)
                
                assert success == False
                assert data is None
                assert "JSON parsing error" in messages[1]  # After preprocessing message
                assert "Auto-repair failed" in " ".join(messages)
            
            def test_repair_function_exception(self):
                """Test handling when repair function itself throws exception"""
                # Create a mock scenario that might cause repair function to fail
                problematic_json = '''
                {
                    "questions": [
                        {
                            "type": "multiple_choice",
                            "title": null,
                            "question_text": undefined,
                            "choices": [1, 2, 3, true],
                            "correct_answer": function() { return "invalid"; }
                        }
                    ]
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(problematic_json, "unknown_llm")
                
                assert success == False
                assert data is None
                # Should handle repair function exceptions gracefully
                assert any("error" in msg.lower() for msg in messages)
            
            def test_preprocessing_with_multiple_issues(self):
                """Test preprocessing handling multiple issues at once"""
                complex_problematic = '''
                # Comment at start
                Here's some text before JSON:
                
                ```json
                {
                    "questions": [
                        {
                            "type": "numerical",
                            "title": "Complex Issues Test",
                            "question_text": "Calculate the "voltage" with μ = 5 and γ = 0.4",
                            "correct_answer": "3.14",
                            "feedback_correct": "Using the formula gamma(sqrt{phi_F}) = 0.776,text{V}"
                        }
                    # Missing closing braces
                ```
                
                # Comment at end
                '''
                
                success, data, messages = self.processor.process_raw_json(complex_problematic)
                
                assert success == True
                assert data is not None
                assert "Preprocessing applied" in messages[0]
                
                # Verify multiple fixes were applied
                question = data['questions'][0]
                assert '"voltage"' in question['question_text']  # Smart quotes fixed
                assert '\\gamma' in question['feedback_correct']  # Greek letters escaped
                assert '\\,\\text{' in question['feedback_correct']  # Comma-text pattern fixed
            
            def test_latex_correction_comprehensive(self):
                """Test comprehensive LaTeX correction scenarios"""
                latex_heavy_json = '''
                {
                    "questions": [
                        {
                            "type": "numerical",
                            "title": "Heavy LaTeX Test",
                            "question_text": "Calculate using gamma, phi_F, and sqrt{x}",
                            "correct_answer": "1.414",
                            "feedback_correct": "Using \\\\gamma = 0.4, \\\\phi_F = 0.8, we get sqrt{2} approx 1.414,text{units}. Also 5 mutext{A} and 10 ohmtext{resistance}.",
                            "choices": ["1.414", "1.732", "2.000", "2.236"]
                        }
                    ]
                }
                '''
                
                success, data, messages = self.processor.process_raw_json(latex_heavy_json)
                
                assert success == True
                assert data is not None
                
                # Verify LaTeX corrections
                question = data['questions'][0]
                assert '\\gamma' in question['question_text']
                assert '\\phi_F' in question['question_text']
                assert '\\sqrt{' in question['question_text']
                
                feedback = question['feedback_correct']
                assert '\\\\gamma' not in feedback  # Double backslashes removed
                assert '\\gamma' in feedback
                assert '\\,\\mu\\text{' in feedback  # mutext corrected
                assert '\\,\\Omega\\text{' in feedback  # ohmtext corrected
                assert '\\,\\text{' in feedback  # comma-text corrected
            
            def test_processing_summary_tracking(self):
                """Test that processing attempts are properly tracked"""
                test_json = '''
                {
                    "questions": [
                        {
                            "type": "multiple_choice",
                            "title": "Summary Test",
                            "question_text": "Test tracking",
                            "choices": ["A", "B", "C", "D"],
                            "correct_answer": "A"
                        }
                    ]
                }
                '''
                
                # Process successfully
                success, data, messages = self.processor.process_raw_json(test_json)
                
                assert success == True
                
                # Check summary tracking
                summary = self.processor.get_processing_summary()
                assert 'repair_attempts' in summary
                assert 'validation_results' in summary
                assert 'processing_log' in summary
            
            def test_auto_llm_type_detection(self):
                """Test automatic LLM type detection and appropriate repair"""
                chatgpt_style = '''
                {
                    "questions": [
                        {
                            "type": "numerical",
                            "title": "ChatGPT Style",
                            "question_text": "Calculate this",
                            "correct_answer": "1.0",
                            "feedback_correct": "The answer uses $$\\\\frac{a}{b}$$ formula"
                        }
                    ]
                }
                '''
                
                # Use "auto" to trigger detection
                success, data, messages = self.processor.process_raw_json(chatgpt_style, "auto")
                
                assert success == True
                assert data is not None
                # Should detect and repair ChatGPT-style issues
                feedback = data['questions'][0]['feedback_correct']
                assert '\\\\frac' not in feedback  # Double backslashes should be fixed

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