#!/usr/bin/env python3
"""
Systematic LLM Testing Framework for q2JSON
Comprehensive validation across multiple LLM providers and output patterns.

Author: Course Planning Assistant  
Date: June 28, 2025
Purpose: Ensure production readiness across all major LLM providers
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Test data structure for LLM-specific testing
@dataclass
class LLMTestCase:
    """Individual LLM test case with provider-specific metadata."""
    llm_provider: str
    model_version: str
    prompt_used: str
    raw_response: str
    expected_questions: int
    test_category: str  # "basic", "complex", "edge_case", "malformed"
    test_date: str
    notes: str = ""

@dataclass
class LLMTestSuite:
    """Complete test suite for systematic LLM validation."""
    provider_name: str
    model_versions: List[str]
    test_cases: List[LLMTestCase]
    success_rate: float = 0.0
    avg_processing_time: float = 0.0
    reliability_score: int = 0

class SystematicLLMTester:
    """Framework for systematic testing across LLM providers."""
    
    def __init__(self):
        self.test_suites: Dict[str, LLMTestSuite] = {}
        self.results_dir = Path("tests/llm_systematic_testing")
        self.results_dir.mkdir(exist_ok=True)
        
        # Define comprehensive test matrix
        self.target_providers = {
            "claude": {
                "versions": ["claude-3.5-sonnet", "claude-3-opus", "claude-3-haiku"],
                "test_priority": "high",  # Your primary LLM
                "current_coverage": "good"
            },
            "gemini": {
                "versions": ["gemini-1.5-pro", "gemini-1.0-pro", "gemini-flash"],
                "test_priority": "high",  # Your secondary LLM
                "current_coverage": "good"
            },
            "chatgpt": {
                "versions": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                "test_priority": "critical",  # Major gap in testing
                "current_coverage": "minimal"
            },
            "copilot": {
                "versions": ["copilot-gpt4", "copilot-web", "copilot-campus"],
                "test_priority": "high",  # Campus environments
                "current_coverage": "none"
            },
            "llama": {
                "versions": ["llama-3.1-70b", "llama-3.1-8b", "code-llama"],
                "test_priority": "medium",  # Open source
                "current_coverage": "none"
            },
            "perplexity": {
                "versions": ["perplexity-pro", "perplexity-standard"],
                "test_priority": "medium",  # Search-enhanced
                "current_coverage": "none"
            }
        }
        
        # Test categories for comprehensive coverage
        self.test_categories = {
            "basic": "Standard educational questions, clean format",
            "complex": "Multi-part questions with LaTeX and metadata",
            "edge_case": "Unusual formatting, long content, special characters",
            "malformed": "Broken JSON, markdown blocks, mixed content",
            "multilingual": "Non-English content, Unicode characters",
            "mathematical": "Heavy LaTeX, equations, scientific notation"
        }
        
    def generate_test_plan(self) -> Dict[str, Any]:
        """Generate systematic testing plan for all LLM providers."""
        
        test_plan = {
            "total_providers": len(self.target_providers),
            "total_test_cases_needed": 0,
            "priority_breakdown": {},
            "coverage_gaps": [],
            "recommended_test_sequence": []
        }
        
        # Analyze current gaps and priorities
        for provider, info in self.target_providers.items():
            test_cases_needed = len(info["versions"]) * len(self.test_categories) * 3  # 3 samples per category
            test_plan["total_test_cases_needed"] += test_cases_needed
            
            priority = info["test_priority"]
            if priority not in test_plan["priority_breakdown"]:
                test_plan["priority_breakdown"][priority] = []
            test_plan["priority_breakdown"][priority].append({
                "provider": provider,
                "cases_needed": test_cases_needed,
                "current_coverage": info["current_coverage"]
            })
            
            # Identify gaps
            if info["current_coverage"] in ["none", "minimal"]:
                test_plan["coverage_gaps"].append({
                    "provider": provider,
                    "priority": priority,
                    "gap_severity": "critical" if info["current_coverage"] == "none" else "major"
                })
        
        # Recommended testing sequence (priority order)
        test_plan["recommended_test_sequence"] = [
            "1. ChatGPT (Critical Gap - Major Provider)",
            "2. Microsoft Copilot (High Priority - Campus Use)",
            "3. Llama Models (Open Source Validation)", 
            "4. Perplexity (Search-Enhanced Responses)",
            "5. Extended Claude Testing (Additional Versions)",
            "6. Extended Gemini Testing (Additional Versions)"
        ]
        
        return test_plan
        
    def create_test_collection_protocol(self) -> Dict[str, Any]:
        """Protocol for systematically collecting LLM test cases."""
        
        protocol = {
            "data_collection_strategy": {
                "prompt_standardization": "Use identical prompts across all LLMs",
                "response_collection": "Capture raw, unedited LLM outputs",
                "metadata_tracking": "Record model version, timestamp, prompt used",
                "sample_size": "Minimum 3 samples per category per provider",
                "diversity_requirements": "Include various educational subjects"
            },
            
            "test_prompts": {
                "basic_educational": """
Create 3 multiple choice questions about basic algebra for 9th grade students. 
Return as JSON with this structure:
{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Question Title",
      "question_text": "Question content",
      "choices": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "points": 2
    }
  ]
}
""",
                
                "complex_mathematical": """
Create 2 advanced calculus questions with LaTeX notation for university students.
Include feedback, difficulty levels, and detailed metadata.
Return as JSON array with complete educational question structure.
""",
                
                "edge_case_prompt": """
Generate 1 question about quantum physics with complex mathematical expressions,
special Unicode characters, and multi-paragraph explanations.
Include all educational metadata and ensure proper JSON formatting.
"""
            },
            
            "collection_checklist": [
                "□ Use standardized prompts across all LLM providers",
                "□ Test each LLM version separately", 
                "□ Capture complete raw responses (no editing)",
                "□ Document exact model version and settings",
                "□ Include timestamp and test environment details",
                "□ Test multiple educational subjects",
                "□ Include both simple and complex question types",
                "□ Deliberately include edge cases and challenging formats",
                "□ Save responses in structured test case format",
                "□ Maintain consistent testing conditions"
            ],
            
            "file_organization": {
                "directory_structure": "tests/llm_test_cases/{provider}/{model_version}/",
                "file_naming": "{provider}_{model}_{category}_{timestamp}.json",
                "metadata_file": "test_metadata.json",
                "results_tracking": "systematic_test_results.json"
            }
        }
        
        return protocol
        
    def analyze_current_gaps(self) -> Dict[str, Any]:
        """Analyze gaps in current LLM testing coverage."""
        
        gaps_analysis = {
            "critical_gaps": [
                {
                    "provider": "ChatGPT",
                    "severity": "critical",
                    "reason": "Major LLM provider with only 1 test case",
                    "impact": "Unknown reliability with most popular AI tool",
                    "recommendation": "Immediate comprehensive testing needed"
                },
                {
                    "provider": "Microsoft Copilot", 
                    "severity": "high",
                    "reason": "Campus environments heavily use Copilot",
                    "impact": "Educational deployment risk",
                    "recommendation": "High priority for institutional users"
                }
            ],
            
            "testing_blind_spots": [
                "Different model versions within same provider",
                "Temporal variations (model updates over time)",
                "Context length limitations and responses",
                "Different prompt engineering approaches",
                "Error conditions and edge case handling",
                "Performance under different load conditions"
            ],
            
            "current_strengths": [
                "Claude: Well-tested with diverse educational content",
                "Gemini: Good coverage across question types", 
                "Core JSONProcessor: 100% success on existing test suite",
                "Educational content: Strong validation framework"
            ],
            
            "risk_assessment": {
                "production_deployment_risk": "medium-high",
                "reason": "Limited LLM diversity in testing",
                "mitigation": "Systematic testing before claiming universal compatibility",
                "timeline": "2-3 weeks for comprehensive validation"
            }
        }
        
        return gaps_analysis
        
    def create_testing_roadmap(self) -> Dict[str, Any]:
        """Create systematic testing roadmap for production readiness."""
        
        roadmap = {
            "phase_1_immediate": {
                "duration": "1 week",
                "focus": "Critical gaps",
                "tasks": [
                    "Collect 20+ ChatGPT responses across question types",
                    "Test Microsoft Copilot with educational prompts",
                    "Document exact model versions and settings",
                    "Run comprehensive acid tests on new data",
                    "Update reliability scores and compatibility matrix"
                ],
                "success_criteria": "90%+ success rate with ChatGPT and Copilot"
            },
            
            "phase_2_comprehensive": {
                "duration": "2 weeks", 
                "focus": "Full LLM ecosystem",
                "tasks": [
                    "Test Llama and open-source models",
                    "Collect Perplexity search-enhanced responses",
                    "Test different model versions within providers",
                    "Edge case and malformed response testing",
                    "Performance benchmarking across all LLMs"
                ],
                "success_criteria": "95%+ success rate across all major LLMs"
            },
            
            "phase_3_validation": {
                "duration": "1 week",
                "focus": "Production validation",
                "tasks": [
                    "Comprehensive acid test with 500+ questions",
                    "Cross-LLM compatibility verification", 
                    "Performance stress testing",
                    "Documentation updates and reliability claims",
                    "Production deployment guidelines"
                ],
                "success_criteria": "Production readiness score 95+"
            }
        }
        
        return roadmap
        
    def generate_test_data_requirements(self) -> Dict[str, Any]:
        """Specify test data collection requirements."""
        
        requirements = {
            "minimum_test_cases": {
                "per_provider": 30,
                "per_model_version": 15,
                "per_category": 5,
                "total_target": 300
            },
            
            "content_diversity": [
                "Mathematics (algebra, calculus, statistics)",
                "Sciences (physics, chemistry, biology)",
                "Humanities (history, literature, philosophy)", 
                "Technical (computer science, engineering)",
                "Languages (linguistics, foreign language)",
                "Professional (business, medicine, law)"
            ],
            
            "format_variations": [
                "Clean JSON responses",
                "JSON in markdown code blocks",
                "Mixed content with explanations",
                "Malformed or incomplete JSON",
                "Unicode and special characters",
                "Very long responses (>2000 characters)"
            ],
            
            "quality_requirements": [
                "Raw, unedited LLM outputs only",
                "Complete response capture (no truncation)",
                "Exact model version documentation",
                "Consistent prompt usage across LLMs",
                "Timestamp and environment metadata",
                "Educational validity of content"
            ]
        }
        
        return requirements
        
def main():
    """Generate systematic LLM testing framework."""
    
    tester = SystematicLLMTester()
    
    print("🧪 Systematic LLM Testing Framework")
    print("=" * 50)
    
    # Generate comprehensive analysis
    test_plan = tester.generate_test_plan()
    protocol = tester.create_test_collection_protocol()
    gaps_analysis = tester.analyze_current_gaps()
    roadmap = tester.create_testing_roadmap()
    requirements = tester.generate_test_data_requirements()
    
    # Save analysis results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {
        "analysis_date": timestamp,
        "test_plan": test_plan,
        "collection_protocol": protocol,
        "gaps_analysis": gaps_analysis,
        "testing_roadmap": roadmap,
        "data_requirements": requirements
    }
    
    output_file = tester.results_dir / f"systematic_llm_analysis_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Systematic testing analysis saved: {output_file}")
    
    # Print key findings
    print(f"\n📊 CURRENT STATUS:")
    print(f"   Providers tested: Claude ✅, Gemini ✅, ChatGPT ⚠️")
    print(f"   Total test cases needed: {test_plan['total_test_cases_needed']}")
    print(f"   Critical gaps: {len(gaps_analysis['critical_gaps'])}")
    
    print(f"\n🎯 NEXT STEPS:")
    for step in roadmap["phase_1_immediate"]["tasks"]:
        print(f"   • {step}")
        
    return results

if __name__ == "__main__":
    main()