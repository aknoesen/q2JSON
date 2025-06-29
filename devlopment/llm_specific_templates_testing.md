# LLM-Specific Template Strategy

## 🎯 **Based on Your Testing Protocol Results**

From your comprehensive testing, here are targeted templates for each LLM's specific behaviors:

## 📁 **Template Files to Create**

### **templates/chatgpt_simple.txt**
```
Simple Educational Question Generator

Create 5 educational questions in JSON format.

Requirements:
- Return ONLY JSON 
- No explanations before or after
- No markdown code blocks
- Use this exact structure:

{"questions": [{"type": "multiple_choice", "title": "Question Title", "question_text": "Question text here", "choices": ["A", "B", "C", "D"], "correct_answer": "A", "points": 1}]}

Topic: [EDUCATIONAL_CONTEXT]
```

### **templates/copilot_ultra_simple.txt**  
```
Generate JSON questions:

Topic: [EDUCATIONAL_CONTEXT]

Output format: {"questions": [{"type": "multiple_choice", "title": "Title", "question_text": "Text", "choices": ["A", "B", "C", "D"], "correct_answer": "A", "points": 1}]}
```

### **templates/claude_explicit.txt**
```
TASK: Generate educational questions in JSON format.

BOUNDARIES: Your response must start with { and end with }. No other text allowed.

EDUCATIONAL CONTEXT: [EDUCATIONAL_CONTEXT]

OUTPUT REQUIREMENT: Valid JSON only with questions array.

EXAMPLE: {"questions": [{"type": "multiple_choice", "title": "Sample", "question_text": "Question?", "choices": ["A", "B", "C", "D"], "correct_answer": "A", "points": 1}]}

BEGIN JSON OUTPUT:
```

### **templates/gemini_standard.txt**
```
Educational Question Generation Task

Context: [EDUCATIONAL_CONTEXT]

Generate educational questions using ONLY the JSON structure below. Do not include any Unicode symbols - use LaTeX notation for all mathematical content.

Required JSON format:
{"questions": [{"type": "multiple_choice", "title": "Descriptive Title", "question_text": "Question with $LaTeX$ math", "choices": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option A", "points": 2}]}

Mathematical notation: Use $...$ for math (e.g., $V = IR$, $10\\,\\Omega$, $\\pi$)

Response: JSON only, no additional text.
```

## 🧪 **Testing Implementation Commands**

### **1. Create Test Directory Structure**
```cmd
mkdir tests\test_data\llm_responses\chatgpt
mkdir tests\test_data\llm_responses\gemini  
mkdir tests\test_data\llm_responses\copilot
mkdir tests\test_data\llm_responses\claude
mkdir tests\test_data\expected_outputs
```

### **2. Run Direct Tests**
```cmd
cd C:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON
python -m pytest tests/test_json_processor_direct.py -v
```

### **3. Run Specific LLM Pattern Tests**
```cmd
python -m pytest tests/test_json_processor_direct.py::TestJSONProcessorDirect::test_chatgpt_markdown_removal -v
```

### **4. Generate Test Report**
```cmd
python -m pytest tests/test_json_processor_direct.py --tb=short -v
```

## 📊 **Test Data Collection Strategy**

### **Step 1: Collect Real LLM Responses**
For each LLM, collect responses from:
1. **Simple template** (your current Test Case 1)
2. **Detailed template** (your Test Case 2) 
3. **Edge case** (your Test Case 3)

### **Step 2: Document Failure Patterns**
Create files in `test_data/llm_responses/[llm]/`:
- `simple_response.txt` - Raw LLM output
- `detailed_response.txt` - Complex prompt output  
- `failure_case.txt` - Known problematic response
- `edge_case.txt` - Boundary condition test

### **Step 3: Validate Normalization**
Test that your `JSONProcessor` can handle each pattern:
```python
# Example test pattern
def test_real_chatgpt_response():
    with open('test_data/llm_responses/chatgpt/simple_response.txt') as f:
        real_response = f.read()
    
    processor = JSONProcessor()
    success, data, messages = processor.process_raw_json(real_response, "chatgpt")
    
    assert success
    assert len(data["questions"]) == 5  # Expected count
```

## 🎯 **Immediate Next Steps**

### **Option A: Run Current Tests**
1. Copy the test file to `tests/test_json_processor_direct.py`
2. Run: `python -m pytest tests/test_json_processor_direct.py -v`
3. See which patterns your current processor handles

### **Option B: Add Real Test Data**  
1. Create the directory structure above
2. Copy your ChatGPT Test Case 1 response into `test_data/llm_responses/chatgpt/simple_response.txt`
3. Modify tests to use real data

### **Option C: Create LLM-Specific Templates**
1. Create the template files above in your `templates/` directory
2. Test them with each LLM
3. Update your app to use appropriate templates per LLM

## 📈 **Expected Results**

This testing strategy will give you:
- ✅ **Precise identification** of which LLM patterns your processor handles
- ✅ **Direct testing** without app overhead
- ✅ **Rapid iteration** on normalization improvements  
- ✅ **Comprehensive coverage** of real-world LLM behaviors
- ✅ **Performance metrics** for each LLM type

Which approach would you like to start with first?