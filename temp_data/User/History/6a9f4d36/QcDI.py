#!/usr/bin/env python3
"""
Test Execution Script for Stage 4 Human Review Integration
This script automates basic testing of Stage 4 functionality
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class Stage4TestRunner:
    """Test runner for Stage 4 Human Review integration"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = project_root
        self.test_data_dir = self.project_root / "test_data"
        self.components_dir = self.project_root / "extracted_components"
        
    def log_test_result(self, test_name, result, details=""):
        """Log test result"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_results.append({
            "test_name": test_name,
            "result": result,
            "details": details,
            "timestamp": timestamp
        })
        print(f"[{timestamp}] {test_name}: {result}")
        if details:
            print(f"    Details: {details}")
    
    def test_component_imports(self):
        """Test 1: Component Import Verification"""
        print("\n=== Testing Component Imports ===")
        
        try:
            # Test extracted_components imports
            from extracted_components.editor_framework import Q2JSONEditorFramework
            from extracted_components.validation_manager import Q2JSONValidationManager
            from extracted_components.question_renderer import Q2JSONQuestionRenderer
            from extracted_components.latex_processor import Q2JSONLaTeXProcessor
            
            self.log_test_result("Component Imports", "PASS", "All components imported successfully")
            return True
            
        except ImportError as e:
            self.log_test_result("Component Imports", "FAIL", f"Import error: {e}")
            return False
    
    def test_navigation_manager(self):
        """Test 2: Navigation Manager Stage 4 Support"""
        print("\n=== Testing Navigation Manager ===")
        
        try:
            from navigation.manager import NavigationManager
            
            # Test stage bounds (using class attributes)
            if NavigationManager.STAGE_MAX != 3:
                self.log_test_result("Navigation Bounds", "FAIL", f"Expected STAGE_MAX=3, got {NavigationManager.STAGE_MAX}")
                return False
            
            # Test stage definitions
            if 3 not in NavigationManager.STAGES:
                self.log_test_result("Stage 3 Definition", "FAIL", "Stage 3 not defined in STAGES")
                return False
            
            # Test stage 3 title
            if "Human Review" not in NavigationManager.STAGES[3]:
                self.log_test_result("Stage 3 Title", "FAIL", f"Expected 'Human Review' in stage 3 title, got {NavigationManager.STAGES[3]}")
                return False
            
            self.log_test_result("Navigation Manager", "PASS", "Stage 4 navigation properly configured")
            return True
            
        except Exception as e:
            self.log_test_result("Navigation Manager", "FAIL", f"Error: {e}")
            return False
    
    def test_session_state_manager(self):
        """Test 3: Session State Manager Stage 4 Support"""
        print("\n=== Testing Session State Manager ===")
        
        try:
            from navigation.state import initialize_session_state, validate_session_state
            
            # Mock streamlit session state
            class MockSessionState:
                def __init__(self):
                    self._state = {}
                
                def __getitem__(self, key):
                    return self._state.get(key)
                
                def __setitem__(self, key, value):
                    self._state[key] = value
                
                def get(self, key, default=None):
                    return self._state.get(key, default)
                
                def __contains__(self, key):
                    return key in self._state
                
                def setdefault(self, key, default=None):
                    if key not in self._state:
                        self._state[key] = default
                    return self._state[key]
            
            # Replace st.session_state for testing
            import streamlit as st
            original_session_state = st.session_state
            st.session_state = MockSessionState()
            
            try:
                # Test initialization
                initialize_session_state()
                
                # Debug: Print all keys that were set
                print(f"Debug: Keys in session state after initialization: {list(st.session_state._state.keys())}")
                
                # Check Stage 4 keys after initialization
                stage4_keys = ['edited_questions_data', 'review_completed']
                missing_keys = []
                for key in stage4_keys:
                    if key not in st.session_state._state:
                        missing_keys.append(key)
                
                if missing_keys:
                    self.log_test_result("Session State Keys", "FAIL", f"Missing keys after initialization: {missing_keys}")
                    return False
                
                # Test validation
                validate_session_state()
                
                # Check keys again after validation
                for key in stage4_keys:
                    if key not in st.session_state._state:
                        self.log_test_result("Session State Keys", "FAIL", f"Missing key after validation: {key}")
                        return False
                
                self.log_test_result("Session State Manager", "PASS", "Stage 4 session state properly configured")
                return True
                
            finally:
                # Restore original session state
                st.session_state = original_session_state
            
        except Exception as e:
            self.log_test_result("Session State Manager", "FAIL", f"Error: {e}")
            return False
    
    def test_stage_files_exist(self):
        """Test 4: Stage Files Existence"""
        print("\n=== Testing Stage Files ===")
        
        required_files = [
            "stages/stage_3_human_review.py",
            "extracted_components/editor_framework.py",
            "extracted_components/validation_manager.py",
            "extracted_components/question_renderer.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test_result("Stage Files", "FAIL", f"Missing files: {missing_files}")
            return False
        
        self.log_test_result("Stage Files", "PASS", "All required stage files exist")
        return True
    
    def test_stage_3_import(self):
        """Test 5: Stage 3 Import Test"""
        print("\n=== Testing Stage 3 Import ===")
        
        try:
            from stages.stage_3_human_review import render_human_review
            
            # Test function exists and is callable
            if not callable(render_human_review):
                self.log_test_result("Stage 3 Import", "FAIL", "render_human_review not callable")
                return False
            
            self.log_test_result("Stage 3 Import", "PASS", "Stage 3 function imported successfully")
            return True
            
        except ImportError as e:
            self.log_test_result("Stage 3 Import", "FAIL", f"Import error: {e}")
            return False
    
    def test_app_integration(self):
        """Test 6: App Integration Test"""
        print("\n=== Testing App Integration ===")
        
        try:
            # Read app.py and check for Stage 3 integration
            app_file = self.project_root / "app.py"
            if not app_file.exists():
                self.log_test_result("App Integration", "FAIL", "app.py not found")
                return False
            
            with open(app_file, 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            # Check for Stage 3 import
            if "from stages.stage_3_human_review import render_human_review" not in app_content:
                self.log_test_result("App Integration", "FAIL", "Stage 3 import not found in app.py")
                return False
            
            # Check for Stage 3 routing
            if "elif current_stage == 3:" not in app_content:
                self.log_test_result("App Integration", "FAIL", "Stage 3 routing not found in app.py")
                return False
            
            self.log_test_result("App Integration", "PASS", "Stage 3 properly integrated into app.py")
            return True
            
        except Exception as e:
            self.log_test_result("App Integration", "FAIL", f"Error: {e}")
            return False
    
    def test_validation_manager_fixes(self):
        """Test 7: Validation Manager Fixes"""
        print("\n=== Testing Validation Manager Fixes ===")
        
        try:
            # Read editor_framework.py and check for fixes
            editor_file = self.project_root / "extracted_components" / "editor_framework.py"
            if not editor_file.exists():
                self.log_test_result("Validation Fixes", "FAIL", "editor_framework.py not found")
                return False
            
            with open(editor_file, 'r', encoding='utf-8') as f:
                editor_content = f.read()
            
            # Check for ValidationResult attribute access (not dictionary)
            if "validation_result['is_valid']" in editor_content:
                self.log_test_result("Validation Fixes", "FAIL", "Dictionary-style access still present")
                return False
            
            # Check for minimum text area height
            if "height=100" not in editor_content and "height=150" not in editor_content:
                self.log_test_result("Validation Fixes", "FAIL", "Text area height not fixed")
                return False
            
            self.log_test_result("Validation Fixes", "PASS", "Validation manager fixes applied")
            return True
            
        except Exception as e:
            self.log_test_result("Validation Fixes", "FAIL", f"Error: {e}")
            return False
    
    def test_requirements_dependencies(self):
        """Test 8: Requirements Dependencies"""
        print("\n=== Testing Requirements Dependencies ===")
        
        try:
            # Check if requirements.txt exists
            req_file = self.project_root / "requirements.txt"
            if not req_file.exists():
                self.log_test_result("Requirements", "FAIL", "requirements.txt not found")
                return False
            
            with open(req_file, 'r', encoding='utf-8') as f:
                requirements = f.read().lower()
            
            # Check for essential dependencies
            essential_deps = ['streamlit', 'pandas', 'numpy']
            missing_deps = []
            
            for dep in essential_deps:
                if dep not in requirements:
                    missing_deps.append(dep)
            
            if missing_deps:
                self.log_test_result("Requirements", "FAIL", f"Missing dependencies: {missing_deps}")
                return False
            
            self.log_test_result("Requirements", "PASS", "Essential dependencies present")
            return True
            
        except Exception as e:
            self.log_test_result("Requirements", "FAIL", f"Error: {e}")
            return False
    
    def generate_test_report(self):
        """Generate test report"""
        print("\n" + "="*50)
        print("STAGE 4 INTEGRATION TEST REPORT")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['result'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results if r['result'] == 'FAIL')
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nTest Results:")
        for result in self.test_results:
            status_icon = "✅" if result['result'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test_name']}: {result['result']}")
            if result['details']:
                print(f"    {result['details']}")
        
        # Save report to file
        report_file = self.project_root / "tests" / "stage4_test_report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return failed_tests == 0
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting Stage 4 Human Review Integration Tests...")
        print(f"Project Root: {self.project_root}")
        
        # Run all tests
        test_methods = [
            self.test_component_imports,
            self.test_navigation_manager,
            self.test_session_state_manager,
            self.test_stage_files_exist,
            self.test_stage_3_import,
            self.test_app_integration,
            self.test_validation_manager_fixes,
            self.test_requirements_dependencies
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test_result(test_method.__name__, "ERROR", f"Unexpected error: {e}")
        
        # Generate report
        success = self.generate_test_report()
        
        if success:
            print("\n🎉 All tests passed! Stage 4 integration is ready.")
        else:
            print("\n⚠️  Some tests failed. Please review the issues above.")
        
        return success


def main():
    """Main test execution function"""
    runner = Stage4TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
