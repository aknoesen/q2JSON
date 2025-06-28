# q2JSON Development Transition Document

**Project**: q2JSON Streamlit Web Application  
**Date**: June 27, 2025  
**Status**: Stage 1 Complete, Stages 2-3 Implemented but Pending Testing  
**Next Session**: ChatGPT testing and full app validation

---

## 🎯 Project Overview

Converting the successful Q2QTI desktop application to a web-based Streamlit app for educational question generation. The app transforms AI/LLM responses into clean, validated JSON questions ready for educational deployment.

### Success Criteria
- ✅ **3-stage workflow** preserved from desktop version
- ✅ **Template system** integrated (with LLM-specific variations)
- ⏳ **Q2validate integration** (pending testing)
- ⏳ **Cross-platform accessibility** (pending full deployment)
- ✅ **Template loading** fixed (corrected order: preamble → user context → postamble)

---

## 📂 Current Project Structure

```
q2json-streamlit/
├── app.py                           ✅ Complete implementation
├── requirements.txt                 ✅ streamlit>=1.28.0, pathlib2>=2.3.7
├── kill-streamlit.bat              ✅ Process management utility
├── templates/                      ✅ Template files confirmed working
│   ├── preamble_default.txt       ✅ Tested
│   └── postamble_default.txt      ✅ Tested  
└── .streamlit/                     
    └── config.toml                 ❌ Removed (was causing launch issues)
```

---

## 🚀 Implementation Status

### ✅ **Stage 1: Prompt Builder - COMPLETE**
- **Template loading**: Fixed order (preamble → user context → postamble)
- **Template files**: Load correctly from `templates/` directory
- **Educational context**: 3 input options (example/template/custom)
- **Question configuration**: Count, type, difficulty, explanations
- **Advanced options**: Custom instructions, difficulty levels
- **Export functionality**: Download prompt as .txt file
- **Template validation**: Shows status in sidebar

### ✅ **Stage 2: AI Processing - IMPLEMENTED (Not Fully Tested)**
- **File upload**: Supports TXT, JSON, MD files
- **Direct paste**: Alternative to file upload
- **Response cleaning**: Auto-extract JSON, clean markdown, fix quotes
- **JSON validation**: Real-time parsing and error detection
- **Manual editor**: Fallback for fixing JSON errors
- **Question preview**: Shows metrics and first 3 questions
- **Session state**: Maintains data between stages

### ✅ **Stage 3: JSON Validation - IMPLEMENTED (Not Fully Tested)**
- **Comprehensive validation**: Required fields, question types, format
- **Unicode conversion**: Automatic Unicode to LaTeX conversion
- **Progress tracking**: Real-time validation progress
- **Detailed reporting**: Question-by-question analysis
- **Multiple exports**: Valid questions only, all questions, validation report
- **Error analysis**: Specific feedback on validation issues

---

## 🤖 LLM Testing Results & Template Strategy

### **Current LLM Compatibility Matrix**

| LLM | Simple Template | Detailed Template | Special Notes |
|-----|----------------|-------------------|---------------|
| **Microsoft Copilot** | ✅ Works | ❌ Blocks prompt | Campus-provided LLM |
| **Google Gemini** | ✅ Works | ✅ Works | Most flexible |
| **Claude (Anthropic)** | ❌ Generates PowerShell scripts | ✅ Works | Needs context boundaries |
| **ChatGPT (OpenAI)** | ⏳ Test tomorrow | ⏳ Test tomorrow | Pending |

### **Template Requirements by LLM**

#### **Microsoft Copilot (Campus LLM)**
- **Template**: Ultra-simple, non-threatening language
- **Triggers**: Long prompts, "FORBIDDEN", "CRITICAL" keywords
- **Solution**: Minimal template + smart Stage 2 processing

#### **Claude**
- **Template**: Detailed context with explicit boundaries
- **Issue**: User preference bleeding (PowerShell context)
- **Solution**: "Focus ONLY on question generation" boundaries

#### **Gemini**
- **Template**: Flexible - works with both simple and detailed
- **Notes**: Most cooperative LLM tested

---

## 🔧 Technical Issues Resolved

### **Template Loading Order** ✅ FIXED
- **Problem**: App was using fallback templates instead of actual files
- **Root Cause**: File path or loading logic error
- **Solution**: Corrected template loading function
- **Verification**: Templates now load correctly, show proper status

### **Streamlit Process Management** ⚠️ ONGOING ISSUE
- **Problem**: Ctrl+C doesn't reliably stop Streamlit in both PowerShell and cmd
- **Workaround**: Created `kill-streamlit.bat` script
- **Usage**: Open new cmd window → navigate to project → run `kill-streamlit.bat`
- **Alternative**: Task Manager → End python.exe processes

### **Config File Issues** ✅ RESOLVED
- **Problem**: TOML parsing error on launch
- **Solution**: Deleted problematic `.streamlit/config.toml` file
- **Result**: App launches successfully with default settings

---

## 📋 Testing Checklist for Next Session

### **Stage 1 Testing** ✅ COMPLETE
- [x] Template files load correctly
- [x] Prompt generation works with correct order
- [x] Download functionality works
- [x] LLM-specific behavior documented

### **Stage 2 Testing** ⏳ PENDING
- [ ] File upload functionality
- [ ] JSON extraction from various AI responses
- [ ] Response cleaning algorithms
- [ ] Manual JSON editor
- [ ] Question preview accuracy
- [ ] Session state persistence

### **Stage 3 Testing** ⏳ PENDING
- [ ] Validation logic accuracy
- [ ] Unicode to LaTeX conversion
- [ ] Export functionality (all 3 types)
- [ ] Validation report generation
- [ ] Error handling and feedback

### **ChatGPT Integration** ⏳ TOMORROW
- [ ] Test simple template response
- [ ] Test detailed template response
- [ ] Document ChatGPT-specific quirks
- [ ] Update LLM compatibility matrix

---

## 🎯 Immediate Next Steps

### **Tomorrow's Session Priority:**
1. **ChatGPT Testing**
   - Test both simple and detailed templates
   - Document response patterns and issues
   - Update compatibility matrix

2. **Full App Testing**
   - Stage 2: Upload real AI responses, test processing
   - Stage 3: Run validation on processed questions
   - End-to-end workflow testing

3. **Template Strategy Finalization**
   - Based on ChatGPT results, decide on template approach
   - Option A: Single adaptive template
   - Option B: LLM-specific template sets in app

### **Deployment Preparation:**
- [ ] Complete testing of all stages
- [ ] Create comprehensive error handling
- [ ] Prepare for Streamlit Cloud deployment
- [ ] Document deployment process

---

## 💡 Strategic Insights

### **LLM Behavior Patterns**
- **Overly simple prompts**: Risk of AI confusion (Claude PowerShell issue)
- **Overly complex prompts**: Risk of safety filter triggers (Copilot blocking)
- **Campus constraints**: Limited to Microsoft Copilot for actual deployment
- **Template strategy**: May need LLM-specific approaches

### **App Architecture Decisions**
- **Smart Stage 2**: Focus on robust response processing vs. perfect prompts
- **Template flexibility**: Support multiple template sets if needed
- **Error handling**: Graceful degradation when things go wrong
- **User experience**: Clear guidance for each LLM's quirks

---

## 🔄 Known Issues & Workarounds

### **Streamlit Process Management**
- **Issue**: Inconsistent Ctrl+C behavior
- **Workaround**: `kill-streamlit.bat` script
- **Long-term**: Consider alternative development approaches

### **LLM Response Variability**
- **Issue**: Each LLM breaks rules differently
- **Strategy**: Build robust Stage 2 processing
- **Fallback**: Manual JSON editor in Stage 2

### **Campus LLM Limitations**
- **Constraint**: Must work with Microsoft Copilot
- **Solution**: Simplified template + enhanced processing
- **Backup**: Document process for other LLMs

---

## 📖 Development Resources

### **Key Files**
- `app.py`: Complete Streamlit application
- `templates/preamble_default.txt`: Pre-user context instructions
- `templates/postamble_default.txt`: Post-user context JSON requirements
- `requirements.txt`: Python dependencies
- `kill-streamlit.bat`: Process management utility

### **Testing Resources**
- **Sample prompts**: Available from previous testing
- **LLM responses**: Collected from Copilot, Gemini, Claude testing
- **Validation examples**: Ready for Stage 3 testing

### **Documentation**
- **LLM compatibility matrix**: Updated with testing results
- **Template strategies**: Documented per LLM requirements
- **Workflow patterns**: 3-stage process validated

---

## 🎓 Course Integration Notes

### **Educational Value**
- **LLM comparison**: Real-world prompt engineering challenges
- **Template engineering**: Practical AI interaction strategies
- **Validation systems**: Quality assurance for AI-generated content
- **Tool development**: From desktop to web application transition

### **Student Learning Outcomes**
- Understanding LLM behavior variability
- Prompt engineering best practices
- AI response processing techniques
- Educational content quality validation

---

**End of Transition Document**  
**Next Session**: ChatGPT testing and complete app validation  
**Status**: Ready for comprehensive testing and deployment preparation