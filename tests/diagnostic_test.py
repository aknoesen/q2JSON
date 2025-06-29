#!/usr/bin/env python3
"""
Diagnostic Test for Master.json Processing
Quick test to identify why acid test is failing.
"""

import json
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent if current_dir.name == 'tests' else current_dir
sys.path.insert(0, str(project_root))

from modules.json_processor import JSONProcessor

def diagnose_master_json():
    """Diagnose Master.json processing issues."""
    
    print("🔍 Diagnostic Test for Master.json Processing")
    print("=" * 50)
    
    # Load Master.json
    master_path = project_root / "test_data" / "Master.json"
    
    if not master_path.exists():
        print(f"❌ Master.json not found at: {master_path}")
        return
        
    print(f"📁 Loading: {master_path}")
    
    with open(master_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"📊 Data type: {type(data)}")
    print(f"📊 Is dict: {isinstance(data, dict)}")
    
    if isinstance(data, dict):
        print(f"📊 Keys: {list(data.keys())}")
        if 'questions' in data:
            questions = data['questions']
            print(f"📊 Questions count: {len(questions)}")
            
            # Test first few questions
            processor = JSONProcessor()
            
            for i, question in enumerate(questions[:3]):
                print(f"\n🧪 Testing Question {i+1}:")
                print(f"   Original type: {type(question)}")
                print(f"   Keys: {list(question.keys()) if isinstance(question, dict) else 'Not a dict'}")
                
                # Convert to string (simulate raw JSON input)
                raw_content = json.dumps({"questions": [question]})
                print(f"   Raw content length: {len(raw_content)}")
                print(f"   Raw content preview: {raw_content[:100]}...")
                
                try:
                    # Process with JSONProcessor
                    result = processor.process_raw_json(raw_content)
                    print(f"   ✅ Result type: {type(result)}")
                    print(f"   ✅ Is dict/list: {isinstance(result, (dict, list))}")
                    
                    if result:
                        # Try to serialize
                        json.dumps(result)
                        print(f"   ✅ JSON serializable: Yes")
                        
                        # Check content
                        if isinstance(result, dict) and 'questions' in result:
                            print(f"   ✅ Questions found: {len(result['questions'])}")
                        elif isinstance(result, list):
                            print(f"   ✅ List length: {len(result)}")
                        else:
                            print(f"   ⚠️  Unexpected structure: {result}")
                    else:
                        print(f"   ❌ Result is None or empty")
                        
                except Exception as e:
                    print(f"   ❌ Processing error: {e}")
                    
    else:
        print(f"❌ Expected dict, got {type(data)}")

if __name__ == "__main__":
    diagnose_master_json()