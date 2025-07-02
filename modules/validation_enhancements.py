"""
Enhanced validation modules for Q2JSON
Includes mathematical consistency checking and other advanced validations
"""

from typing import Dict, List, Any, Tuple
from .mathematical_consistency_detector import MathematicalConsistencyDetector


class EnhancedValidator:
    """
    Enhanced validation system that extends basic JSON validation
    with advanced consistency checks
    """
    
    def __init__(self):
        self.math_detector = MathematicalConsistencyDetector()
        self.validation_messages = []
        self.warnings = []
        self.errors = []
    
    def validate_with_enhancements(self, questions_data: Dict) -> Tuple[bool, List[str]]:
        """
        Perform enhanced validation including mathematical consistency
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, messages)
        """
        
        self.validation_messages = []
        self.warnings = []
        self.errors = []
        
        # Basic structure validation (delegate to existing logic)
        if not self._basic_structure_validation(questions_data):
            return False, self.validation_messages
        
        # Mathematical consistency checking
        self._check_mathematical_consistency(questions_data)
        
        # Additional future validations can be added here
        # self._check_latex_consistency(questions_data)
        # self._check_image_references(questions_data)
        # self._check_topic_coherence(questions_data)
        
        # Compile final messages
        all_messages = self.validation_messages + self.warnings + self.errors
        
        # Return success if no errors (warnings don't fail validation)
        return len(self.errors) == 0, all_messages
    
    def _basic_structure_validation(self, questions_data: Dict) -> bool:
        """Basic structure validation - can be replaced with existing logic"""
        
        if 'questions' not in questions_data:
            self.errors.append("❌ Missing 'questions' array")
            return False
        
        if not isinstance(questions_data['questions'], list):
            self.errors.append("❌ 'questions' must be an array")
            return False
        
        if len(questions_data['questions']) == 0:
            self.errors.append("❌ 'questions' array is empty")
            return False
        
        self.validation_messages.append("✅ Basic structure validation passed")
        return True
    
    def _check_mathematical_consistency(self, questions_data: Dict):
        """Check for mathematical contradictions"""
        
        contradictions = self.math_detector.detect_contradictions(questions_data)
        
        if not contradictions:
            self.validation_messages.append("✅ No mathematical contradictions detected")
            return
        
        # Categorize contradictions by severity
        severe_count = sum(1 for c in contradictions if c.severity == "severe")
        moderate_count = sum(1 for c in contradictions if c.severity == "moderate")
        minor_count = sum(1 for c in contradictions if c.severity == "minor")
        
        # Severe contradictions are errors (fail validation)
        if severe_count > 0:
            self.errors.append(f"🚨 {severe_count} severe mathematical contradictions detected")
        
        # Moderate and minor are warnings (don't fail validation)
        if moderate_count > 0:
            self.warnings.append(f"🔶 {moderate_count} moderate mathematical contradictions detected")
        
        if minor_count > 0:
            self.warnings.append(f"⚠️ {minor_count} minor mathematical contradictions detected")
        
        # Add detailed information for review
        stats = self.math_detector.get_summary_stats()
        self.warnings.append(
            f"📊 Mathematical consistency summary: "
            f"{stats['questions_affected']} questions affected, "
            f"max difference {stats['max_difference']:.1f}%"
        )
    
    def get_detailed_math_report(self) -> str:
        """Get detailed mathematical contradiction report"""
        return self.math_detector.generate_report()
    
    def get_contradiction_summary(self) -> Dict[str, Any]:
        """Get summary of mathematical contradictions"""
        return self.math_detector.get_summary_stats()


def integrate_enhanced_validation(json_processor_instance):
    """
    Integrate enhanced validation into existing JSONProcessor
    
    Args:
        json_processor_instance: Instance of JSONProcessor to enhance
    """
    
    # Store original validation method
    original_validate = json_processor_instance._validate_questions_structure
    
    def enhanced_validation_wrapper(questions_data):
        """Wrapper that adds enhanced validation"""
        
        # Run original validation first
        basic_valid = original_validate(questions_data)
        
        if not basic_valid:
            return False  # Don't proceed with enhanced validation if basic fails
        
        # Run enhanced validation
        validator = EnhancedValidator()
        enhanced_valid, messages = validator.validate_with_enhancements(questions_data)
        
        # Store enhanced validation results
        if not hasattr(json_processor_instance, 'enhanced_validation_messages'):
            json_processor_instance.enhanced_validation_messages = []
        
        json_processor_instance.enhanced_validation_messages.extend(messages)
        
        # Store validator instance for detailed reports
        json_processor_instance._enhanced_validator = validator
        
        # Return combined result (basic validation is required, enhanced adds warnings)
        return basic_valid  # Don't fail on enhanced validation warnings
    
    # Replace validation method
    json_processor_instance._validate_questions_structure = enhanced_validation_wrapper
    
    # Add methods to access enhanced validation results
    def get_enhanced_validation_messages():
        return getattr(json_processor_instance, 'enhanced_validation_messages', [])
    
    def get_mathematical_consistency_report():
        if hasattr(json_processor_instance, '_enhanced_validator'):
            return json_processor_instance._enhanced_validator.get_detailed_math_report()
        return "Enhanced validation not run"
    
    def get_mathematical_consistency_summary():
        if hasattr(json_processor_instance, '_enhanced_validator'):
            return json_processor_instance._enhanced_validator.get_contradiction_summary()
        return {}
    
    # Add methods to processor instance
    json_processor_instance.get_enhanced_validation_messages = get_enhanced_validation_messages
    json_processor_instance.get_mathematical_consistency_report = get_mathematical_consistency_report
    json_processor_instance.get_mathematical_consistency_summary = get_mathematical_consistency_summary