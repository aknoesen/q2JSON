#!/usr/bin/env python3
"""
q2validate_cli - Command Line JSON Validation Tool for Q2LMS
"""

# Fix Windows Unicode encoding issues
import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Rest of your imports...
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Import from Q2LMS modules (single source of truth)
sys.path.insert(0, str(Path(__file__).parent.parent / "q2lms"))

try:
    from modules.schema_validator import JSONSchemaValidator
    from modules.unicode_converter import get_unicode_converter
except ImportError as e:
    print(f"Error: Cannot import from Q2LMS modules: {e}")
    print("Make sure Q2LMS is in the parent directory and has the required modules")
    print("Expected structure:")
    print("  Project-Root/")
    print("  ├── q2lms/modules/")
    print("  └── q2validate/q2validate_cli.py")
    sys.exit(1)

class Q2ValidateCLI:
    def __init__(self):
        """Initialize using Q2LMS modules"""
        self.validator = JSONSchemaValidator()
        self.converter = get_unicode_converter()
    
    def validate_and_process_questions(self, questions: List[Dict[str, Any]], auto_fix_unicode: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Validate and process questions using Q2LMS validation logic"""
        
        results = {
            'total_questions': len(questions),
            'schema_valid': 0,
            'unicode_issues': 0,
            'auto_fixed': 0,
            'ready_for_q2lms': 0,
            'question_results': []
        }
        
        processed_questions = []
        
        for i, question in enumerate(questions):
            # Schema validation using Q2LMS validator
            is_schema_valid, schema_errors = self.validator.validate_question_schema(question)
            
            # Unicode detection using Q2LMS converter
            unicode_issues = self.converter.detect_issues(question)
            has_unicode = len(unicode_issues) > 0
            
            # Auto-fix Unicode if requested and available
            final_question = question.copy()
            conversion_report = {}
            
            if auto_fix_unicode and has_unicode and hasattr(self.converter, 'convert_question'):
                final_question, conversion_report = self.converter.convert_question(question)
                # Re-check after conversion
                remaining_unicode = self.converter.detect_issues(final_question)
                has_unicode_after = len(remaining_unicode) > 0
            else:
                has_unicode_after = has_unicode
                conversion_report = {'conversion_successful': not has_unicode}
            
            # Update counters
            if is_schema_valid:
                results['schema_valid'] += 1
            if has_unicode:
                results['unicode_issues'] += 1
            if auto_fix_unicode and conversion_report.get('conversion_successful', False):
                results['auto_fixed'] += 1
            if is_schema_valid and not has_unicode_after:
                results['ready_for_q2lms'] += 1
            
            # Store individual results
            question_result = {
                'index': i,
                'title': question.get('title', f'Question {i+1}'),
                'schema_valid': is_schema_valid,
                'schema_errors': schema_errors,
                'had_unicode': has_unicode,
                'has_unicode_after': has_unicode_after,
                'unicode_issues': unicode_issues,
                'conversion_report': conversion_report,
                'ready_for_q2lms': is_schema_valid and not has_unicode_after
            }
            
            results['question_results'].append(question_result)
            processed_questions.append(final_question)
        
        return processed_questions, results
    
    def create_export_data(self, questions: List[Dict[str, Any]], results: Dict[str, Any]) -> Dict[str, Any]:
        """Create export data structure compatible with Q2LMS"""
        
        export_data = {
            'questions': questions,
            'metadata': {
                'processed_by': 'q2validate_cli',
                'processing_date': datetime.now().isoformat(),
                'validation_results': {
                    'total_questions': results['total_questions'],
                    'schema_valid': results['schema_valid'],
                    'unicode_issues_found': results['unicode_issues'],
                    'unicode_issues_fixed': results['auto_fixed'],
                    'ready_for_q2lms': results['ready_for_q2lms']
                },
                'format_version': '1.0',
                'validated_for_q2lms': True
            }
        }
        
        return export_data
    
    def print_summary(self, results: Dict[str, Any], verbose: bool = False):
        """Print validation summary to console"""
        
        print("\n" + "="*60)
        print("🔍 Q2VALIDATE RESULTS SUMMARY")
        print("="*60)
        
        print(f"📊 Total Questions: {results['total_questions']}")
        print(f"✅ Schema Valid: {results['schema_valid']}")
        print(f"⚠️  Unicode Issues Found: {results['unicode_issues']}")
        print(f"🔧 Unicode Issues Fixed: {results['auto_fixed']}")
        print(f"🎯 Ready for Q2LMS: {results['ready_for_q2lms']}")
        
        success_rate = (results['ready_for_q2lms'] / results['total_questions'] * 100) if results['total_questions'] > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if results['ready_for_q2lms'] == results['total_questions']:
            print("\n🎉 SUCCESS: All questions are valid and ready for Q2LMS!")
        elif results['ready_for_q2lms'] > 0:
            print(f"\n✅ PARTIAL: {results['ready_for_q2lms']} questions ready, {results['total_questions'] - results['ready_for_q2lms']} need attention")
        else:
            print("\n❌ WARNING: No questions are ready for Q2LMS!")
        
        # Detailed errors if verbose
        if verbose and results['ready_for_q2lms'] < results['total_questions']:
            print("\n" + "-"*40)
            print("DETAILED ISSUES:")
            print("-"*40)
            
            for result in results['question_results']:
                if not result['ready_for_q2lms']:
                    print(f"\nQuestion {result['index'] + 1}: {result['title']}")
                    if not result['schema_valid']:
                        print("  ❌ Schema errors:")
                        for error in result['schema_errors']:
                            print(f"    • {error}")
                    if result['has_unicode_after']:
                        print("  ⚠️  Unicode issues:")
                        for field, chars in result['unicode_issues'].items():
                            print(f"    • {field}: {', '.join(chars)}")
    
    def process_file(self, input_file: str, output_file: str = None, 
                    auto_fix: bool = True, verbose: bool = False, 
                    ready_only: bool = False) -> bool:
        """Process input file and generate output"""
        
        # Read input file
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                print(f"❌ Error: Input file '{input_file}' not found")
                return False
            
            with open(input_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            print(f"Loaded: {input_file}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in '{input_file}': {e}")
            return False
        except Exception as e:
            print(f"Error reading '{input_file}': {e}")
            return False
        
        # Handle different JSON structures
        if isinstance(questions_data, dict) and 'questions' in questions_data:
            questions = questions_data['questions']
        elif isinstance(questions_data, list):
            questions = questions_data
        else:
            print("❌ Error: Unexpected JSON structure. Expected {'questions': [...]} or [...]")
            return False
        
        if not questions:
            print("⚠️  Warning: No questions found in JSON")
            return False
        
        print(f"🔄 Processing {len(questions)} questions using Q2LMS validation...")
        
        # Process questions
        processed_questions, validation_results = self.validate_and_process_questions(
            questions, auto_fix
        )
        
        # Filter for ready questions only if requested
        if ready_only:
            ready_questions = [
                processed_questions[i] for i, result in enumerate(validation_results['question_results'])
                if result['ready_for_q2lms']
            ]
            processed_questions = ready_questions
            
            if not ready_questions:
                print("❌ Error: No questions are ready for export")
                return False
        
        # Print summary
        self.print_summary(validation_results, verbose)
        
        # Write output file if specified
        if output_file:
            try:
                export_data = self.create_export_data(processed_questions, validation_results)
                
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"\n📤 Output saved: {output_file}")
                print(f"✅ Ready for import into Q2LMS")
                
            except Exception as e:
                print(f"❌ Error writing output file '{output_file}': {e}")
                return False
        
        # Return success status
        return validation_results['ready_for_q2lms'] > 0

def main():
    parser = argparse.ArgumentParser(
        description='q2validate - Validate JSON questions for Q2LMS using Q2LMS validation rules',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python q2validate_cli.py input.json
  python q2validate_cli.py input.json --output validated.json
  python q2validate_cli.py input.json --output ready.json --ready-only
  python q2validate_cli.py input.json --no-auto-fix --verbose

This tool uses the same validation logic as Q2LMS to ensure compatibility.
        """
    )
    
    parser.add_argument('input', help='Input JSON file from q2prompt')
    parser.add_argument('-o', '--output', help='Output JSON file (optional)')
    parser.add_argument('--no-auto-fix', action='store_true', 
                       help='Disable automatic Unicode to LaTeX conversion')
    parser.add_argument('--ready-only', action='store_true',
                       help='Export only questions ready for Q2LMS')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed error information')
    parser.add_argument('--version', action='version', version='q2validate_cli 1.0.0')
    
    args = parser.parse_args()
    
    # Create validator instance
    validator = Q2ValidateCLI()
    
    # Process file
    success = validator.process_file(
        input_file=args.input,
        output_file=args.output,
        auto_fix=not args.no_auto_fix,
        verbose=args.verbose,
        ready_only=args.ready_only
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()