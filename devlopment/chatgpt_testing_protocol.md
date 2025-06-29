# ChatGPT Testing Protocol for q2JSON

## **Test Setup**
**Date**: June 28, 2025  
**Purpose**: Complete LLM compatibility matrix with ChatGPT results  
**Environment**: q2JSON Streamlit app, **DEV MODE** - Hot reloading enabled  
**Development Benefits**: Real-time debugging, immediate iteration, enhanced logging

---

## **Test Cases**

### **Test Case 1: Simple Template**
**Objective**: Test ChatGPT with minimal, non-threatening prompt structure

**Steps**:
1. Launch q2JSON app: `streamlit run app.py`
2. Navigate to Stage 1: Prompt Builder
3. Configure test parameters:
   - **Educational Context**: Select "Example" 
   - **Topic**: "Basic algebra"
   - **Question Count**: 5
   - **Question Types**: Multiple Choice, True/False
   - **Difficulty**: Easy
   - **Include Explanations**: Yes
4. **Advanced Options**: Leave default (minimal custom instructions)
5. Generate and download prompt
6. Test in ChatGPT interface

**Expected Behaviors to Document**:
- Does ChatGPT generate clean JSON?
- Are response boundaries respected?
- Any safety filter triggers?
- Quality of question generation

---

### **Test Case 2: Detailed Template**
**Objective**: Test ChatGPT with comprehensive context and boundaries

**Steps**:
1. Same setup as Test Case 1
2. **Advanced Options**: 
   - **Custom Instructions**: "Focus ONLY on generating educational questions in valid JSON format. Do not provide explanations about the task itself."
   - **Difficulty Details**: "Ensure questions test fundamental understanding"
3. Generate and download prompt
4. Test in ChatGPT interface

**Expected Behaviors to Document**:
- Does additional context improve output quality?
- Any tendency to generate non-JSON responses?
- Comparison with simple template results

---

### **Test Case 3: Edge Case Testing**
**Objective**: Test ChatGPT's handling of complex educational contexts

**Steps**:
1. **Educational Context**: Select "Custom"
2. **Custom Context**: 
   ```
   Students are learning about photosynthesis in a 9th-grade biology class. 
   They have covered the basic equation and light-dependent reactions. 
   Questions should assess their understanding of the Calvin cycle and 
   factors affecting photosynthesis rates.
   ```
3. **Question Count**: 8
4. **Question Types**: Multiple Choice, Short Answer, Essay
5. **Difficulty**: Medium to Hard
6. Test response processing

**Expected Behaviors to Document**:
- Handling of complex scientific content
- JSON structure compliance with mixed question types
- Quality of generated distractors and explanations

---

## **Data Collection Template**

### **Response Quality Metrics**
For each test, record:

**JSON Compliance**:
- [ ] Valid JSON structure
- [ ] Required fields present
- [ ] Proper data types
- [ ] Clean formatting (no markdown artifacts)

**Content Quality**:
- [ ] Questions match educational context
- [ ] Appropriate difficulty level
- [ ] Good distractors (for MC questions)
- [ ] Meaningful explanations
- [ ] No factual errors

**ChatGPT-Specific Behaviors**:
- [ ] Follows instructions precisely
- [ ] Stays within JSON boundaries
- [ ] Handles custom context appropriately
- [ ] Any unexpected responses or formatting

**Comparison Notes**:
- How does it compare to Copilot's ultra-simple needs?
- How does it compare to Claude's boundary requirements?
- How does it compare to Gemini's flexibility?

---

## **Test Results Documentation**

### **Test Case 1 Results: Simple Template**
**Date/Time**: ___________  
**ChatGPT Version**: ___________

**Response Summary**:
- JSON validity: ⭐⭐⭐⭐⭐ (1-5 stars)
- Content quality: ⭐⭐⭐⭐⭐
- Instruction following: ⭐⭐⭐⭐⭐
- Format cleanliness: ⭐⭐⭐⭐⭐

**Notable behaviors**:
- [Record any interesting patterns]
- [Safety filter issues?]
- [JSON formatting quirks?]

**Sample response excerpt** (first 200 characters):
```
[Paste sample here]
```

### **Test Case 2 Results: Detailed Template**
[Same format as above]

### **Test Case 3 Results: Edge Case**
[Same format as above]

---

## **LLM Compatibility Matrix Update**

Based on results, update the compatibility matrix:

| LLM | Simple Template | Detailed Template | Special Requirements |
|-----|----------------|-------------------|---------------------|
| **Microsoft Copilot** | ✅ Works | ❌ Blocks prompt | Ultra-simple language only |
| **Google Gemini** | ✅ Works | ✅ Works | Most flexible |
| **Claude (Anthropic)** | ❌ PowerShell scripts | ✅ Works | Needs explicit boundaries |
| **ChatGPT (OpenAI)** | ⏳ Testing | ⏳ Testing | [Update with findings] |

---

## **Stage 2 Testing Preparation**

After ChatGPT testing, prepare for Stage 2 validation:

**Files to Create**:
1. **chatgpt_simple.txt** - Response from simple template test
2. **chatgpt_detailed.txt** - Response from detailed template test
3. **chatgpt_edge.txt** - Response from edge case test

**Stage 2 Test Protocol**:
1. Upload each response file to Stage 2
2. Test automatic JSON extraction
3. Validate JSON parsing
4. Test manual editor functionality
5. Verify question preview accuracy

---

## **Success Criteria for Today**

**ChatGPT Testing Complete** ✅:
- [ ] All 3 test cases executed
- [ ] Results documented and compared
- [ ] LLM compatibility matrix updated
- [ ] Response files prepared for Stage 2

**Stage 2 Validation** ✅:
- [ ] File upload functionality confirmed
- [ ] JSON extraction accuracy verified
- [ ] Manual editor tested
- [ ] Session state persistence confirmed

**Stage 3 Preview** ✅:
- [ ] Basic validation workflow tested
- [ ] Export functionality verified
- [ ] Error handling confirmed

**Documentation Updated** ✅:
- [ ] Transition document updated with findings
- [ ] Template strategy finalized
- [ ] Deployment readiness assessed