"""
Test with your actual ChatGPT response
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.append('.')

from modules.json_processor import JSONProcessor

def test_your_chatgpt_data():
    """Test with your actual problematic ChatGPT response"""
    
    try:
        # Try to read your actual ChatGPT response
        with open('test_data/chatgpt_responses/antenna_display_math.json', 'r', encoding='utf-8') as f:
            your_data = f.read()
        
        print(f"✅ Found your ChatGPT response: {len(your_data)} characters")
        
        # Test it with our modular processor
        processor = JSONProcessor()
        success, result, messages = processor.process_raw_json(your_data, 'chatgpt')
        
        print(f"\n📊 RESULTS:")
        print(f"Success: {success}")
        print(f"Messages: {messages}")
        
        if success and result:
            print(f"✅ Questions loaded: {len(result['questions'])}")
            
            # Show validation
            validation = processor.validate_questions(result)
            print(f"✅ Validation: {validation['valid']}/{validation['total']} questions valid")
            
            # Show first question title
            if result['questions']:
                first_q = result['questions'][0]
                print(f"✅ First question: {first_q.get('title', 'No title')}")
            
            print(f"\n🎉 SUCCESS! The modular repair worked on your actual data!")
            print(f"This means the enhanced repair function is solving your ChatGPT issue!")
            
        else:
            print(f"\n❌ Still failed. The repair function needs more work.")
            print("Messages show exactly what's still broken:")
            for i, msg in enumerate(messages, 1):
                print(f"  {i}. {msg}")
    
    except FileNotFoundError:
        print("❌ File not found: test_data/chatgpt_responses/antenna_display_math.json")
        print("\nTo test with your real data:")
        print("1. Copy your problematic ChatGPT response")
        print("2. Save it as: test_data/chatgpt_responses/antenna_display_math.json")
        print("3. Run this test again")
        
        # Test with simulated data instead
        print("\n🧪 Testing with simulated problematic data...")
        test_simulated_problem()

def test_simulated_problem():
    """Test with data that simulates your problem"""
    
    # This simulates your actual problematic response
    problematic_json = '''
    {
        "questions": [
            {
                "type": "numerical",
                "title": "Patch Resonant Frequency Calculation",
                "question_text": "Calculate the resonant frequency",
                "choices": [],
                "correct_answer": "3.218",
                "points": 2,
                "tolerance": 0.01,
                "feedback_correct": "Correct! $$f_0 = \\\\dfrac{3\\\\times10^8}{2\\\\times35\\\\times10^{-3}\\\\times\\\\sqrt{2.2}} = 3.218\\\\,\\\\text{GHz}$$.",
                "feedback_incorrect": "Remember to convert mm to meters",
                "image_file": [],
                "topic": "Antennas",
                "subtopic": "Patch Antennas",
                "difficulty": "Intermediate"
            }
        ]
    }
    '''
    
    processor = JSONProcessor()
    success, result, messages = processor.process_raw_json(problematic_json, 'chatgpt')
    
    print(f"📊 SIMULATED TEST RESULTS:")
    print(f"Success: {success}")
    print(f"Messages: {messages}")
    
    if success:
        print(f"✅ The repair function can handle display math issues!")
    else:
        print(f"❌ The repair function needs enhancement for display math")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Modular Repair with Your Actual ChatGPT Data")
    print("=" * 60)
    
    test_your_chatgpt_data()