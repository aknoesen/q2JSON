# q2JSON Streamlit Implementation Plan

**Project**: q2JSON - AI Response to Clean Educational JSON  
**Timeline**: 1-2 Days  
**Status**: Ready to Begin  
**Date Created**: June 28, 2025

## 🎯 Project Overview

Build q2JSON - a Streamlit web application that converts AI/LLM responses into clean, validated JSON questions ready for educational deployment. This focuses on the first critical step in the educational content pipeline.

### Success Criteria
- ✅ **3-stage workflow** preserved from desktop version
- ✅ **Template system** integrated and working
- ✅ **Q2validate integration** functional
- ✅ **Web deployment** on Streamlit Cloud
- ✅ **Cross-platform accessibility** (any browser)
- ✅ **Mobile responsive** design

## 📂 Project Structure

```
q2json-streamlit/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── templates/               # Template files (from desktop version)
│   ├── preamble_default.txt
│   └── postamble_default.txt
├── q2validate/              # Copy from desktop project
│   ├── __init__.py
│   └── validation_logic.py
├── utils/                   # Helper functions
│   ├── __init__.py
│   ├── template_loader.py
│   └── json_processor.py
└── assets/                  # Static files
    └── style.css           # Custom styling
```

## ⚡ Day 1: Core Implementation (4-6 hours)

### Hour 1: Setup & Structure (60 min)

#### Environment Setup
```bash
mkdir q2json-streamlit
cd q2json-streamlit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install streamlit pandas
echo "streamlit" > requirements.txt
```

#### Basic App Structure
```python
# app.py - Initial structure
import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="q2JSON Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📝 q2JSON Generator")
st.markdown("*Convert AI Responses to Clean Educational JSON*")

# Navigation
stage = st.sidebar.radio(
    "Workflow Stage",
    ["🎯 Prompt Builder", "🤖 AI Processing", "✅ JSON Validation"],
    index=0
)

# Stage placeholders
if stage == "🎯 Prompt Builder":
    st.header("🎯 Build Your AI Prompt")
    st.info("Create optimized prompts for AI question generation")
    
elif stage == "🤖 AI Processing":
    st.header("🤖 Process AI Response")
    st.info("Upload and clean your AI-generated questions")
    
elif stage == "✅ JSON Validation":
    st.header("✅ JSON Validation & Export")
    st.info("Validate and export clean JSON for educational use")
```

#### Test Initial Structure
```bash
streamlit run app.py
```

### Hour 2-3: Stage 1 - Prompt Builder (120 min)

#### Copy Template Files
```bash
mkdir templates
# Copy from desktop project:
# templates/preamble_default.txt
# templates/postamble_default.txt
```

#### Implement Prompt Builder
```python
# Add to Stage 1 section in app.py

# LLM Selection
ai_provider = st.selectbox(
    "Choose AI Provider",
    ["Microsoft Copilot", "ChatGPT (OpenAI)", "Claude (Anthropic)", "Google Gemini"],
    index=0
)

# Educational Context
st.subheader("Educational Context")
context_option = st.radio(
    "Choose input method:",
    ["Use Example", "Use Template", "Write Custom"]
)

if context_option == "Use Example":
    educational_context = st.text_area(
        "Educational Context",
        value="You are an expert in antennas, and teaching a lecture. The topic is patch antennas and implementation on PCB, polarization characteristics are of particular interest.",
        height=100
    )
elif context_option == "Use Template":
    educational_context = st.text_area(
        "Educational Context",
        value="You are an expert in [SUBJECT], and teaching a lecture. The topic is [TOPIC], [SPECIFIC_FOCUS] are of particular interest.",
        height=100
    )
else:
    educational_context = st.text_area(
        "Educational Context",
        placeholder="Enter your educational context here...",
        height=100
    )

# Question Configuration
col1, col2 = st.columns(2)
with col1:
    question_count = st.selectbox(
        "Number of Questions",
        [5, 10, 15, 20],
        index=0
    )
with col2:
    question_type = st.selectbox(
        "Question Types",
        ["Mixed types", "Multiple choice only", "True/False only", "Numerical only", "Fill in multiple blanks"],
        index=0
    )

# Generate Prompt Button
if st.button("🚀 Generate Complete Prompt", type="primary"):
    if educational_context.strip():
        # Load templates
        try:
            with open('templates/preamble_default.txt', 'r') as f:
                preamble = f.read()
            with open('templates/postamble_default.txt', 'r') as f:
                postamble = f.read()
            
            # Build complete prompt
            complete_prompt = f"{preamble}\n\n{educational_context}\n\nGenerate {question_count} questions of type: {question_type.lower()}.\n\n{postamble}"
            
            # Store in session state
            st.session_state.generated_prompt = complete_prompt
            st.success("✅ Prompt generated successfully!")
            
        except FileNotFoundError:
            # Fallback templates
            complete_prompt = f"Generate {question_count} educational questions of type: {question_type.lower()}\n\nContext: {educational_context}\n\nFormat as clean JSON with proper structure for educational assessment."
            st.session_state.generated_prompt = complete_prompt
            st.warning("⚠️ Using fallback template")

# Display Generated Prompt
if 'generated_prompt' in st.session_state:
    st.subheader("Generated Prompt")
    st.text_area("Complete Prompt", st.session_state.generated_prompt, height=200)
    
    # Download button
    st.download_button(
        "💾 Download Prompt File",
        st.session_state.generated_prompt,
        file_name="q2json_prompt.txt",
        mime="text/plain"
    )
    
    # Instructions
    st.info("""
    **Next Steps:**
    1. Download the prompt file above
    2. Upload it to your chosen AI (ChatGPT, Claude, etc.)
    3. Copy the AI response
    4. Go to 'AI Processing' stage to continue
    """)
```

### Hour 4-5: Stage 2 - AI Response Processing (120 min)

#### Implement AI Response Processing
```python
# Add to Stage 2 section in app.py

st.subheader("Upload AI Response")

# File upload
uploaded_file = st.file_uploader(
    "Upload AI Response",
    type=['txt', 'json'],
    help="Upload the response from your AI"
)

# Or paste directly
ai_response = st.text_area(
    "Or paste AI response directly:",
    height=200,
    placeholder="Paste the complete response from your AI here..."
)

# Get response text
response_text = ""
if uploaded_file:
    response_text = str(uploaded_file.read(), "utf-8")
elif ai_response:
    response_text = ai_response

if response_text:
    st.subheader("Processing Options")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        auto_extract = st.checkbox("Auto-extract JSON", value=True)
    with col2:
        clean_markdown = st.checkbox("Clean markdown", value=True)
    with col3:
        fix_quotes = st.checkbox("Fix quotes", value=True)
    
    if st.button("🔧 Process Response", type="primary"):
        processed_text = response_text
        
        # Auto-extract JSON
        if auto_extract:
            import re
            json_match = re.search(r'\{.*\}', processed_text, re.DOTALL)
            if json_match:
                processed_text = json_match.group(0)
        
        # Clean markdown
        if clean_markdown:
            processed_text = processed_text.replace('```json', '').replace('```', '')
        
        # Fix quotes
        if fix_quotes:
            processed_text = processed_text.replace('"', '"').replace('"', '"')
            processed_text = processed_text.replace(''', "'").replace(''', "'")
        
        # Validate JSON
        try:
            questions_data = json.loads(processed_text)
            
            if 'questions' in questions_data and isinstance(questions_data['questions'], list):
                st.session_state.questions_data = questions_data
                st.success(f"✅ Valid JSON with {len(questions_data['questions'])} questions found!")
                
                # Preview
                st.subheader("Questions Preview")
                for i, q in enumerate(questions_data['questions'][:3]):
                    st.write(f"**{i+1}. {q.get('title', 'Untitled')}** ({q.get('type', 'unknown')})")
                
                if len(questions_data['questions']) > 3:
                    st.write(f"... and {len(questions_data['questions']) - 3} more questions")
                
            else:
                st.error("❌ JSON is valid but missing 'questions' array")
                
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON parsing error: {str(e)}")
            
            # Manual editing option
            st.subheader("Manual JSON Editor")
            manual_json = st.text_area(
                "Edit JSON manually:",
                value=processed_text,
                height=300
            )
            
            if st.button("Validate Manual JSON"):
                try:
                    questions_data = json.loads(manual_json)
                    st.session_state.questions_data = questions_data
                    st.success("✅ Manual JSON validation successful!")
                except json.JSONDecodeError:
                    st.error("❌ Manual JSON is still invalid")

# Show current data status
if 'questions_data' in st.session_state:
    st.info(f"📊 Ready to validate {len(st.session_state.questions_data['questions'])} questions")
```

### Hour 6: Stage 3 - Validation (60 min)

#### Copy Q2Validate Logic
```bash
mkdir q2validate
# Copy validation logic from desktop project
# Adapt q2validate_cli.py for direct Python import
```

#### Implement Validation
```python
# Add to Stage 3 section in app.py

if 'questions_data' not in st.session_state:
    st.warning("⚠️ No questions data available. Please complete Stage 2 first.")
else:
    questions = st.session_state.questions_data['questions']
    st.info(f"Ready to validate {len(questions)} questions")
    
    # Validation options
    col1, col2 = st.columns(2)
    with col1:
        auto_fix_unicode = st.checkbox("Auto-fix Unicode to LaTeX", value=True)
    with col2:
        verbose_output = st.checkbox("Show detailed results", value=True)
    
    if st.button("🔍 Run Validation", type="primary"):
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Starting validation...")
        progress_bar.progress(25)
        
        # Import and run validation (adapt from desktop version)
        try:
            # Placeholder for actual validation logic
            import time
            time.sleep(1)  # Simulate processing
            
            status_text.text("Processing questions...")
            progress_bar.progress(50)
            time.sleep(1)
            
            status_text.text("Generating report...")
            progress_bar.progress(75)
            time.sleep(1)
            
            # Mock results (replace with actual validation)
            results = {
                'total': len(questions),
                'valid': len(questions) - 1,
                'unicode_issues': 2,
                'unicode_fixed': 2,
                'ready': len(questions) - 1,
                'success_rate': 80.0
            }
            
            progress_bar.progress(100)
            status_text.text("Validation complete!")
            
            # Display results
            st.subheader("📊 Validation Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Questions", results['total'])
            with col2:
                st.metric("Schema Valid", results['valid'])
            with col3:
                st.metric("Ready for Q2LMS", results['ready'])
            with col4:
                st.metric("Success Rate", f"{results['success_rate']}%")
            
            # Export options
            st.subheader("📤 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export Ready Questions"):
                    ready_questions = {"questions": questions[:results['ready']]}
                    st.download_button(
                        "📥 Download Ready Questions",
                        json.dumps(ready_questions, indent=2),
                        "ready_questions.json",
                        "application/json"
                    )
            
            with col2:
                if st.button("Export All Questions"):
                    st.download_button(
                        "📥 Download All Questions",
                        json.dumps(st.session_state.questions_data, indent=2),
                        "all_questions.json",
                        "application/json"
                    )
            
        except Exception as e:
            st.error(f"❌ Validation failed: {str(e)}")
            progress_bar.progress(0)
            status_text.text("Validation failed")
```

## ⚡ Day 2: Polish & Deploy (2-4 hours)

### Hour 1-2: UI Polish & Styling (120 min)

#### Custom CSS
```python
# Add to top of app.py after imports

def load_css():
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stage-header {
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()
```

#### Error Handling & User Feedback
```python
# Add throughout app.py

try:
    # Existing code
except FileNotFoundError:
    st.error("Template files not found. Using fallback templates.")
except json.JSONDecodeError:
    st.error("Invalid JSON format. Please check your input.")
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
    if st.checkbox("Show technical details"):
        st.exception(e)
```

### Hour 3: Testing & Debugging (60 min)

#### Test Checklist
- [ ] **Stage 1**: Prompt generation works
- [ ] **Stage 2**: File upload and JSON processing works
- [ ] **Stage 3**: Validation runs (mock or real)
- [ ] **Navigation**: All stages accessible
- [ ] **Mobile**: Responsive on phone/tablet
- [ ] **Error handling**: Graceful failure modes
- [ ] **Session state**: Data persists between stages

#### Mobile Responsiveness Test
```python
# Add responsive design checks
if st.sidebar.button("📱 Mobile Preview"):
    st.info("Test the app on mobile by opening in your phone's browser")
```

### Hour 4: Deploy to Streamlit Cloud (60 min)

#### Prepare for Deployment
```bash
# Create requirements.txt
echo "streamlit
pandas
pathlib" > requirements.txt

# Create .streamlit/config.toml
mkdir .streamlit
echo '[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"' > .streamlit/config.toml
```

#### Git Setup & Deploy
```bash
git init
git add .
git commit -m "Initial Q2QTI Streamlit App

- Complete 3-stage workflow
- Template system integrated
- File upload/download functionality
- Mock validation system
- Mobile responsive design
- Ready for Streamlit Cloud deployment"

# Push to GitHub
git remote add origin https://github.com/yourusername/q2qti-streamlit.git
git push -u origin main
```

#### Streamlit Cloud Deployment
1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Connect GitHub** account
3. **Deploy app** from repository
4. **Test live version**

## 🔄 Integration with Existing Code

### From Desktop Project
```bash
# Copy these files/folders:
cp -r ../Q2-Desktop-App/q2prompt/ ./templates/
cp -r ../Q2-Desktop-App/q2validate/ ./q2validate/
cp -r ../Q2-Desktop-App/q2lms/ ./q2lms/
```

### Adapt Q2Validate
```python
# In q2validate/validation_logic.py
def validate_questions_direct(questions_data):
    """
    Direct Python function for validation
    (adapted from q2validate_cli.py)
    """
    # Your existing validation logic here
    # Return results dictionary instead of printing
    pass
```

## ✅ Success Checklist

### Day 1 Complete When:
- [ ] **App launches** with `streamlit run app.py`
- [ ] **3 stages** navigable via sidebar
- [ ] **Stage 1** generates and downloads prompts
- [ ] **Stage 2** processes uploaded text/files
- [ ] **Stage 3** runs validation (mock or real)
- [ ] **Session state** maintains data between stages

### Day 2 Complete When:
- [ ] **UI polished** with custom styling
- [ ] **Error handling** comprehensive
- [ ] **Mobile responsive** design working
- [ ] **Deployed** to Streamlit Cloud
- [ ] **Live URL** accessible and functional
- [ ] **End-to-end test** successful

## 🚀 Post-Launch Tasks

### Immediate (Week 1)
- [ ] **Share with beta testers** (including macOS tester!)
- [ ] **Gather feedback** on user experience
- [ ] **Monitor usage** via Streamlit analytics
- [ ] **Fix critical bugs** if any found

### Short-term (Month 1)
- [ ] **Integrate real q2validate** logic
- [ ] **Add user authentication** if needed
- [ ] **Implement feedback** from testers
- [ ] **Add analytics** and usage tracking

### Long-term (Months 2-3)
- [ ] **Advanced features** based on usage
- [ ] **Q2LMS integration** planning
- [ ] **Multi-user capabilities**
- [ ] **Performance optimization**

## 📞 Support & Troubleshooting

### Common Issues
- **Import errors**: Check requirements.txt and virtual environment
- **File not found**: Verify template files copied correctly
- **Deployment fails**: Check Streamlit Cloud logs and requirements
- **Mobile issues**: Test responsive design with browser dev tools

### Resources
- **Streamlit docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Deployment guide**: [docs.streamlit.io/streamlit-cloud](https://docs.streamlit.io/streamlit-cloud)
- **GitHub repo**: Your project repository for issues and updates

---

**This implementation plan provides a complete roadmap for converting the successful Q2QTI desktop application to a web-based Streamlit app in 1-2 days, maintaining all functionality while gaining web accessibility and easier deployment.**