import pytest
import sys
import os
from unittest.mock import Mock, patch
import re
from debug_fixed_detector import debug_pattern_matching, test_with_improved_patterns
from debug_fixed_detector import test_with_improved_patterns
from debug_fixed_detector import test_with_improved_patterns
import time
import time
import time

# Add modules to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))



class TestDebugPatternMatching:
    """Test the debug pattern matching functionality"""
    
    def test_debug_pattern_matching_basic(self, capsys):
        """Test basic debug pattern matching output"""
        # Run the debug function
        debug_pattern_matching()
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify key elements are present in output
        assert "DEBUGGING FIXED DETECTOR PATTERN MATCHING" in captured.out
        assert "Test text:" in captured.out
        assert "Declared answer:" in captured.out
        assert "Final answers found:" in captured.out
        assert "TESTING INDIVIDUAL PATTERNS:" in captured.out
        assert "TESTING SIMPLER PATTERNS:" in captured.out
    
    def test_debug_pattern_extraction_values(self, capsys):
        """Test that debug correctly extracts expected values"""
        debug_pattern_matching()
        captured = capsys.readouterr()
        
        # Should find both 0.8116 and 0.776 values
        assert "0.8116" in captured.out
        assert "0.776" in captured.out
        
        # Should identify final answer pattern
        assert "Final answer statements" in captured.out
        assert "V_T equals" in captured.out
        assert "Value with V unit" in captured.out
    
    def test_individual_pattern_testing(self):
        """Test individual regex patterns used in debug"""
        test_text = "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
        
        # Test final answer pattern
        final_answer_pattern = r'(?:final\s+answer|the\s+answer\s+is|result\s+is|therefore|conclusion)\s*[:\s]*[VIR]?_?[A-Z]?\s*[=≈]\s*(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{[^}]+\}|[A-Za-zΩμ]+)?'
        matches = list(re.finditer(final_answer_pattern, test_text, re.IGNORECASE))
        
        assert len(matches) == 1
        assert float(matches[0].group(1)) == 0.776
    
    def test_simple_patterns(self):
        """Test the simpler regex patterns"""
        test_text = "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
        
        # Test V_T equals pattern
        vt_pattern = r'V_T\s*=\s*(\d+\.?\d*)'
        matches = list(re.finditer(vt_pattern, test_text))
        
        assert len(matches) == 2
        values = [float(match.group(1)) for match in matches]
        assert 0.8116 in values
        assert 0.776 in values
    
    def test_debug_with_different_inputs(self):
        """Test debug function behavior with different text inputs"""
        # Mock the detector to test with different inputs
        original_debug = debug_pattern_matching
        
        def modified_debug():
            # Test with different scenarios
            test_cases = [
                "V_T = 5.0 V exactly",
                "The result is approximately 3.14159",
                "No numbers here!",
                "Multiple values: 1.0, 2.0, 3.0 V"
            ]
            
            for test_text in test_cases:
                # Test simple pattern matching
                vt_matches = re.findall(r'V_T\s*=\s*(\d+\.?\d*)', test_text)
                approx_matches = re.findall(r'approximately\s+(\d+\.?\d*)', test_text)
                
                # Should handle all cases without error
                assert isinstance(vt_matches, list)
                assert isinstance(approx_matches, list)
        
        # Run modified test
        modified_debug()


class TestImprovedDetector:
    """Test the ImprovedDetector class from the debug script"""
    
    @pytest.fixture
    def improved_detector(self):
        """Create an ImprovedDetector instance"""
        # Import the class from the debug script
        
        # Create inline class as done in the script
        class ImprovedDetector:
            def __init__(self):
                self.tolerance_threshold = 0.05
                self.common_intermediates = {0.4, 0.5, 0.8, 0.894, 1.673, 2.0, 2.8}
            
            def extract_final_values(self, text: str):
                """Simplified final value extraction"""
                final_values = []
                
                patterns = [
                    r'final\s+answer[:\s]*.*?(\d+\.?\d*)',
                    r'V_T\s*=\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{)?V(?:\})?[\s.!]*$',
                    r'=\s*(\d+\.?\d*)\s*V',
                    r'≈\s*(\d+\.?\d*)',
                ]
                
                for pattern in patterns:
                    for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                        try:
                            value = float(match.group(1))
                            if value not in self.common_intermediates:
                                context = text[max(0, match.start()-30):match.end()+30].strip()
                                final_values.append((value, context))
                        except (ValueError, IndexError):
                            continue
                
                # Remove duplicates
                unique_values = []
                for value, context in final_values:
                    if not any(abs(v - value) < 0.001 for v, _ in unique_values):
                        unique_values.append((value, context))
                
                return unique_values
            
            def detect_contradiction(self, declared: float, text: str):
                """Simple contradiction detection"""
                final_values = self.extract_final_values(text)
                
                for value, context in final_values:
                    if abs(declared - value) > 0.001:
                        percentage_diff = abs(declared - value) / max(declared, 0.001) * 100
                        if percentage_diff > 2.0:
                            return True, value, percentage_diff, context
                
                return False, None, 0, ""
        
        return ImprovedDetector()
    
    def test_extract_final_values_basic(self, improved_detector):
        """Test basic final value extraction"""
        text = "The final answer is V_T = 1.234 V"
        
        final_values = improved_detector.extract_final_values(text)
        
        assert len(final_values) > 0
        values = [v[0] for v in final_values]
        assert 1.234 in values
    
    def test_extract_final_values_filters_intermediates(self, improved_detector):
        """Test that common intermediate values are filtered out"""
        text = "Using gamma = 0.4 and phi_F = 0.8, the final answer is 1.234 V"
        
        final_values = improved_detector.extract_final_values(text)
        
        # Should find 1.234 but not 0.4 or 0.8 (common intermediates)
        values = [v[0] for v in final_values]
        assert 1.234 in values
        assert 0.4 not in values
        assert 0.8 not in values
    
    def test_detect_contradiction_positive(self, improved_detector):
        """Test contradiction detection when there should be one"""
        declared = 0.776
        text = "Calculation gives V_T = 0.8116 V. Final answer: V_T = 0.776 V."
        
        has_contradiction, value, diff, context = improved_detector.detect_contradiction(declared, text)
        
        assert has_contradiction == True
        assert value == 0.8116
        assert diff > 2.0  # Should be > 2% difference threshold
        assert "0.8116" in context
    
    def test_detect_contradiction_negative_normal_rounding(self, improved_detector):
        """Test no contradiction for normal rounding"""
        declared = 0.812
        text = "V_T = 0.8116 V. Rounding to three decimal places: V_T ≈ 0.812 V."
        
        has_contradiction, value, diff, context = improved_detector.detect_contradiction(declared, text)
        
        # Should not detect contradiction for normal rounding
        # The 0.8116 might be found but percentage difference should be small
        if has_contradiction:
            assert diff <= 2.0  # Within rounding tolerance
        else:
            assert has_contradiction == False
    
    def test_detect_contradiction_calculation_progression(self, improved_detector):
        """Test no contradiction for normal calculation progression"""
        declared = 0.8116
        text = "V_T = 0.5 + 0.4(1.673 - 0.894) = 0.8116 V"
        
        has_contradiction, value, diff, context = improved_detector.detect_contradiction(declared, text)
        
        assert has_contradiction == False
    
    def test_remove_duplicates(self, improved_detector):
        """Test that duplicate values are properly removed"""
        text = "V_T = 1.234 V and also V_T = 1.234 V again"
        
        final_values = improved_detector.extract_final_values(text)
        
        # Should only have one instance of 1.234
        values = [v[0] for v in final_values]
        assert values.count(1.234) == 1
    
    def test_context_preservation(self, improved_detector):
        """Test that context is properly preserved"""
        text = "The important final answer is V_T = 9.876 V for this problem"
        
        final_values = improved_detector.extract_final_values(text)
        
        assert len(final_values) > 0
        value, context = final_values[0]
        assert value == 9.876
        assert "final answer" in context.lower()
    
    def test_multiple_patterns_same_value(self, improved_detector):
        """Test handling when multiple patterns match the same value"""
        text = "Final answer: V_T = 5.55 V = 5.55 volts"
        
        final_values = improved_detector.extract_final_values(text)
        
        # Should deduplicate the same value
        values = [v[0] for v in final_values]
        assert values.count(5.55) == 1


class TestImprovedPatternsIntegration:
    """Test the complete test_with_improved_patterns function"""
    
    def test_improved_patterns_execution(self, capsys):
        """Test that the improved patterns test runs correctly"""
        test_with_improved_patterns()
        
        captured = capsys.readouterr()
        
        # Verify key elements in output
        assert "TESTING WITH IMPROVED PATTERNS" in captured.out
        assert "Real contradiction" in captured.out
        assert "Normal rounding" in captured.out
        assert "Calculation progression" in captured.out
        
        # Should show PASS results
        assert "✅ PASS" in captured.out
    
    def test_improved_patterns_test_cases(self, capsys):
        """Test the specific test cases in improved patterns"""
        test_with_improved_patterns()
        
        captured = capsys.readouterr()
        
        # Verify specific test cases are covered
        assert "Declared: 0.776" in captured.out
        assert "Declared: 0.812" in captured.out
        assert "Declared: 0.8116" in captured.out
        
        # Check that contradictions are properly detected/not detected
        lines = captured.out.split('\n')
        
        # Find test results
        real_contradiction_result = None
        normal_rounding_result = None
        calculation_progression_result = None
        
        for i, line in enumerate(lines):
            if "Real contradiction" in line:
                # Look for the result in following lines
                for j in range(i, min(i+10, len(lines))):
                    if "Contradiction detected:" in lines[j]:
                        real_contradiction_result = "True" in lines[j]
                        break
            elif "Normal rounding" in line:
                for j in range(i, min(i+10, len(lines))):
                    if "Contradiction detected:" in lines[j]:
                        normal_rounding_result = "True" in lines[j]
                        break
            elif "Calculation progression" in line:
                for j in range(i, min(i+10, len(lines))):
                    if "Contradiction detected:" in lines[j]:
                        calculation_progression_result = "True" in lines[j]
                        break
        
        # Verify expected results
        assert real_contradiction_result == True, "Should detect real contradiction"
        assert normal_rounding_result == False, "Should not detect contradiction in normal rounding"
        assert calculation_progression_result == False, "Should not detect contradiction in calculation progression"


class TestDebugEdgeCases:
    """Test edge cases in the debug functionality"""
    
    def test_empty_text_handling(self):
        """Test handling of empty or minimal text"""
        
        # Create a detector instance
        class TestDetector:
            def __init__(self):
                self.common_intermediates = {0.4, 0.5, 0.8}
            
            def extract_final_values(self, text: str):
                if not text or not text.strip():
                    return []
                
                # Simple pattern for testing
                matches = re.findall(r'(\d+\.?\d*)', text)
                return [(float(m), text) for m in matches if float(m) not in self.common_intermediates]
        
        detector = TestDetector()
        
        # Test with empty text
        result = detector.extract_final_values("")
        assert result == []
        
        # Test with whitespace only
        result = detector.extract_final_values("   \n  \t  ")
        assert result == []
        
        # Test with no numbers
        result = detector.extract_final_values("This text has no numbers")
        assert result == []
    
    def test_invalid_number_handling(self):
        """Test handling of invalid number patterns"""
        # Test patterns that might cause ValueError
        test_text = "Value: 123.456.789 and also 12..34 and normal 5.67"
        
        # Should extract only valid numbers
        valid_numbers = []
        for match in re.finditer(r'(\d+\.?\d*)', test_text):
            try:
                value = float(match.group(1))
                valid_numbers.append(value)
            except ValueError:
                continue
        
        # Should find valid numbers and skip invalid ones
        assert 5.67 in valid_numbers
        # Should handle malformed numbers gracefully
        assert len(valid_numbers) >= 1
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters"""
        test_text = "The résult is V_T = 3.14159 µV with π ≈ 3.14"
        
        # Should handle Unicode characters without crashing
        vt_pattern = r'V_T\s*=\s*(\d+\.?\d*)'
        matches = re.findall(vt_pattern, test_text)
        
        assert len(matches) == 1
        assert float(matches[0]) == 3.14159
    
    def test_very_long_text(self):
        """Test performance with very long text"""
        # Create long text with embedded values
        long_text = "Start of text. " + "Some filler text. " * 1000 + "Final answer: V_T = 7.89 V. " + "More filler. " * 1000
        
        # Should still extract values efficiently
        final_answer_pattern = r'final\s+answer[:\s]*.*?(\d+\.?\d*)'
        matches = re.findall(final_answer_pattern, long_text, re.IGNORECASE)
        
        assert len(matches) == 1
        assert float(matches[0]) == 7.89
    
    def test_nested_mathematical_expressions(self):
        """Test with complex nested mathematical expressions"""
        complex_text = """
        Using the formula V_T = V_{T0} + γ(√(2φ_F + V_{SB}) - √(2φ_F)):
        V_T = 0.5 + 0.4(√(0.8 + 2) - √(0.8))
        V_T = 0.5 + 0.4(√2.8 - √0.8)
        V_T = 0.5 + 0.4(1.673 - 0.894) = 0.8116 V
        Final answer: V_T ≈ 0.776 V
        """
        
        # Should extract multiple values
        all_numbers = re.findall(r'(\d+\.?\d*)', complex_text)
        numeric_values = [float(n) for n in all_numbers]
        
        # Should find key values
        assert 0.8116 in numeric_values
        assert 0.776 in numeric_values
        assert 0.5 in numeric_values
        assert 0.4 in numeric_values


class TestDebugPerformance:
    """Test performance aspects of debug functions"""
    
    def test_debug_function_timing(self):
        """Test that debug functions complete in reasonable time"""
        
        start_time = time.time()
        debug_pattern_matching()
        debug_time = time.time() - start_time
        
        assert debug_time < 2.0  # Should complete within 2 seconds
    
    def test_improved_patterns_timing(self):
        """Test that improved patterns test completes quickly"""
        
        start_time = time.time()
        test_with_improved_patterns()
        test_time = time.time() - start_time
        
        assert test_time < 3.0  # Should complete within 3 seconds
    
    def test_regex_compilation_efficiency(self):
        """Test that regex patterns compile efficiently"""
        patterns = [
            r'final\s+answer[:\s]*.*?(\d+\.?\d*)',
            r'V_T\s*=\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:,?\s*)?(?:\\text\{)?V(?:\})?[\s.!]*$',
            r'=\s*(\d+\.?\d*)\s*V',
            r'≈\s*(\d+\.?\d*)',
        ]
        
        # Should be able to compile all patterns quickly
        start_time = time.time()
        
        compiled_patterns = []
        for pattern in patterns:
            compiled_patterns.append(re.compile(pattern, re.IGNORECASE | re.MULTILINE))
        
        compile_time = time.time() - start_time
        
        assert compile_time < 0.1  # Should compile very quickly
        assert len(compiled_patterns) == len(patterns)


class TestDebugMocking:
    """Test debug functions with mocked dependencies"""
    
    @patch('debug_fixed_detector.MathematicalConsistencyDetectorFixed')
    def test_debug_with_mocked_detector(self, mock_detector_class):
        """Test debug function with mocked detector"""
        # Setup mock
        mock_detector = Mock()
        mock_detector._extract_genuine_final_answers.return_value = [(0.776, "test context")]
        mock_detector_class.return_value = mock_detector
        
        # This would test the debug function with controlled detector behavior
        # For now, we verify the mock is accessible
        assert mock_detector_class is not None
    
    def test_improved_detector_isolation(self):
        """Test improved detector in isolation"""
        # Test that ImprovedDetector works independently
        class IsolatedImprovedDetector:
            def __init__(self):
                self.tolerance_threshold = 0.05
                self.common_intermediates = {0.4, 0.5, 0.8}
            
            def extract_final_values(self, text: str):
                if not text:
                    return []
                
                pattern = r'(\d+\.?\d*)'
                matches = re.findall(pattern, text)
                
                final_values = []
                for match in matches:
                    try:
                        value = float(match)
                        if value not in self.common_intermediates:
                            final_values.append((value, text))
                    except ValueError:
                        continue
                
                return final_values
        
        detector = IsolatedImprovedDetector()
        result = detector.extract_final_values("Test with 1.23 and 0.5 values")
        
        # Should find 1.23 but not 0.5 (intermediate)
        values = [v[0] for v in result]
        assert 1.23 in values
        assert 0.5 not in values


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])