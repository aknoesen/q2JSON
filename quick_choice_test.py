#!/usr/bin/env python3
"""
Quick test for question choices detection
"""

import json

def quick_choice_test():
    """Quick test to verify choices exist"""
    
    test_file = r"c:\Users\aknoesen\Documents\Knoesen\Database for EEC1\Debug Problem Cases\MosfetQQDebug.json"
    
    print("Quick Choice Detection Test")
    print("=" * 40)
    
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"Total questions: {len(questions)}")
    
    for i, question in enumerate(questions[:3]):  # Check first 3
        title = question.get('title', 'No title')
        q_type = question.get('type', 'No type')
        choices = question.get('choices', [])
        
        print(f"\nQuestion {i+1}:")
        print(f"  Title: {title[:50]}...")
        print(f"  Type: {q_type}")
        print(f"  Choices: {len(choices)}")
        
        if choices:
            print(f"  First choice: {choices[0][:50]}...")
            print(f"  Last choice: {choices[-1][:50]}...")
        else:
            print("  ❌ NO CHOICES FOUND!")
    
    # Check specific MOSFET question
    print(f"\nMOSFET Question (Question 1):")
    if questions:
        mosfet_q = questions[0]
        choices = mosfet_q.get('choices', [])
        print(f"  Choices count: {len(choices)}")
        
        if choices:
            print(f"  All choices:")
            for i, choice in enumerate(choices):
                print(f"    {i+1}. {choice}")
        else:
            print("  ❌ MOSFET question has NO CHOICES!")
            print("  Question structure:")
            for key, value in mosfet_q.items():
                print(f"    {key}: {type(value)}")

if __name__ == "__main__":
    quick_choice_test()