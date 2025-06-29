# run_direct_tests.py
"""
Direct test runner without pytest dependency
Run this while you install pytest
"""

import json
import sys
from pathlib import Path

# Add current directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from modules.json_processor import JSONProcessor
    print("✅ Successfully imported JSONProcessor")
except ImportError as e:
    print(f"❌ Failed to import JSONProcessor: {e}")
    sys.exit(1)

def test_corner_cases():
    """Test corner cases processing"""
    print("\n" + "="*50)
    print("TESTING: Corner Cases Processing")
    print("="*50)
    
    processor = JSONProcessor()
    
    # Load corner cases data
    corner_cases_file = Path("test_data/CornerCases.json")
    
    if corner_cases_file.exists():
        print("✅ Found CornerCases.json file")
        with open(corner_cases_file, 'r', encoding='utf-8') as f:
            corner_cases_data = f.read()
    else:
        print("⚠️ CornerCases.json not found, using sample data")
        corner_cases_data = '''{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Phase Relationship in a Pure Inductor",
      "question_text": "In a purely inductive AC circuit, what is the phase relationship?",
      "choices": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "points": 2,
      "tolerance": 0.05,
      "id": "_1"
    }
  ],
  "metadata": {
    "total_questions": 1
  }
}'''
    
    # Test processing
    print("🔧 Processing corner cases data...")
    success, data, messages = processor.process_raw_json(corner_cases_data, "edge_case")
    
    print(f"Success: {success}")
    print(f"Messages: {len(messages)}")
    for message in messages:
        print(f"  - {message}")
    
    if success:
        print(f"✅ Questions processed: {len(data['questions'])}")
        
        # Check for extended fields
        first_question = data["questions"][0]
        extended_fields = []
        standard_fields = {"type", "title", "question_text", "choices", "correct_answer", "points"}
        
        for field in first_question.keys():
            if field not in standard_fields:
                extended_fields.append(field)
        
        print(f"✅ Extended fields found: {extended_fields}")
        
        # Check metadata preservation
        if "metadata" in data:
            print("✅ Metadata preserved")
        else:
            print("⚠️ Metadata not preserved")
    else:
        print("❌ Processing failed")
    
    return success

def test_chatgpt_pattern():
    """Test ChatGPT markdown pattern"""
    print("\n" + "="*50)
    print("TESTING: ChatGPT Markdown Pattern")
    print("="*50)
    
    processor = JSONProcessor()
    
    chatgpt_response = '''Here are your educational questions:

```json
{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Test Question",
      "question_text": "What is the impedance?",
      "choices": ["100Ω", "200Ω", "50Ω", "0Ω"],
      "correct_answer": "100Ω",
      "points": 1
    }
  ]
}
```

These questions follow your specifications.'''
    
    print("🔧 Processing ChatGPT response with markdown...")
    success, data, messages = processor.process_raw_json(chatgpt_response, "chatgpt")
    
    print(f"Success: {success}")
    for message in messages:
        print(f"  - {message}")
    
    if success:
        print(f"✅ Questions extracted: {len(data['questions'])}")
        
        # Check if markdown is removed
        exported = processor.export_json(data)
        if "```json" not in exported and "```" not in exported:
            print("✅ Markdown successfully removed")
        else:
            print("⚠️ Markdown still present in export")
    else:
        print("❌ ChatGPT pattern processing failed")
    
    return success

def test_malformed_recovery():
    """Test malformed JSON recovery"""
    print("\n" + "="*50)
    print("TESTING: Malformed JSON Recovery")
    print("="*50)
    
    processor = JSONProcessor()
    
    # Missing closing brace
    malformed_json = '''{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Test",
      "question_text": "Question?",
      "choices": ["A", "B"],
      "correct_answer": "A",
      "points": 1
    }
  ]
  # Missing closing brace'''
    
    print("🔧 Testing recovery from malformed JSON...")
    success, data, messages = processor.process_raw_json(malformed_json, "malformed")
    
    print(f"Recovery success: {success}")
    for message in messages:
        print(f"  - {message}")
    
    if success:
        print("✅ Successfully recovered from malformed JSON")
    else:
        print("❌ Could not recover from malformed JSON")
    
    return success

def test_performance():
    """Test performance with larger dataset"""
    print("\n" + "="*50)
    print("TESTING: Performance with Large Dataset")
    print("="*50)
    
    import time
    
    processor = JSONProcessor()
    
    # Create 20 test questions
    large_dataset = {"questions": []}
    for i in range(20):
        question = {
            "type": "multiple_choice",
            "title": f"Question {i+1}",
            "question_text": f"What is the answer to question {i+1}?",
            "choices": [f"Option {j}" for j in range(1, 5)],
            "correct_answer": "Option 1",
            "points": 1,
            "id": f"_q{i+1}"
        }
        large_dataset["questions"].append(question)
    
    large_json = json.dumps(large_dataset, indent=2)
    
    print(f"🔧 Processing {len(large_dataset['questions'])} questions...")
    start_time = time.time()
    success, data, messages = processor.process_raw_json(large_json, "performance")
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    print(f"Success: {success}")
    print(f"Processing time: {processing_time:.3f} seconds")
    if success:
        print(f"✅ Questions processed: {len(data['questions'])}")
    
    return success

def main():
    """Run all tests"""
    print("🧪 Starting Direct Test Suite")
    print("="*60)
    
    tests = [
        ("Corner Cases", test_corner_cases),
        ("ChatGPT Pattern", test_chatgpt_pattern),
        ("Malformed Recovery", test_malformed_recovery),
        ("Performance", test_performance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

if __name__ == "__main__":
    main()