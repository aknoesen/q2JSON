"""
Q2JSON Main Processing Pipeline with Mathematical Consistency Validation
Complete pipeline: JSON Loading → LaTeX Correction → Mathematical Validation → Output
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from mathematical_consistency_detector_working import MathematicalConsistencyDetectorWorking
except ImportError:
    print("ERROR: Mathematical consistency detector module not found")
    print("Please ensure mathematical_consistency_detector_working.py exists in modules/")
    sys.exit(1)

# Import LaTeX corrector if available (optional)
try:
    from latex_corrector import LaTeXCorrector
    LATEX_AVAILABLE = True
except ImportError:
    # Use ASCII-safe warning message for Windows console compatibility
    print("WARNING: LaTeX corrector not found - LaTeX correction will be skipped")
    LATEX_AVAILABLE = False


class Q2JSONPipeline:
    """
    Complete Q2JSON processing pipeline with mathematical validation
    Workflow: Load JSON → LaTeX Correction → Mathematical Validation → Save → Report
    """
    
    def __init__(self):
        """Initialize the pipeline components"""
        self.math_detector = MathematicalConsistencyDetectorWorking()
        self.latex_corrector = LaTeXCorrector() if LATEX_AVAILABLE else None
        self.processing_results = {}
    
    def process_file(self, input_file: str, output_file: str = None, 
                    check_math: bool = True, fix_latex: bool = True, 
                    verbose: bool = True) -> dict:
        """
        Complete processing pipeline for Q2JSON files
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output file (optional)
            check_math: Whether to run mathematical consistency checking
            fix_latex: Whether to run LaTeX correction
            verbose: Whether to provide detailed output
            
        Returns:
            Dictionary with processing results
        """
        
        if verbose:
            print("Q2JSON Processing Pipeline")
            print("=" * 50)
            print(f"Input file: {input_file}")
        
        # Step 1: Load and parse JSON
        try:
            questions_data = self._load_json_file(input_file, verbose)
        except Exception as e:
            return self._create_error_result("json_loading", str(e), verbose)
        
        # Step 2: LaTeX Correction (if available and enabled)
        latex_results = {"status": "skipped", "corrections_made": 0, "questions_affected": 0}
        
        if fix_latex and LATEX_AVAILABLE:
            try:
                questions_data, latex_results = self._apply_latex_correction(questions_data, verbose)
            except Exception as e:
                return self._create_error_result("latex_correction", str(e), verbose)
        elif fix_latex and not LATEX_AVAILABLE:
            if verbose:
                print("\nStep 1: LaTeX Correction - SKIPPED (module not available)")
        
        # Step 3: Mathematical Consistency Check
        math_results = {"status": "skipped"}
        
        if check_math:
            try:
                math_results = self._run_mathematical_validation(questions_data, verbose)
            except Exception as e:
                if verbose:
                    print(f"Mathematical validation failed: {str(e)}")
                math_results = {"status": "error", "message": str(e)}
        
        # Step 4: Save processed data
        if output_file:
            try:
                self._save_processed_data(questions_data, output_file, verbose)
            except Exception as e:
                return self._create_error_result("file_save", str(e), verbose)
        
        # Step 5: Generate comprehensive results
        results = {
            "status": "completed",
            "input_file": input_file,
            "output_file": output_file,
            "questions_processed": len(questions_data.get('questions', [])),
            "latex_corrections": latex_results,
            "mathematical_validation": math_results,
            "processed_data": questions_data
        }
        
        if verbose:
            self._print_final_report(results)
        
        return results
    
    def _load_json_file(self, input_file: str, verbose: bool) -> dict:
        """Load and parse JSON file"""
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove JSON comments (lines starting with //)
            content = '\n'.join(line for line in content.split('\n') 
                              if not line.strip().startswith('//'))
            questions_data = json.loads(content)
        
        if verbose:
            question_count = len(questions_data.get('questions', []))
            print(f"Loaded {question_count} questions from JSON")
        
        return questions_data
    
    def _apply_latex_correction(self, questions_data: dict, verbose: bool) -> tuple:
        """Apply LaTeX correction to questions data"""
        
        if verbose:
            print("\nStep 1: LaTeX Correction")
        
        latex_results = self.latex_corrector.correct_latex_in_questions(questions_data)
        
        if verbose:
            if latex_results['corrections_made'] > 0:
                print(f"   Fixed {latex_results['corrections_made']} LaTeX issues")
                print(f"   Questions affected: {latex_results['questions_affected']}")
            else:
                print("   No LaTeX corrections needed")
        
        return latex_results['corrected_data'], latex_results
    
    def _run_mathematical_validation(self, questions_data: dict, verbose: bool) -> dict:
        """Run mathematical consistency validation"""
        
        if verbose:
            print("\nStep 2: Mathematical Consistency Validation")
        
        contradictions = self.math_detector.detect_contradictions(questions_data)
        math_results = self.math_detector.get_summary_stats()
        
        if verbose:
            if contradictions:
                print(f"   Found {len(contradictions)} mathematical contradictions")
                
                # Show severity breakdown
                severity_counts = math_results.get('by_severity', {})
                for severity, count in severity_counts.items():
                    print(f"   {severity.title()}: {count}")
                
                if self.math_detector.has_severe_contradictions():
                    print("   SEVERE contradictions detected - immediate review recommended")
            else:
                print(f"   No mathematical contradictions detected")
                print(f"   Analyzed {math_results.get('questions_analyzed', 0)} questions")
                print(f"   Extracted {math_results.get('values_extracted', 0)} values")
        
        return math_results
    
    def _save_processed_data(self, questions_data: dict, output_file: str, verbose: bool):
        """Save processed data to output file"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, indent=2, ensure_ascii=False)
        
        if verbose:
            print(f"\nSaved processed data to: {output_file}")
    
    def _create_error_result(self, step: str, error_message: str, verbose: bool) -> dict:
        """Create error result dictionary"""
        
        if verbose:
            print(f"Error in {step}: {error_message}")
        
        return {
            "status": "error",
            "step": step,
            "message": error_message
        }
    
    def _print_final_report(self, results: dict):
        """Print comprehensive final report"""
        
        print("\n" + "=" * 60)
        print("Q2JSON PROCESSING SUMMARY")
        print("=" * 60)
        
        # Basic stats
        print(f"Status: {results['status'].upper()}")
        print(f"Questions processed: {results['questions_processed']}")
        
        # LaTeX results
        latex_results = results['latex_corrections']
        print(f"\nLaTeX Correction:")
        if latex_results['status'] == 'skipped':
            print("   SKIPPED")
        else:
            print(f"   Corrections made: {latex_results.get('corrections_made', 0)}")
            print(f"   Questions affected: {latex_results.get('questions_affected', 0)}")
        
        # Mathematical validation results
        math_results = results['mathematical_validation']
        print(f"\nMathematical Validation:")
        
        if math_results['status'] == 'passed':
            print("   PASSED - No contradictions detected")
            print(f"   Questions analyzed: {math_results.get('questions_analyzed', 0)}")
            print(f"   Values extracted: {math_results.get('values_extracted', 0)}")
        elif math_results['status'] == 'issues_found':
            print(f"   ISSUES FOUND - {math_results['total_contradictions']} contradictions")
            print(f"   Questions affected: {math_results['questions_affected']}")
            
            severity_counts = math_results.get('by_severity', {})
            for severity, count in severity_counts.items():
                print(f"   {severity.title()}: {count}")
            
            print(f"\nDETAILED MATHEMATICAL REPORT:")
            print(self.math_detector.generate_detailed_report())
        elif math_results['status'] == 'skipped':
            print("   SKIPPED")
        else:
            print(f"   ERROR: {math_results.get('message', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        
        # Recommendations
        if math_results.get('status') == 'issues_found':
            print("RECOMMENDATIONS:")
            print("1. Review flagged mathematical contradictions above")
            print("2. Verify calculations in affected questions")
            print("3. Ensure consistency between declared answers and feedback")
            
            if any(c.severity == "severe" for c in self.math_detector.contradictions_found):
                print("4. PRIORITY: Address severe contradictions immediately")
            
            print("")


def main():
    """Main entry point for Q2JSON processing"""
    
    parser = argparse.ArgumentParser(
        description="Q2JSON Processing Pipeline with Mathematical Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.json                    # Full processing with math checking
  python main.py input.json -o output.json     # Process and save to specific output
  python main.py input.json --no-math-check    # Skip mathematical validation
  python main.py input.json --no-latex-fix     # Skip LaTeX correction
  python main.py input.json -q                 # Quiet mode (minimal output)
        """
    )
    
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('-o', '--output', help='Output JSON file path (default: input_processed.json)')
    parser.add_argument('--no-math-check', action='store_true', 
                       help='Skip mathematical consistency checking')
    parser.add_argument('--no-latex-fix', action='store_true',
                       help='Skip LaTeX correction')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (minimal output)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    # Set default output file if not specified
    output_file = args.output
    if not output_file:
        input_path = Path(args.input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_processed{input_path.suffix}")
    
    # Initialize and run pipeline
    pipeline = Q2JSONPipeline()
    
    results = pipeline.process_file(
        input_file=args.input_file,
        output_file=output_file,
        check_math=not args.no_math_check,
        fix_latex=not args.no_latex_fix,
        verbose=not args.quiet
    )
    
    # Exit with appropriate status codes
    if results['status'] == 'completed':
        # Check for mathematical issues
        math_results = results.get('mathematical_validation', {})
        if math_results.get('status') == 'issues_found':
            if pipeline.math_detector.has_severe_contradictions():
                sys.exit(2)  # Severe mathematical issues
            else:
                sys.exit(1)  # Minor/moderate mathematical issues
        else:
            sys.exit(0)  # Success
    else:
        sys.exit(3)  # Processing error


if __name__ == "__main__":
    main()