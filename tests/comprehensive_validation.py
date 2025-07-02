#!/usr/bin/env python3
"""
Comprehensive Corner Case Validation Script
Independent testing of LLM JSON output against preamble/postamble requirements
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent if current_dir.name == 'tests' else current_dir
sys.path.insert(0, str(project_root))

from modules.json_processor import JSONProcessor
from modules.llm_repairs import get_repair_function, detect_llm_type

class ComprehensiveValidator:
    """
    Comprehensive validation against all preamble/postamble requirements
    """
    
    def __init__(self):
        self.processor = JSONProcessor()
        self.test_results = []
        
    def validate_against_requirements(self, json_data: str, source: str = "unknown") -> Dict:
        """
        Validate JSON against all critical requirements
        
        Args:
            json_data: Raw JSON string to validate
            source: Description of data source
            
        Returns:
            Comprehensive validation results
        """
        result = {
            'source': source,
            'timestamp': time.time(),
            'preamble_compliance': {},
            'postamble_compliance': {},
            'processing_success': False,
            'auto_correction_applied': False,
            'final_validation': {},
            'critical_violations': []
        }
        
        # Step 1: Check preamble requirements (Unicode/LaTeX)
        result['preamble_compliance'] = self._check_preamble_requirements(json_data)
        
        # Step 2: Check postamble requirements (JSON structure)
        result['postamble_compliance'] = self._check_postamble_requirements(json_data)
        
        # Step 3: Attempt processing with auto-correction
        llm_type = detect_llm_type(json_data)
        success, processed_data, messages = self.processor.process_raw_json(json_data, llm_type)
        
        result['processing_success'] = success
        result['processing_messages'] = messages
        result['detected_llm_type'] = llm_type
        
        if success and processed_data:
            # Step 4: Deep validation of processed data
            validation_results = self.processor.validate_questions(processed_data)
            result['final_validation'] = validation_results
            
            # Check if auto-correction was applied
            if len(self.processor.repair_attempts) > 0:
                result['auto_correction_applied'] = True
                result['repair_details'] = self.processor.repair_attempts[-1]
        
        # Step 5: Identify critical violations
        result['critical_violations'] = self._identify_critical_violations(result)
        
        self.test_results.append(result)
        return result
    
    def _check_preamble_requirements(self, json_data: str) -> Dict:
        """Check against preamble requirements"""
        violations = []
        warnings = []
        
        # Critical: No Unicode characters
        forbidden_unicode = ['Ω', '°', '²', '³', 'μ', 'π', '±', '≤', '≥', '∞', 'α', 'β', 'γ', 'θ', 'λ', 'σ', '×', '÷', '√']
        
        unicode_found = []
        for char in forbidden_unicode:
            if char in json_data:
                unicode_found.append(char)
        
        if unicode_found:
            violations.append(f"CRITICAL: Forbidden Unicode characters found: {unicode_found}")
        
        # Check for proper LaTeX usage
        if '$' not in json_data and any(char in json_data for char in ['Ω', '°', '²']):
            violations.append("Mathematical content not wrapped in LaTeX delimiters")
        
        # Check for display math (problematic)
        if '$$' in json_data:
            warnings.append("Display math ($$...$$) detected - may cause JSON parsing issues")
        
        return {
            'violations': violations,
            'warnings': warnings,
            'unicode_compliant': len(unicode_found) == 0,
            'latex_delimited': '$' in json_data
        }
    
    def _check_postamble_requirements(self, json_data: str) -> Dict:
        """Check against postamble requirements"""
        violations = []
        warnings = []
        
        # Must start with { and end with }
        stripped_data = json_data.strip()
        if not (stripped_data.startswith('{') and stripped_data.endswith('}')):
            violations.append("JSON must start with { and end with }")
        
        # Check for forbidden patterns
        forbidden_patterns = [
            ('```json', 'Markdown code blocks forbidden'),
            ('```', 'Markdown code blocks forbidden'),
            ('[cite', 'Citation patterns forbidden'),
            ('PowerShell', 'Context bleeding detected'),
            ('I cannot', 'Refusal patterns detected'),
            ('I apologize', 'Apology patterns detected')
        ]
        
        for pattern, message in forbidden_patterns:
            if pattern in json_data:
                violations.append(f"{message}: '{pattern}' found")
        
        # Check for proper JSON structure attempt
        try:
            parsed = json.loads(stripped_data)
            if isinstance(parsed, dict) and 'questions' in parsed:
                warnings.append("Proper questions array structure detected")
            else:
                violations.append("Missing 'questions' array structure")
        except json.JSONDecodeError:
            violations.append("Invalid JSON syntax")
        
        return {
            'violations': violations,
            'warnings': warnings,
            'json_boundaries_correct': stripped_data.startswith('{') and stripped_data.endswith('}'),
            'forbidden_patterns_found': len([v for v in violations if 'forbidden' in v.lower()]) > 0
        }
    
    def _identify_critical_violations(self, result: Dict) -> List[str]:
        """Identify violations that would cause system failure"""
        critical = []
        
        # Preamble critical violations
        preamble = result['preamble_compliance']
        if not preamble['unicode_compliant']:
            critical.append("SYSTEM FAILURE: Unicode characters present - hard constraint violation")
        
        # Postamble critical violations
        postamble = result['postamble_compliance']
        if not postamble['json_boundaries_correct']:
            critical.append("SYSTEM FAILURE: Invalid JSON boundaries")
        
        # Processing failures
        if not result['processing_success']:
            critical.append("SYSTEM FAILURE: JSON processing failed even with auto-correction")
        
        return critical
    
    def run_corner_case_suite(self) -> Dict:
        """Run comprehensive corner case test suite"""
        print("🧪 Running Comprehensive Corner Case Validation Suite")
        print("=" * 60)
        
        test_suite_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'critical_failures': 0,
            'auto_corrections': 0,
            'test_details': []
        }
        
        # Test 1: Known corner cases
        corner_cases_path = project_root / "test_data" / "CornerCases.json"
        if corner_cases_path.exists():
            print("\n📋 Testing CornerCases.json...")
            with open(corner_cases_path, 'r', encoding='utf-8') as f:
                corner_data = f.read()
            
            result = self.validate_against_requirements(corner_data, "CornerCases.json")
            test_suite_results['test_details'].append(result)
            test_suite_results['total_tests'] += 1
            
            if result['processing_success']:
                test_suite_results['passed_tests'] += 1
            if result['critical_violations']:
                test_suite_results['critical_failures'] += 1
            if result['auto_correction_applied']:
                test_suite_results['auto_corrections'] += 1
        
        # Test 2: Real ChatGPT data
        chatgpt_path = project_root / "test_data" / "chatgpt_responses" / "antenna_display_math.json"
        if chatgpt_path.exists():
            print("\n📋 Testing ChatGPT antenna display math...")
            with open(chatgpt_path, 'r', encoding='utf-8') as f:
                chatgpt_data = f.read()
            
            result = self.validate_against_requirements(chatgpt_data, "ChatGPT Antenna Display Math")
            test_suite_results['test_details'].append(result)
            test_suite_results['total_tests'] += 1
            
            if result['processing_success']:
                test_suite_results['passed_tests'] += 1
            if result['critical_violations']:
                test_suite_results['critical_failures'] += 1
            if result['auto_correction_applied']:
                test_suite_results['auto_corrections'] += 1
        
        # Test 3: Synthetic violations
        synthetic_tests = [
            ('Unicode Violations', '{"questions":[{"title":"Test with Ω and °","type":"multiple_choice"}]}'),
            ('Display Math', '{"questions":[{"title":"Test","feedback_correct":"$$f = \\\\frac{1}{2}$$","type":"numerical"}]}'),
            ('Markdown Contamination', '```json\\n{"questions":[{"title":"Test"}]}\\n```'),
            ('Citation Pattern', '{"questions":[{"title":"Test [cite:1]","type":"true_false"}]}'),
            ('Malformed JSON', '{"questions":[{"title":"Test","type":"multiple_choice"'),
        ]
        
        for test_name, test_data in synthetic_tests:
            print(f"\n📋 Testing {test_name}...")
            result = self.validate_against_requirements(test_data, test_name)
            test_suite_results['test_details'].append(result)
            test_suite_results['total_tests'] += 1
            
            if result['processing_success']:
                test_suite_results['passed_tests'] += 1
            if result['critical_violations']:
                test_suite_results['critical_failures'] += 1
            if result['auto_correction_applied']:
                test_suite_results['auto_corrections'] += 1
        
        return test_suite_results
    
    def generate_report(self, suite_results: Dict) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE CORNER CASE VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests: {suite_results['total_tests']}")
        report.append(f"Passed: {suite_results['passed_tests']}")
        report.append(f"Critical Failures: {suite_results['critical_failures']}")
        report.append(f"Auto-Corrections Applied: {suite_results['auto_corrections']}")
        
        success_rate = (suite_results['passed_tests'] / suite_results['total_tests']) * 100 if suite_results['total_tests'] > 0 else 0
        report.append(f"Success Rate: {success_rate:.1f}%")
        report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS")
        report.append("-" * 40)
        
        for i, result in enumerate(suite_results['test_details'], 1):
            report.append(f"\n{i}. {result['source']}")
            report.append(f"   Status: {'✅ PASS' if result['processing_success'] else '❌ FAIL'}")
            report.append(f"   LLM Type: {result.get('detected_llm_type', 'unknown')}")
            report.append(f"   Auto-Correction: {'✅ Applied' if result['auto_correction_applied'] else '⏸️ Not needed'}")
            
            # Preamble compliance
            preamble = result['preamble_compliance']
            report.append(f"   Unicode Compliant: {'✅' if preamble['unicode_compliant'] else '❌'}")
            report.append(f"   LaTeX Delimited: {'✅' if preamble['latex_delimited'] else '⚠️'}")
            
            # Critical violations
            if result['critical_violations']:
                report.append(f"   ⚠️ CRITICAL VIOLATIONS:")
                for violation in result['critical_violations']:
                    report.append(f"      • {violation}")
            
            # Final validation (if processed successfully)
            if result['processing_success'] and 'final_validation' in result:
                final_val = result['final_validation']
                report.append(f"   Final Validation: {final_val['valid']}/{final_val['total']} questions valid")
                
                if final_val.get('unicode_violations'):
                    report.append(f"   ❌ Unicode Violations: {len(final_val['unicode_violations'])}")
                if final_val.get('latex_issues'):
                    report.append(f"   ⚠️ LaTeX Issues: {len(final_val['latex_issues'])}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main execution function"""
    validator = ComprehensiveValidator()
    
    # Run the comprehensive test suite
    results = validator.run_corner_case_suite()
    
    # Generate and display report
    report = validator.generate_report(results)
    print(report)
    
    # Save report to file
    report_path = project_root / "tests" / "corner_case_validation_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")
    
    # Return exit code based on critical failures
    exit_code = 1 if results['critical_failures'] > 0 else 0
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
