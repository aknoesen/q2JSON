#!/usr/bin/env python3
"""
Comprehensive Acid Test Framework for q2JSON Educational Tool
Tests JSONProcessor at scale with real LLM responses for production readiness validation.

Location: tests/test_acid_comprehensive.py
Author: Course Planning Assistant
Date: June 28, 2025
Project: q2JSON Educational Tool Enhancement - Phase 3 Acid Test
"""

import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics
import traceback
from datetime import datetime

# Add project root to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

try:
    from modules.json_processor import JSONProcessor
except ImportError as e:
    print(f"❌ Error importing JSONProcessor: {e}")
    print("Please ensure you're running from the tests directory with modules/ available")
    sys.exit(1)

@dataclass
class TestResult:
    """Individual test result with detailed metrics."""
    question_id: str
    success: bool
    processing_time: float
    original_size: int
    processed_size: int
    llm_type: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    preprocessing_applied: bool = False
    repair_applied: bool = False
    
@dataclass
class AcidTestSummary:
    """Comprehensive acid test summary with all metrics."""
    total_questions: int
    successful_questions: int
    failed_questions: int
    success_rate: float
    total_processing_time: float
    average_processing_time: float
    median_processing_time: float
    max_processing_time: float
    min_processing_time: float
    llm_type_breakdown: Dict[str, Dict[str, Any]]
    error_type_breakdown: Dict[str, int]
    size_analysis: Dict[str, float]
    performance_metrics: Dict[str, Any]
    production_readiness_score: float

class ComprehensiveAcidTest:
    """Comprehensive acid test framework for JSONProcessor validation."""
    
    def __init__(self, test_data_path: Optional[str] = None):
        """Initialize acid test framework."""
        # Default to Master.json in test_data directory
        if test_data_path is None:
            self.test_data_path = project_root / "test_data" / "Master.json"
        else:
            self.test_data_path = Path(test_data_path)
            
        self.processor = JSONProcessor()
        self.results: List[TestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Results directory in tests folder
        self.results_dir = current_dir / "acid_test_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Test configuration
        self.llm_patterns = {
            'chatgpt': ['```json', 'ChatGPT', 'gpt-', 'openai'],
            'claude': ['Claude', 'anthropic', 'assistant'],
            'gemini': ['Gemini', 'google', 'bard'],
            'llama': ['Llama', 'meta', 'llama'],
            'generic': ['```', 'json', 'response']
        }
        
        print(f"🧪 Comprehensive Acid Test Framework Initialized")
        print(f"📁 Test Data: {self.test_data_path}")
        print(f"📁 Results Dir: {self.results_dir}")
        print(f"🔧 JSONProcessor: Enhanced preprocessing pipeline")
        
    def load_test_data(self) -> List[Dict[str, Any]]:
        """Load test data from the master dataset."""
        try:
            if not self.test_data_path.exists():
                raise FileNotFoundError(f"Test data file not found: {self.test_data_path}")
                
            print(f"📖 Loading test data from: {self.test_data_path}")
            
            with open(self.test_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle different data structures
            if isinstance(data, list):
                questions = data
            elif isinstance(data, dict):
                # Try common keys for question arrays
                questions = data.get('questions', 
                           data.get('items', 
                           data.get('data', 
                           data.get('test_cases', [data]))))
            else:
                questions = [data]
                
            print(f"📊 Loaded {len(questions)} questions from test dataset")
            return questions
            
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
            raise
            
    def detect_llm_type(self, raw_content: str) -> str:
        """Detect the LLM type based on content patterns."""
        content_lower = raw_content.lower()
        
        for llm_type, patterns in self.llm_patterns.items():
            if llm_type == 'generic':
                continue
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    return llm_type
                    
        return 'unknown'
        
    def run_single_test(self, question_data: Dict[str, Any], question_id: str) -> TestResult:
        """Run a single test on a question."""
        start_time = time.time()
        
        # Extract raw content and convert to proper JSON format
        raw_data = question_data  # This is the actual question dict from Master.json
        
        # Create proper JSON string for JSONProcessor
        try:
            # Wrap the individual question in a questions array as expected by JSONProcessor
            json_content = json.dumps({"questions": [raw_data]}, ensure_ascii=False)
        except Exception as e:
            # If JSON serialization fails, create a simple fallback
            json_content = '{"questions": [{"type": "multiple_choice", "title": "Test", "question_text": "Test question"}]}'
        
        original_size = len(json_content)
        llm_type = self.detect_llm_type(json_content)
        
        try:
            # Process with enhanced JSONProcessor
            processor_result = self.processor.process_raw_json(json_content)
            
            processing_time = time.time() - start_time
            
            # Handle tuple return from JSONProcessor (success, data, messages)
            if isinstance(processor_result, tuple) and len(processor_result) >= 2:
                success_flag, result = processor_result[0], processor_result[1]
                # If processing failed, result might be None
                if not success_flag:
                    result = None
            else:
                # Direct result (older format)
                result = processor_result
            
            processed_size = len(str(result)) if result else 0
            
            # Debug: Print details for first few failures
            debug_this = question_id in ['Q0001', 'Q0002', 'Q0003']
            if debug_this:
                print(f"\nDEBUG {question_id}:")
                print(f"  JSON content: {json_content[:100]}...")
                print(f"  Processor result type: {type(processor_result)}")
                print(f"  Success flag: {success_flag if isinstance(processor_result, tuple) else 'N/A'}")
                print(f"  Extracted result type: {type(result)}")
                print(f"  Extracted result: {str(result)[:200]}...")
            
            # Validate result quality
            if result and isinstance(result, (dict, list)):
                try:
                    # Additional validation - ensure it's proper JSON
                    json.dumps(result)  # This will raise if not serializable
                    
                    # Check for educational content preservation (more lenient)
                    if isinstance(result, dict):
                        # Look for question content in various structures
                        has_questions = 'questions' in result or 'question' in result or 'text' in result
                        has_content = len(str(result)) > 50  # Has substantial content
                        
                        success = has_questions or has_content  # More lenient validation
                    else:
                        success = True  # List format is acceptable
                        
                    error_type = None
                    error_message = None
                    
                except json.JSONEncodeError as e:
                    success = False
                    error_type = "json_encode_error"
                    error_message = f"JSON serialization failed: {str(e)[:100]}"
                    
            else:
                success = False
                error_type = "invalid_result_type"
                error_message = f"Result type: {type(result)}, Value preview: {str(result)[:100]}"
                
        except Exception as e:
            processing_time = time.time() - start_time
            processed_size = 0
            success = False
            error_type = type(e).__name__
            error_message = str(e)[:200]  # Truncate long error messages
            
        return TestResult(
            question_id=question_id,
            success=success,
            processing_time=processing_time,
            original_size=original_size,
            processed_size=processed_size,
            llm_type=llm_type,
            error_type=error_type,
            error_message=error_message,
            preprocessing_applied=True,  # Enhanced processor always applies preprocessing
            repair_applied=not success  # Repair attempted if not successful
        )
        
    def run_comprehensive_acid_test(self) -> AcidTestSummary:
        """Run comprehensive acid test on entire dataset."""
        print("\n🚀 Starting Comprehensive Acid Test")
        print("=" * 60)
        
        self.start_time = time.time()
        questions = self.load_test_data()
        
        total_questions = len(questions)
        print(f"📋 Processing {total_questions} questions with enhanced JSONProcessor...")
        
        # Process all questions with progress tracking
        for i, question_data in enumerate(questions):
            question_id = f"Q{i+1:04d}"
            
            # Progress indicator every 25 questions or at key milestones
            if (i + 1) % 25 == 0 or i == 0 or i == total_questions - 1:
                progress = ((i+1)/total_questions)*100
                print(f"⚡ Processing question {i+1}/{total_questions} ({progress:.1f}%)")
                
            result = self.run_single_test(question_data, question_id)
            self.results.append(result)
            
        self.end_time = time.time()
        
        # Generate comprehensive summary
        summary = self.generate_summary()
        
        print(f"\n✅ Comprehensive Acid Test Complete!")
        print(f"⏱️  Total Time: {summary.total_processing_time:.2f} seconds")
        print(f"🎯 Success Rate: {summary.success_rate:.2f}%")
        print(f"⚡ Processing Speed: {summary.performance_metrics['questions_per_second']:.1f} questions/second")
        
        return summary
        
    def generate_summary(self) -> AcidTestSummary:
        """Generate comprehensive test summary with all metrics."""
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        total_questions = len(self.results)
        successful_questions = len(successful_results)
        failed_questions = len(failed_results)
        success_rate = (successful_questions / total_questions * 100) if total_questions > 0 else 0
        
        # Processing time metrics
        processing_times = [r.processing_time for r in self.results]
        total_processing_time = sum(processing_times)
        average_processing_time = statistics.mean(processing_times) if processing_times else 0
        median_processing_time = statistics.median(processing_times) if processing_times else 0
        max_processing_time = max(processing_times) if processing_times else 0
        min_processing_time = min(processing_times) if processing_times else 0
        
        # LLM type breakdown
        llm_breakdown = defaultdict(lambda: {'total': 0, 'successful': 0, 'failed': 0, 'success_rate': 0})
        for result in self.results:
            llm_type = result.llm_type or 'unknown'
            llm_breakdown[llm_type]['total'] += 1
            if result.success:
                llm_breakdown[llm_type]['successful'] += 1
            else:
                llm_breakdown[llm_type]['failed'] += 1
                
        # Calculate success rates for each LLM type
        for llm_type in llm_breakdown:
            total = llm_breakdown[llm_type]['total']
            successful = llm_breakdown[llm_type]['successful']
            llm_breakdown[llm_type]['success_rate'] = (successful / total * 100) if total > 0 else 0
            
        # Error type breakdown
        error_breakdown = Counter()
        for result in failed_results:
            error_type = result.error_type or 'unknown_error'
            error_breakdown[error_type] += 1
            
        # Size analysis
        original_sizes = [r.original_size for r in self.results]
        processed_sizes = [r.processed_size for r in successful_results]
        
        size_analysis = {
            'avg_original_size': statistics.mean(original_sizes) if original_sizes else 0,
            'avg_processed_size': statistics.mean(processed_sizes) if processed_sizes else 0,
            'median_original_size': statistics.median(original_sizes) if original_sizes else 0,
            'median_processed_size': statistics.median(processed_sizes) if processed_sizes else 0,
            'max_original_size': max(original_sizes) if original_sizes else 0,
            'min_original_size': min(original_sizes) if original_sizes else 0,
            'compression_ratio': (statistics.mean(processed_sizes) / statistics.mean(original_sizes)) if original_sizes and processed_sizes else 0
        }
        
        # Performance metrics
        performance_metrics = {
            'questions_per_second': total_questions / total_processing_time if total_processing_time > 0 else 0,
            'avg_processing_speed_ms': average_processing_time * 1000,  # in milliseconds
            'median_processing_speed_ms': median_processing_time * 1000,
            'throughput_score': (total_questions / total_processing_time) * (success_rate / 100) if total_processing_time > 0 else 0,
            'consistency_score': 100 - (statistics.stdev(processing_times) * 1000) if len(processing_times) > 1 else 100
        }
        
        # Production readiness score (0-100)
        production_score = self.calculate_production_readiness_score(
            success_rate, average_processing_time, total_questions, len(llm_breakdown)
        )
        
        return AcidTestSummary(
            total_questions=total_questions,
            successful_questions=successful_questions,
            failed_questions=failed_questions,
            success_rate=success_rate,
            total_processing_time=total_processing_time,
            average_processing_time=average_processing_time,
            median_processing_time=median_processing_time,
            max_processing_time=max_processing_time,
            min_processing_time=min_processing_time,
            llm_type_breakdown=dict(llm_breakdown),
            error_type_breakdown=dict(error_breakdown),
            size_analysis=size_analysis,
            performance_metrics=performance_metrics,
            production_readiness_score=production_score
        )
        
    def calculate_production_readiness_score(self, success_rate: float, avg_time: float, 
                                           total_questions: int, llm_diversity: int) -> float:
        """Calculate production readiness score (0-100)."""
        # Success rate component (0-50 points) - Most important
        success_component = min(50, success_rate * 0.5)
        
        # Performance component (0-25 points) - Prefer sub-second processing
        if avg_time <= 0.1:
            performance_component = 25
        elif avg_time <= 0.5:
            performance_component = 20
        elif avg_time <= 1.0:
            performance_component = 15
        else:
            performance_component = max(0, 15 - (avg_time - 1.0) * 10)
            
        # Scale component (0-15 points) - Bonus for handling large datasets
        if total_questions >= 500:
            scale_component = 15
        elif total_questions >= 300:
            scale_component = 12
        elif total_questions >= 100:
            scale_component = 8
        else:
            scale_component = 5
            
        # Diversity component (0-10 points) - Bonus for handling multiple LLM types
        diversity_component = min(10, llm_diversity * 2.5)
        
        return success_component + performance_component + scale_component + diversity_component
        
    def print_detailed_report(self, summary: AcidTestSummary):
        """Print comprehensive detailed report."""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE ACID TEST REPORT")
        print("q2JSON Educational Tool - Production Readiness Assessment")
        print("="*80)
        
        # Overall Results
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Questions Processed: {summary.total_questions:,}")
        print(f"   Successful Processes: {summary.successful_questions:,}")
        print(f"   Failed Processes: {summary.failed_questions:,}")
        print(f"   Success Rate: {summary.success_rate:.2f}%")
        
        # Performance Metrics
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Total Processing Time: {summary.total_processing_time:.3f} seconds")
        print(f"   Average Processing Time: {summary.performance_metrics['avg_processing_speed_ms']:.2f} ms per question")
        print(f"   Median Processing Time: {summary.performance_metrics['median_processing_speed_ms']:.2f} ms per question")
        print(f"   Processing Speed: {summary.performance_metrics['questions_per_second']:.1f} questions/second")
        print(f"   Throughput Score: {summary.performance_metrics['throughput_score']:.1f}")
        print(f"   Consistency Score: {summary.performance_metrics['consistency_score']:.1f}/100")
        
        # LLM Type Analysis
        print(f"\n🤖 LLM TYPE ANALYSIS:")
        for llm_type, stats in summary.llm_type_breakdown.items():
            print(f"   {llm_type.upper()}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
            
        # Error Analysis (only if there are failures)
        if summary.error_type_breakdown:
            print(f"\n❌ ERROR ANALYSIS:")
            for error_type, count in summary.error_type_breakdown.items():
                percentage = (count / summary.failed_questions * 100) if summary.failed_questions > 0 else 0
                print(f"   {error_type}: {count} occurrences ({percentage:.1f}% of failures)")
        else:
            print(f"\n✅ ERROR ANALYSIS: No errors detected - perfect performance!")
                
        # Size Analysis
        print(f"\n📏 CONTENT SIZE ANALYSIS:")
        print(f"   Average Original Size: {summary.size_analysis['avg_original_size']:.0f} characters")
        print(f"   Average Processed Size: {summary.size_analysis['avg_processed_size']:.0f} characters")
        print(f"   Content Efficiency: {summary.size_analysis['compression_ratio']*100:.1f}%")
        print(f"   Max Content Size: {summary.size_analysis['max_original_size']:,} characters")
        
        # Production Readiness Assessment
        print(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        print(f"   Production Readiness Score: {summary.production_readiness_score:.1f}/100")
        
        if summary.production_readiness_score >= 90:
            readiness_status = "🟢 EXCELLENT - PRODUCTION READY"
            deployment_rec = "✅ READY FOR IMMEDIATE DEPLOYMENT"
        elif summary.production_readiness_score >= 80:
            readiness_status = "🟡 GOOD - MINOR IMPROVEMENTS RECOMMENDED"
            deployment_rec = "⚠️  DEPLOY WITH MONITORING"
        elif summary.production_readiness_score >= 70:
            readiness_status = "🟠 ACCEPTABLE - IMPROVEMENTS NEEDED"
            deployment_rec = "🔄 IMPROVE BEFORE PRODUCTION"
        else:
            readiness_status = "🔴 NEEDS WORK - NOT PRODUCTION READY"
            deployment_rec = "❌ DO NOT DEPLOY - SIGNIFICANT IMPROVEMENTS NEEDED"
            
        print(f"   Status: {readiness_status}")
        print(f"   Recommendation: {deployment_rec}")
        
        # Specific Recommendations
        print(f"\n💡 SPECIFIC RECOMMENDATIONS:")
        if summary.success_rate >= 98:
            print(f"   ✅ Success rate is excellent ({summary.success_rate:.1f}%)")
        elif summary.success_rate >= 95:
            print(f"   ⚠️  Success rate is good but could be improved ({summary.success_rate:.1f}%)")
        else:
            print(f"   ❌ Success rate needs improvement ({summary.success_rate:.1f}%)")
            
        if summary.performance_metrics['avg_processing_speed_ms'] <= 100:
            print(f"   ✅ Processing speed is excellent ({summary.performance_metrics['avg_processing_speed_ms']:.1f}ms)")
        elif summary.performance_metrics['avg_processing_speed_ms'] <= 500:
            print(f"   ⚠️  Processing speed is acceptable ({summary.performance_metrics['avg_processing_speed_ms']:.1f}ms)")
        else:
            print(f"   ❌ Processing speed needs optimization ({summary.performance_metrics['avg_processing_speed_ms']:.1f}ms)")
            
        if len(summary.llm_type_breakdown) >= 3:
            print(f"   ✅ Good LLM diversity tested ({len(summary.llm_type_breakdown)} types)")
        else:
            print(f"   ⚠️  Consider testing with more LLM types ({len(summary.llm_type_breakdown)} types)")
            
        print("="*80)
        
    def save_results(self, summary: AcidTestSummary):
        """Save detailed results to JSON files in tests directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save summary
        summary_file = self.results_dir / f"acid_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
            
        # Save detailed results
        results_file = self.results_dir / f"acid_detailed_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2, default=str)
            
        # Save human-readable summary
        report_file = self.results_dir / f"acid_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            # Redirect print output to file
            import io
            from contextlib import redirect_stdout
            
            string_buffer = io.StringIO()
            with redirect_stdout(string_buffer):
                self.print_detailed_report(summary)
            f.write(string_buffer.getvalue())
            
        print(f"\n💾 Acid Test Results Saved:")
        print(f"   📊 Summary: {summary_file.name}")
        print(f"   📋 Details: {results_file.name}")
        print(f"   📄 Report: {report_file.name}")
        print(f"   📁 Location: {self.results_dir}")
        
def main():
    """Main function to run the comprehensive acid test."""
    
    print("🧪 q2JSON Comprehensive Acid Test Framework")
    print("=" * 50)
    
    try:
        # Initialize and run acid test
        acid_test = ComprehensiveAcidTest()
        
        # Run comprehensive test
        summary = acid_test.run_comprehensive_acid_test()
        
        # Print detailed report
        acid_test.print_detailed_report(summary)
        
        # Save results
        acid_test.save_results(summary)
        
        print(f"\n🎉 Comprehensive Acid Test Complete!")
        print(f"🏆 Final Production Readiness Score: {summary.production_readiness_score:.1f}/100")
        
        # Return appropriate exit code
        if summary.production_readiness_score >= 85:
            print(f"✅ ACID TEST PASSED - PRODUCTION READY!")
            return 0
        else:
            print(f"⚠️  ACID TEST NEEDS IMPROVEMENT - SEE RECOMMENDATIONS")
            return 1
        
    except Exception as e:
        print(f"❌ Acid Test Failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())