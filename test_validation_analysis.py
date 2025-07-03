#!/usr/bin/env python3
"""
Q2JSON Stage 4 JSON Validation Analysis Script
Phase 1: Diagnostic Analysis

This script analyzes the current JSON validation implementation to identify
why educational content creates false positives.

Usage: python test_validation_analysis.py
"""

import json
import sys
import os
from pathlib import Path
import re

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from modules.json_processor import JSONProcessor
except ImportError:
    print("Could not import JSONProcessor. Checking alternative paths...")
    # Try to find the module in different locations
    possible_paths = [
        'modules',
        'q2json_components',
        '.'
    ]
    for path in possible_paths:
        if os.path.exists(os.path.join(path, 'json_processor.py')):
            sys.path.append(path)
            try:
                from json_processor import JSONProcessor
                print(f"Found JSONProcessor in {path}")
                break
            except ImportError:
                continue
    else:
        print("JSONProcessor not found. Creating a mock version for analysis.")
        JSONProcessor = None

def analyze_latex_patterns(text):
    """Analyze LaTeX patterns in the text that might cause validation issues."""
    patterns = {
        'math_expressions': re.findall(r'\$[^$]+\$', text),
        'subscripts': re.findall(r'[A-Za-z]_\{[^}]+\}', text),
        'superscripts': re.findall(r'[A-Za-z]\^?\{[^}]+\}', text),
        'greek_letters': re.findall(r'\\[a-zA-Z]+', text),
        'mathematical_functions': re.findall(r'\\(?:sqrt|text|times|approx|Delta)\{[^}]*\}', text),
        'units_notation': re.findall(r',text\{[^}]+\}', text),
        'special_chars': re.findall(r'[\$_\^\\{}]', text)
    }
    return patterns

def analyze_educational_content_patterns(data):
    """Analyze educational content patterns that might trigger false positives."""
    patterns_found = {
        'latex_expressions': [],
        'mathematical_notation': [],
        'units_and_measurements': [],
        'scientific_notation': [],
        'special_characters': []
    }
    
    def extract_text_fields(obj, path=""):
        """Recursively extract text fields from JSON object."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    # Analyze this text field
                    latex_patterns = analyze_latex_patterns(value)
                    if any(latex_patterns.values()):
                        patterns_found['latex_expressions'].append({
                            'field': new_path,
                            'content': value,
                            'patterns': latex_patterns
                        })
                    
                    # Check for other educational patterns
                    if re.search(r'\d+\.?\d*\s*\\?text\{[^}]+\}', value):
                        patterns_found['units_and_measurements'].append({
                            'field': new_path,
                            'content': value
                        })
                    
                    if re.search(r'\\approx|\\times|\\Delta', value):
                        patterns_found['mathematical_notation'].append({
                            'field': new_path,
                            'content': value
                        })
                
                extract_text_fields(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                extract_text_fields(item, f"{path}[{i}]")
    
    extract_text_fields(data)
    return patterns_found

def test_json_validation():
    """Test JSON validation with the MosfetQQDebug.json file."""
    
    # Path to the test file
    test_file_path = r"c:\Users\aknoesen\Documents\Knoesen\Database for EEC1\Debug Problem Cases\MosfetQQDebug.json"
    
    print("="*80)
    print("Q2JSON STAGE 4 JSON VALIDATION ANALYSIS - PHASE 1")
    print("="*80)
    print(f"Test file: {test_file_path}")
    print()
    
    # Check if test file exists
    if not os.path.exists(test_file_path):
        print(f"ERROR: Test file not found at {test_file_path}")
        return False
    
    # Load the test data
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        print(f"✅ Successfully loaded test data ({len(test_data.get('questions', []))} questions)")
    except Exception as e:
        print(f"❌ Failed to load test data: {e}")
        return False
    
    # Analyze educational content patterns
    print("\n" + "="*60)
    print("TASK 3: EDUCATIONAL CONTENT PATTERN ANALYSIS")
    print("="*60)
    
    patterns = analyze_educational_content_patterns(test_data)
    
    print(f"\nFound {len(patterns['latex_expressions'])} fields with LaTeX expressions:")
    for item in patterns['latex_expressions'][:5]:  # Show first 5
        print(f"  Field: {item['field']}")
        print(f"  Content snippet: {item['content'][:100]}...")
        print(f"  Patterns: {item['patterns']}")
        print()
    
    print(f"\nFound {len(patterns['units_and_measurements'])} fields with units/measurements:")
    for item in patterns['units_and_measurements'][:3]:  # Show first 3
        print(f"  Field: {item['field']}")
        print(f"  Content: {item['content'][:150]}...")
        print()
    
    print(f"\nFound {len(patterns['mathematical_notation'])} fields with mathematical notation:")
    for item in patterns['mathematical_notation'][:3]:  # Show first 3
        print(f"  Field: {item['field']}")
        print(f"  Content: {item['content'][:150]}...")
        print()
    
    # Test with JSONProcessor if available
    if JSONProcessor:
        print("\n" + "="*60)
        print("TASK 2: CURRENT VALIDATION TESTING")
        print("="*60)
        
        try:
            processor = JSONProcessor()
            print("✅ JSONProcessor initialized successfully")
            
            # Test validation using the correct method
            print("\nTesting JSON validation...")
            validation_results = processor.validate_questions(test_data)
            
            print(f"Validation Results:")
            print(f"  Total questions: {validation_results.get('total', 0)}")
            print(f"  Valid: {validation_results.get('valid', 0)}")
            print(f"  Warnings: {validation_results.get('warnings', 0)}")
            print(f"  Errors: {validation_results.get('errors', 0)}")
            
            # Show Unicode violations (these are typically FALSE POSITIVES)
            if validation_results.get('unicode_violations'):
                print(f"\n❌ Unicode violations found: {len(validation_results['unicode_violations'])}")
                print("These are likely FALSE POSITIVES for educational content:")
                for violation in validation_results['unicode_violations'][:5]:
                    print(f"  - {violation}")
                if len(validation_results['unicode_violations']) > 5:
                    print(f"  ... and {len(validation_results['unicode_violations']) - 5} more violations")
            
            # Show LaTeX issues (these may be FALSE POSITIVES)
            if validation_results.get('latex_issues'):
                print(f"\n⚠️ LaTeX issues found: {len(validation_results['latex_issues'])}")
                print("These may be FALSE POSITIVES for educational content:")
                for issue in validation_results['latex_issues'][:5]:
                    print(f"  - {issue}")
                if len(validation_results['latex_issues']) > 5:
                    print(f"  ... and {len(validation_results['latex_issues']) - 5} more issues")
            
            # PHASE 3: Show Mathematical Consistency Results
            math_results = validation_results.get('mathematical_consistency', {})
            if math_results.get('contradictions_found', 0) > 0:
                print(f"\n🎯 Mathematical consistency issues found: {math_results['contradictions_found']}")
                print("These are REAL CONTENT CONTRADICTIONS:")
                for contradiction in math_results.get('contradictions', []):
                    print(f"  - Q{contradiction['question_index']}: {contradiction['question_title']}")
                    print(f"    Declared: {contradiction['declared_answer']} vs Found: {contradiction['found_value']}")
                    print(f"    Difference: {contradiction['difference_percent']}% ({contradiction['severity']})")
                    print(f"    Context: {contradiction['context'][:60]}...")
            else:
                print(f"\n✅ Mathematical consistency: No contradictions detected")
                if math_results.get('numerical_questions', 0) > 0:
                    print(f"   Checked {math_results['numerical_questions']} numerical questions")
                print("Note: This includes checking for the known 0.776 vs 0.812 issue in Question 8")
            
            # Show detailed question analysis for problems
            if validation_results.get('question_analysis'):
                problem_questions = [q for q in validation_results['question_analysis'] 
                                   if q['status'] != 'valid']
                if problem_questions:
                    print(f"\n🔍 Questions flagged as problematic: {len(problem_questions)}")
                    for q in problem_questions[:3]:  # Show first 3
                        print(f"  Q{q['index']}: {q['title']} - Status: {q['status']}")
                        for issue in q.get('issues', [])[:2]:
                            print(f"    Issue: {issue}")
                        for violation in q.get('unicode_violations', [])[:2]:
                            print(f"    Unicode: {violation}")
                        for latex_issue in q.get('latex_issues', [])[:2]:
                            print(f"    LaTeX: {latex_issue}")
                        for math_issue in q.get('mathematical_issues', [])[:2]:
                            print(f"    Mathematical: {math_issue}")
                        print()
            
            # PHASE 3: Complete Three-Tier Validation Summary
            print(f"\n" + "="*60)
            print("COMPLETE THREE-TIER VALIDATION SUMMARY")
            print("="*60)
            
            total_questions = validation_results.get('total', 0)
            questions_with_warnings = 0
            questions_fully_valid = 0
            
            print(f"Total Questions Analyzed: {total_questions}")
            print(f"\n📊 VALIDATION BREAKDOWN:")
            
            # Structure validation
            structure_errors = validation_results.get('errors', 0)
            print(f"  🏗️  Structure: {total_questions - structure_errors}/{total_questions} valid")
            if structure_errors > 0:
                print(f"      {structure_errors} questions have structural errors")
            
            # LaTeX validation  
            latex_issues_count = len(validation_results.get('latex_issues', []))
            questions_with_latex_issues = len([q for q in validation_results.get('question_analysis', []) if q.get('latex_issues')])
            print(f"  📝 LaTeX: {total_questions - questions_with_latex_issues}/{total_questions} valid")
            if latex_issues_count > 0:
                print(f"      {questions_with_latex_issues} questions have LaTeX syntax warnings")
            
            # Mathematical consistency
            math_results = validation_results.get('mathematical_consistency', {})
            math_contradictions = math_results.get('contradictions_found', 0)
            numerical_questions = math_results.get('numerical_questions', 0)
            print(f"  🧮 Mathematical: {numerical_questions - math_contradictions}/{numerical_questions} numerical questions consistent")
            if math_contradictions > 0:
                print(f"      {math_contradictions} questions have mathematical contradictions")
            
            # Overall status
            print(f"\n🎯 OVERALL STATUS:")
            questions_with_any_issues = len([q for q in validation_results.get('question_analysis', []) 
                                           if q.get('status') != 'valid'])
            questions_fully_valid = total_questions - questions_with_any_issues
            
            print(f"  ✅ Fully Valid: {questions_fully_valid} questions")
            print(f"  ⚠️  With Warnings: {questions_with_any_issues} questions")
            print(f"  ❌ With Errors: {structure_errors} questions")
            
            if questions_with_any_issues > 0:
                print(f"\n📋 QUESTIONS WITH ISSUES:")
                for q in validation_results.get('question_analysis', []):
                    if q.get('status') != 'valid':
                        issues_summary = []
                        if q.get('latex_issues'):
                            issues_summary.append(f"LaTeX ({len(q['latex_issues'])})")
                        if q.get('mathematical_issues'):
                            issues_summary.append(f"Mathematical ({len(q['mathematical_issues'])})")
                        if q.get('issues'):
                            issues_summary.append(f"Structural ({len(q['issues'])})")
                        
                        print(f"  Q{q['index']}: {q['title'][:40]}... - {', '.join(issues_summary)}")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Error testing validation: {e}")
            print("This indicates the validation system may have issues with educational content")
            import traceback
            traceback.print_exc()
            return None
    
    else:
        print("\n" + "="*60)
        print("TASK 1: VALIDATION CODE LOCATION")
        print("="*60)
        print("❌ JSONProcessor not found in expected locations")
        print("Searching for validation-related files...")
        
        # Search for validation files
        search_paths = [
            "modules",
            "stages", 
            "q2json_components",
            "extracted_components",
            "."
        ]
        
        validation_files = []
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith('.py') and ('valid' in file.lower() or 'json' in file.lower()):
                            validation_files.append(os.path.join(root, file))
        
        print(f"Found {len(validation_files)} potential validation files:")
        for file in validation_files:
            print(f"  - {file}")
    
    # Summary of findings
    print("\n" + "="*60)
    print("PHASE 1 ANALYSIS SUMMARY")
    print("="*60)
    
    total_latex = len(patterns['latex_expressions'])
    total_math = len(patterns['mathematical_notation'])
    total_units = len(patterns['units_and_measurements'])
    
    print(f"Educational Content Analysis:")
    print(f"  - LaTeX expressions found: {total_latex}")
    print(f"  - Mathematical notation instances: {total_math}")
    print(f"  - Units/measurements patterns: {total_units}")
    print(f"  - Total educational patterns: {total_latex + total_math + total_units}")
    
    print(f"\nCritical Patterns That May Cause False Positives:")
    
    # Extract specific problematic patterns
    problematic_patterns = []
    for item in patterns['latex_expressions']:
        for pattern_type, pattern_list in item['patterns'].items():
            if pattern_list:
                problematic_patterns.extend(pattern_list)
    
    unique_patterns = list(set(problematic_patterns))[:10]
    for i, pattern in enumerate(unique_patterns, 1):
        print(f"  {i}. {pattern}")
    
    print(f"\n🎯 NEXT STEPS FOR PHASE 2:")
    print(f"  1. Fix validation rules that reject LaTeX expressions like: {unique_patterns[0] if unique_patterns else 'N/A'}")
    print(f"  2. Allow mathematical notation patterns")
    print(f"  3. Support educational units format (\\text{{V}}, \\text{{mS}}, etc.)")
    print(f"  4. Test fixes with this educational content")
    
    return True

if __name__ == "__main__":
    success = test_json_validation()
    sys.exit(0 if success else 1)
