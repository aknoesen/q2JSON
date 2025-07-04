"""
LaTeX Auto-Corrector Module for Q2JSON Pipeline
Automatically corrects common LaTeX formatting errors in question data
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple


class LaTeXCorrector:
    """
    LaTeX corrector that automatically fixes common LaTeX formatting errors
    in Q2JSON question data, particularly focusing on mathematical expressions
    and units.
    """
    
    def __init__(self):
        """Initialize the LaTeX corrector with correction patterns"""
        self.correction_patterns = self._initialize_correction_patterns()
        self.correction_stats = {
            'total_corrections': 0,
            'patterns_applied': {},
            'questions_affected': set()
        }
    
    def _initialize_correction_patterns(self) -> List[Tuple[str, str, str]]:
        """
        Initialize regex patterns for LaTeX corrections
        Returns: List of (pattern, replacement, description) tuples
        """
        patterns = [
            # Fix missing backslash before mu for micrometers
            (r'mutext\{([^}]+)\}', r'\\mu\\text{\1}', 'mu prefix correction'),
            
            # Fix missing backslash before text command
            (r'(?<!\\)text\{([^}]+)\}', r'\\text{\1}', 'text command correction'),
            
            # Fix missing backslash before gamma
            (r'(?<!\\)gamma(?![a-zA-Z])', r'\\gamma', 'gamma symbol correction'),
            
            # Fix missing backslash before phi_F
            (r'(?<!\\)phi_F(?![a-zA-Z])', r'\\phi_F', 'phi_F symbol correction'),
            
            # Add proper spacing before units with \, (thin space) - handle numbers with commas
            (r'(\d+(?:\.\d+)?),\\text\{([^}]+)\}', r'\1\\,\\text{\2}', 'comma to thin space correction'),
            
            # Add proper spacing before units with \, (thin space) - handle numbers with spaces
            (r'(\d+(?:\.\d+)?)\s*,\s*\\text\{([^}]+)\}', r'\1\\,\\text{\2}', 'unit spacing correction'),
            
            # Fix sqrt commands that might be missing backslash
            (r'(?<!\\)sqrt\{([^}]+)\}', r'\\sqrt{\1}', 'sqrt command correction'),
            
            # Fix times symbol
            (r'(?<!\\)times(?![a-zA-Z])', r'\\times', 'times symbol correction'),
            
            # Fix approx symbol
            (r'(?<!\\)approx(?![a-zA-Z])', r'\\approx', 'approx symbol correction'),
        ]
        
        return patterns
    
    def correct_latex_in_questions(self, questions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply LaTeX corrections to all questions in the questions data
        
        Args:
            questions_data: Dictionary containing questions array
            
        Returns:
            Dictionary with correction results and corrected data
        """
        # Reset stats for this run
        self.correction_stats = {
            'total_corrections': 0,
            'patterns_applied': {},
            'questions_affected': set()
        }
        
        corrected_data = json.loads(json.dumps(questions_data))  # Deep copy
        
        if 'questions' not in corrected_data:
            return {
                'status': 'error',
                'message': 'No questions array found in data',
                'corrected_data': corrected_data,
                'corrections_made': 0,
                'questions_affected': 0
            }
        
        # Process each question
        for i, question in enumerate(corrected_data['questions']):
            original_question = json.dumps(question)
            
            # Apply corrections to all text fields in the question
            self._correct_question_fields(question, i)
            
            # Check if this question was modified
            if json.dumps(question) != original_question:
                self.correction_stats['questions_affected'].add(i)
        
        return {
            'status': 'completed',
            'corrected_data': corrected_data,
            'corrections_made': self.correction_stats['total_corrections'],
            'questions_affected': len(self.correction_stats['questions_affected']),
            'pattern_stats': dict(self.correction_stats['patterns_applied'])
        }
    
    def _correct_question_fields(self, question: Dict[str, Any], question_index: int) -> None:
        """
        Apply LaTeX corrections to all text fields in a question
        
        Args:
            question: Question dictionary to correct
            question_index: Index of the question for tracking
        """
        # Fields that commonly contain LaTeX
        text_fields = [
            'title',
            'question_text',
            'feedback_correct',
            'feedback_incorrect'
        ]
        
        # Correct main text fields
        for field in text_fields:
            if field in question and isinstance(question[field], str):
                original_text = question[field]
                corrected_text = self._apply_latex_corrections(original_text)
                
                if corrected_text != original_text:
                    question[field] = corrected_text
                    self.correction_stats['questions_affected'].add(question_index)
        
        # Correct choices array
        if 'choices' in question and isinstance(question['choices'], list):
            for i, choice in enumerate(question['choices']):
                if isinstance(choice, str):
                    original_choice = choice
                    corrected_choice = self._apply_latex_corrections(choice)
                    
                    if corrected_choice != original_choice:
                        question['choices'][i] = corrected_choice
                        self.correction_stats['questions_affected'].add(question_index)
        
        # Correct correct_answer field
        if 'correct_answer' in question and isinstance(question['correct_answer'], str):
            original_answer = question['correct_answer']
            corrected_answer = self._apply_latex_corrections(original_answer)
            
            if corrected_answer != original_answer:
                question['correct_answer'] = corrected_answer
                self.correction_stats['questions_affected'].add(question_index)
    
    def _apply_latex_corrections(self, text: str) -> str:
        """
        Apply all LaTeX correction patterns to a text string
        
        Args:
            text: Text to correct
            
        Returns:
            Corrected text
        """
        corrected_text = text
        
        for pattern, replacement, description in self.correction_patterns:
            # Count occurrences before replacement
            matches = re.findall(pattern, corrected_text)
            
            if matches:
                # Apply the correction
                corrected_text = re.sub(pattern, replacement, corrected_text)
                
                # Update statistics
                corrections_made = len(matches)
                self.correction_stats['total_corrections'] += corrections_made
                
                if description not in self.correction_stats['patterns_applied']:
                    self.correction_stats['patterns_applied'][description] = 0
                self.correction_stats['patterns_applied'][description] += corrections_made
        
        return corrected_text
    
    def correct_text_string(self, text: str) -> str:
        """
        Apply LaTeX corrections to a single text string
        
        Args:
            text: Text string to correct
            
        Returns:
            Corrected text string
        """
        return self._apply_latex_corrections(text)
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the last correction run
        
        Returns:
            Dictionary with correction statistics
        """
        return {
            'total_corrections': self.correction_stats['total_corrections'],
            'questions_affected': len(self.correction_stats['questions_affected']),
            'patterns_applied': dict(self.correction_stats['patterns_applied'])
        }
    
    def test_patterns(self, test_strings: List[str]) -> List[Dict[str, str]]:
        """
        Test correction patterns on a list of strings
        
        Args:
            test_strings: List of strings to test
            
        Returns:
            List of dictionaries with original and corrected strings
        """
        results = []
        
        for test_string in test_strings:
            corrected = self._apply_latex_corrections(test_string)
            results.append({
                'original': test_string,
                'corrected': corrected,
                'changed': corrected != test_string
            })
        
        return results


def test_latex_corrector():
    """
    Test function to verify LaTeX corrector functionality
    """
    corrector = LaTeXCorrector()
    
    # Test strings based on MOSFET patterns found
    test_strings = [
        "0.5,mutext{m}",
        "0.4,text{V}",
        "gamma is 0.4",
        "phi_F is 0.8",
        "0.5,text{V}",
        "sqrt{2.8}",
        "5,text{mS}",
        "0.80 times 5,text{mS}",
        "V_T approx 0.812,text{V}"
    ]
    
    print("LaTeX Corrector Test Results:")
    print("=" * 50)
    
    results = corrector.test_patterns(test_strings)
    
    for result in results:
        if result['changed']:
            print(f"✓ {result['original']} → {result['corrected']}")
        else:
            print(f"- {result['original']} (no change)")
    
    print(f"\nTotal corrections made: {corrector.correction_stats['total_corrections']}")
    
    return results


if __name__ == "__main__":
    # Run tests when module is executed directly
    test_latex_corrector()
