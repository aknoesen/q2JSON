"""
Core JSON processing and validation logic (Stage 3)
Extracted from main app for direct testing and iteration
"""

import json
import re
import time
from typing import Dict, List, Tuple, Optional, Any
from .llm_repairs import get_repair_function


class JSONProcessor:
    """
    Core JSON processing logic equivalent to Stage 3 functionality
    Handles parsing, validation, repair, and export of educational questions
    """
    
    def __init__(self):
        self.repair_attempts = []
        self.validation_results = {}
        self.processing_log = []
    
    def process_raw_json(self, raw_json: str, llm_type: str = "auto") -> Tuple[bool, Optional[Dict], List[str]]:
        """
        Main processing function - equivalent to Stage 3 logic
        
        Args:
            raw_json: Raw JSON string from LLM response
            llm_type: LLM type for specific repair strategy ("chatgpt", "claude", etc.)
            
        Returns:
            Tuple of (success: bool, questions_data: dict or None, messages: list)
        """
        messages = []
        
        # Step 1: Try direct parsing first
        try:
            questions_data = json.loads(raw_json)
            
            if self._validate_questions_structure(questions_data):
                messages.append("✅ Direct JSON parsing successful")
                return True, questions_data, messages
            else:
                messages.append("❌ Valid JSON but missing 'questions' array")
                return False, None, messages
                
        except json.JSONDecodeError as e:
            messages.append(f"❌ JSON parsing error: {str(e)}")
        
        # Step 2: Attempt automatic repair
        messages.append("🔧 Attempting automatic repair...")
        
        try:
            repaired_json = self.auto_repair_json(raw_json, llm_type)
            questions_data = json.loads(repaired_json)
            
            if self._validate_questions_structure(questions_data):
                messages.append("✅ JSON automatically repaired!")
                return True, questions_data, messages
            else:
                messages.append("❌ Repaired JSON missing 'questions' array")
                return False, None, messages
                
        except json.JSONDecodeError as e2:
            messages.append(f"❌ Auto-repair failed: {str(e2)}")
            return False, None, messages
        except Exception as e3:
            messages.append(f"❌ Repair function error: {str(e3)}")
            return False, None, messages
    
    def auto_repair_json(self, raw_json: str, llm_type: str = "auto") -> str:
        """
        Attempt automatic JSON repair using LLM-specific strategies
        
        Args:
            raw_json: Raw JSON string to repair
            llm_type: LLM type for specific repair strategy
            
        Returns:
            Repaired JSON string
        """
        # Get appropriate repair function
        repair_func = get_repair_function(llm_type)
        
        # Apply repair
        repaired = repair_func(raw_json)
        
        # Log repair attempt
        self.repair_attempts.append({
            'llm_type': llm_type,
            'original_length': len(raw_json),
            'repaired_length': len(repaired),
            'changes_made': len(raw_json) != len(repaired)
        })
        
        return repaired
    
    def _validate_questions_structure(self, questions_data: Dict) -> bool:
        """
        Validate that JSON has proper questions array structure
        
        Args:
            questions_data: Parsed JSON data
            
        Returns:
            True if valid structure, False otherwise
        """
        if not isinstance(questions_data, dict):
            return False
            
        if 'questions' not in questions_data:
            return False
            
        if not isinstance(questions_data['questions'], list):
            return False
            
        if len(questions_data['questions']) == 0:
            return False
            
        return True
    
    def validate_questions(self, questions_data: Dict) -> Dict:
        """
        Comprehensive validation of question content and structure
        
        Args:
            questions_data: Parsed questions data
            
        Returns:
            Dictionary with validation results
        """
        questions = questions_data.get('questions', [])
        
        validation_results = {
            'total': len(questions),
            'valid': 0,
            'warnings': 0,
            'errors': 0,
            'issues': [],
            'question_analysis': []
        }
        
        required_fields = ['type', 'title', 'question_text']
        
        for i, question in enumerate(questions):
            q_analysis = {
                'index': i + 1,
                'title': question.get('title', f'Question {i+1}'),
                'type': question.get('type', 'unknown'),
                'status': 'valid',
                'issues': []
            }
            
            # Check required fields
            for field in required_fields:
                if field not in question or not question[field]:
                    q_analysis['issues'].append(f"Missing {field}")
                    q_analysis['status'] = 'error'
            
            # Validate question type specific requirements
            q_type = question.get('type')
            if q_type == 'multiple_choice':
                if 'choices' not in question:
                    q_analysis['issues'].append("Missing choices array")
                    q_analysis['status'] = 'error'
                elif len(question.get('choices', [])) != 4:
                    q_analysis['issues'].append(f"Expected 4 choices, found {len(question.get('choices', []))}")
                    q_analysis['status'] = 'warning'
            
            elif q_type == 'numerical':
                if 'correct_answer' in question:
                    try:
                        float(str(question['correct_answer']))
                    except (ValueError, TypeError):
                        q_analysis['issues'].append("Correct answer is not numeric")
                        q_analysis['status'] = 'error'
            
            elif q_type == 'true_false':
                if 'correct_answer' in question:
                    if str(question['correct_answer']).lower() not in ['true', 'false']:
                        q_analysis['issues'].append("Correct answer must be 'True' or 'False'")
                        q_analysis['status'] = 'error'
            
            # Count status
            if q_analysis['status'] == 'valid':
                validation_results['valid'] += 1
            elif q_analysis['status'] == 'warning':
                validation_results['warnings'] += 1
            else:
                validation_results['errors'] += 1
            
            validation_results['question_analysis'].append(q_analysis)
        
        self.validation_results = validation_results
        return validation_results
    
    def export_json(self, questions_data: Dict, format_type: str = "standard", 
                   filename_prefix: str = "q2json_questions") -> str:
        """
        Export validated questions in specified format
        
        Args:
            questions_data: Validated questions data
            format_type: Export format ("standard", "compact", "pretty")
            filename_prefix: Prefix for filename generation
            
        Returns:
            JSON string ready for download/export
        """
        if format_type == "compact":
            return json.dumps(questions_data, separators=(',', ':'), ensure_ascii=False)
        elif format_type == "pretty":
            return json.dumps(questions_data, indent=4, ensure_ascii=False)
        else:  # standard
            return json.dumps(questions_data, indent=2, ensure_ascii=False)
    
    def get_processing_summary(self) -> Dict:
        """
        Get summary of processing attempts and results
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'repair_attempts': len(self.repair_attempts),
            'last_repair_details': self.repair_attempts[-1] if self.repair_attempts else None,
            'validation_results': self.validation_results,
            'processing_log': self.processing_log
        }