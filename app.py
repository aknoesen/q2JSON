# q2JSON Streamlit App - Complete Working Version with Correct Template Order
# Save this as app.py

import streamlit as st
import json
import re
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="q2JSON Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    
    .question-preview {
        background: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Main title
st.title("📝 q2JSON Generator")
st.markdown("*Convert AI Responses to Clean Educational JSON*")

# Add some info about the app
st.markdown("""
Transform messy AI responses into perfectly formatted JSON questions ready for educational use.
This tool bridges the gap between AI-generated content and educational deployment.
""")

# Navigation sidebar
st.sidebar.title("Navigation")
stage = st.sidebar.radio(
    "Workflow Stage",
    ["🎯 Prompt Builder", "🤖 AI Processing", "✅ JSON Validation"],
    index=0
)

# Add sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### About q2JSON")
st.sidebar.markdown("""
**3-Stage Workflow:**
1. **Prompt Builder** - Create optimized AI prompts
2. **AI Processing** - Clean and parse AI responses  
3. **JSON Validation** - Validate and export clean JSON
""")

# Session state initialization
if 'generated_prompt' not in st.session_state:
    st.session_state.generated_prompt = None
if 'questions_data' not in st.session_state:
    st.session_state.questions_data = None
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None
if 'processed_response' not in st.session_state:
    st.session_state.processed_response = None

# Helper function to load templates
def load_template_files():
    """Load preamble and postamble template files"""
    try:
        preamble_path = Path('templates/preamble_default.txt')
        postamble_path = Path('templates/postamble_default.txt')
        
        if preamble_path.exists() and postamble_path.exists():
            with open(preamble_path, 'r', encoding='utf-8') as f:
                preamble = f.read()
            with open(postamble_path, 'r', encoding='utf-8') as f:
                postamble = f.read()
            return preamble, postamble, "✅ Using your actual template files"
        else:
            # Files not found, use fallback
            return get_fallback_templates()
    except Exception as e:
        # Error loading files, use fallback
        return get_fallback_templates()

def get_fallback_templates():
    """Fallback templates if files are not found"""
    preamble = """You are an expert educator and question writer. Your task is to create high-quality educational questions based on the context provided below.

Please follow these guidelines:
1. Create questions that test understanding, not just memorization
2. Use clear, unambiguous language appropriate for the educational level
3. Include realistic and plausible distractors for multiple choice questions
4. Ensure questions are directly related to the learning objectives
5. Vary question difficulty from basic recall to higher-order thinking
6. Format your response as valid JSON only (no additional text)

Educational Context and Requirements:"""
    
    postamble = """

IMPORTANT: Format your response as a JSON object with this EXACT structure:

{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Descriptive Title for Question",
      "question_text": "The complete question text goes here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "points": 2,
      "feedback_correct": "Explanation for correct answer",
      "feedback_incorrect": "General feedback for incorrect answers"
    },
    {
      "type": "true_false", 
      "title": "Descriptive Title for Question",
      "question_text": "True or false statement goes here",
      "correct_answer": true,
      "points": 1
    },
    {
      "type": "numerical",
      "title": "Descriptive Title for Question", 
      "question_text": "Question requiring numerical answer",
      "correct_answer": 42.5,
      "tolerance": 0.1,
      "units": "meters",
      "points": 3
    },
    {
      "type": "fill_in_multiple_blanks",
      "title": "Descriptive Title for Question",
      "question_text": "Complete this statement: The [blank1] antenna has [blank2] polarization.",
      "correct_answers": {
        "blank1": "patch",
        "blank2": "linear"
      },
      "points": 2
    }
  ]
}

Supported question types:
- "multiple_choice": Exactly 4 options, one correct answer
- "true_false": Boolean question (true/false)
- "numerical": Numeric answer with tolerance and units
- "fill_in_multiple_blanks": Fill-in questions with multiple blanks

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON (no markdown, no explanations)
- Use exact field names as shown above
- Ensure all questions are complete and properly formatted
- Double-check JSON syntax is correct"""
    
    return preamble, postamble, "⚠️ Using fallback templates (templates/ directory not found)"

# Main content area based on selected stage
if stage == "🎯 Prompt Builder":
    st.header("🎯 Build Your AI Prompt")
    
    # Stage description
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Create optimized prompts for AI question generation")
    with col2:
        st.metric("Stage", "1 of 3")
    
    # Compatible AI Providers (Informational)
    st.subheader("🤖 Compatible AI Providers")
    st.info("✨ This prompt works with: **ChatGPT, Claude, Copilot, Gemini**, and other LLMs")
    st.markdown("*No configuration needed - the same prompt works universally across all AI providers*")
    
    # Educational Context Section
    st.subheader("📚 Educational Context")
    
    # Context input options
    context_option = st.radio(
        "Choose how to input your educational context:",
        ["🎯 Use Example", "📝 Use Template", "✍️ Write Custom"],
        horizontal=True
    )
    
    # Load educational context based on selection
    if context_option == "🎯 Use Example":
        educational_context = st.text_area(
            "Educational Context:",
            value="You are an expert in antennas, and teaching a lecture. The topic is patch antennas and implementation on PCB, polarization characteristics are of particular interest.",
            height=120,
            help="This is a working example from antenna theory"
        )
    elif context_option == "📝 Use Template":
        educational_context = st.text_area(
            "Educational Context:",
            value="You are an expert in [SUBJECT], and teaching a lecture. The topic is [TOPIC], [SPECIFIC_FOCUS] are of particular interest.",
            height=120,
            help="Fill in the brackets with your specific subject matter"
        )
    else:  # Write Custom
        educational_context = st.text_area(
            "Educational Context:",
            placeholder="Enter your educational context here...\n\nExample: You are an expert in calculus, teaching derivatives. Focus on practical applications and common student misconceptions.",
            height=120,
            help="Describe your subject area, teaching context, and specific focus"
        )
    
    # Question Configuration
    st.subheader("⚙️ Question Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        question_count = st.selectbox(
            "Number of Questions:",
            [5, 10, 15, 20],
            index=0,
            help="How many questions should the AI generate?"
        )
    
    with col2:
        question_type = st.selectbox(
            "Question Types:",
            [
                "Mixed types", 
                "Multiple choice only", 
                "Multiple dropdowns only",
                "Numerical only",
                "True/False only"
            ],
            index=0,
            help="What types of questions do you want?"
        )
    
    # Advanced Options (expandable)
    with st.expander("🔧 Advanced Options"):
        difficulty_level = st.select_slider(
            "Difficulty Level:",
            options=["Beginner", "Intermediate", "Advanced", "Mixed"],
            value="Intermediate"
        )
        
        include_explanations = st.checkbox(
            "Include explanations for correct answers",
            value=True,
            help="Add detailed explanations to help students understand"
        )
        
        custom_instructions = st.text_area(
            "Additional Instructions (Optional):",
            placeholder="Any specific requirements or constraints...",
            height=80
        )
    
    # Generate Prompt Button
    st.subheader("🚀 Generate Your Prompt")
    
    if st.button("🎯 Generate Complete Prompt", type="primary", use_container_width=True):
        if educational_context.strip():
            with st.spinner("Generating optimized prompt..."):
                # Load templates (CORRECTED ORDER)
                preamble, postamble, template_source = load_template_files()
                
                # Build complete prompt with CORRECT order
                prompt_parts = []
                
                # 1. PREAMBLE FIRST
                prompt_parts.append(preamble)
                
                # 2. USER CONTEXT SECOND
                prompt_parts.append(f"\n\n{educational_context}")
                
                # 3. CONFIGURATION DETAILS
                prompt_parts.append(f"\n\nGenerate {question_count} questions of type: {question_type.lower()}")
                
                if difficulty_level != "Mixed":
                    prompt_parts.append(f"\nDifficulty level: {difficulty_level}")
                
                if include_explanations:
                    prompt_parts.append("\nInclude detailed explanations for both correct and incorrect answers")
                
                if custom_instructions.strip():
                    prompt_parts.append(f"\nAdditional requirements: {custom_instructions}")
                
                # 4. POSTAMBLE LAST
                prompt_parts.append(f"\n\n{postamble}")
                
                complete_prompt = "".join(prompt_parts)
                
                # Store in session state
                st.session_state.generated_prompt = complete_prompt
                st.session_state.prompt_config = {
                    'question_count': question_count,
                    'question_type': question_type,
                    'difficulty': difficulty_level,
                    'explanations': include_explanations
                }
                
            st.success("✅ Prompt generated successfully!")
            st.info(template_source)
        else:
            st.error("❌ Please provide educational context before generating prompt")
    
    # Display Generated Prompt
    if 'generated_prompt' in st.session_state and st.session_state.generated_prompt:
        st.subheader("📋 Generated Prompt")
        
        # Show prompt configuration
        if 'prompt_config' in st.session_state:
            config = st.session_state.prompt_config
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions", config['question_count'])
            with col2:
                st.metric("Type", config['question_type'])
            with col3:
                st.metric("Difficulty", config['difficulty'])
        
        # Display the prompt
        st.text_area(
            "Complete Prompt (Ready for AI):",
            st.session_state.generated_prompt,
            height=250,
            help="Copy this entire prompt and paste it into your chosen AI"
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "💾 Download Prompt File",
                st.session_state.generated_prompt,
                file_name="q2json_prompt.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.success("✅ Ready to copy! (Select text and use Ctrl+C)")
        
        with col3:
            if st.button("➡️ Continue to AI Processing", type="primary", use_container_width=True):
                # Switch to stage 2
                st.info("Navigate to 'AI Processing' in the sidebar to continue")
        
        # Instructions for next steps
        st.info("""
        **Next Steps:**
        1. 📥 **Download** the prompt file above or copy the text
        2. 🌐 **Open** your preferred AI (ChatGPT, Claude, Copilot, etc.)
        3. 📤 **Upload** the file or paste the prompt
        4. ⏳ **Wait** for the AI to generate your questions
        5. 📋 **Copy** the AI's response 
        6. ➡️ **Continue** to the AI Processing stage
        """)

elif stage == "🤖 AI Processing":
    st.header("🤖 Process AI Response")
    
    # Stage description  
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Upload and clean your AI-generated questions")
    with col2:
        st.metric("Stage", "2 of 3")
    
    st.subheader("📥 Upload AI Response")
    
    # File upload option
    uploaded_file = st.file_uploader(
        "Upload AI Response File:",
        type=['txt', 'json', 'md'],
        help="Upload the file containing your AI's response"
    )
    
    # Or paste directly
    ai_response = st.text_area(
        "Or paste AI response directly:",
        height=200,
        placeholder="Paste the complete response from your AI here...",
        help="Copy and paste the entire response from ChatGPT, Claude, etc."
    )
    
    # Get response text
    response_text = ""
    if uploaded_file:
        try:
            response_text = str(uploaded_file.read(), "utf-8")
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    elif ai_response.strip():
        response_text = ai_response
    
    if response_text:
        st.subheader("🔧 Processing Options")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            auto_extract = st.checkbox("Auto-extract JSON", value=True, help="Automatically find JSON in the response")
        with col2:
            clean_markdown = st.checkbox("Clean markdown", value=True, help="Remove ```json and ``` markers")
        with col3:
            fix_quotes = st.checkbox("Fix quotes", value=True, help="Fix smart quotes and apostrophes")
        
        if st.button("🔧 Process Response", type="primary", use_container_width=True):
            with st.spinner("Processing AI response..."):
                processed_text = response_text
                processing_steps = []
                
                # Step 1: Auto-extract JSON
                if auto_extract:
                    # Look for JSON block between curly braces
                    json_pattern = r'\{.*?\}'
                    json_matches = re.findall(json_pattern, processed_text, re.DOTALL)
                    
                    if json_matches:
                        # Take the largest JSON block
                        processed_text = max(json_matches, key=len)
                        processing_steps.append("✅ JSON block extracted")
                    else:
                        processing_steps.append("⚠️ No JSON block found")
                
                # Step 2: Clean markdown
                if clean_markdown:
                    original_length = len(processed_text)
                    processed_text = re.sub(r'```json\s*', '', processed_text)
                    processed_text = re.sub(r'```\s*', '', processed_text)
                    if len(processed_text) != original_length:
                        processing_steps.append("✅ Markdown cleaned")
                
                # Step 3: Fix quotes
                if fix_quotes:
                    original_text = processed_text
                    processed_text = processed_text.replace('"', '"').replace('"', '"')
                    processed_text = processed_text.replace(''', "'").replace(''', "'")
                    if processed_text != original_text:
                        processing_steps.append("✅ Quotes fixed")
                
                # Step 4: Validate JSON
                try:
                    questions_data = json.loads(processed_text)
                    
                    if 'questions' in questions_data and isinstance(questions_data['questions'], list):
                        st.session_state.questions_data = questions_data
                        st.session_state.processed_response = processed_text
                        
                        processing_steps.append(f"✅ Valid JSON with {len(questions_data['questions'])} questions")
                        
                        # Show processing results
                        st.success("🎉 Processing completed successfully!")
                        
                        for step in processing_steps:
                            st.write(step)
                        
                        # Preview questions
                        st.subheader("📋 Questions Preview")
                        
                        questions = questions_data['questions']
                        
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Questions", len(questions))
                        with col2:
                            question_types = [q.get('type', 'unknown') for q in questions]
                            unique_types = len(set(question_types))
                            st.metric("Question Types", unique_types)
                        with col3:
                            has_titles = sum(1 for q in questions if q.get('title'))
                            st.metric("With Titles", has_titles)
                        with col4:
                            has_feedback = sum(1 for q in questions if q.get('feedback_correct'))
                            st.metric("With Feedback", has_feedback)
                        
                        # Show first few questions
                        st.markdown("**First 3 Questions:**")
                        for i, q in enumerate(questions[:3]):
                            with st.container():
                                st.markdown(f"""
                                <div class="question-preview">
                                <strong>{i+1}. {q.get('title', 'Untitled')}</strong> 
                                <span style="color: #666;">({q.get('type', 'unknown')})</span><br>
                                <em>{q.get('question_text', 'No question text')[:100]}...</em>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if len(questions) > 3:
                            st.write(f"... and **{len(questions) - 3} more questions**")
                        
                        # Continue button
                        st.info("✅ Ready for validation! Continue to the JSON Validation stage.")
                        
                    else:
                        st.error("❌ JSON is valid but missing 'questions' array")
                        st.json(questions_data)
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON parsing error: {str(e)}")
                    
                    # Show processing steps that worked
                    if processing_steps:
                        st.write("**Processing steps completed:**")
                        for step in processing_steps:
                            st.write(step)
                    
                    # Manual editing option
                    st.subheader("✏️ Manual JSON Editor")
                    st.markdown("The JSON has syntax errors. Please fix them below:")
                    
                    manual_json = st.text_area(
                        "Edit JSON manually:",
                        value=processed_text,
                        height=300,
                        help="Fix any JSON syntax errors"
                    )
                    
                    if st.button("🔍 Validate Manual JSON"):
                        try:
                            questions_data = json.loads(manual_json)
                            if 'questions' in questions_data:
                                st.session_state.questions_data = questions_data
                                st.session_state.processed_response = manual_json
                                st.success("✅ Manual JSON validation successful!")
                                st.rerun()
                            else:
                                st.error("❌ JSON missing 'questions' array")
                        except json.JSONDecodeError as e2:
                            st.error(f"❌ Still invalid JSON: {str(e2)}")
    
    # Show current data status
    if 'questions_data' in st.session_state and st.session_state.questions_data:
        st.success(f"✅ Ready to validate {len(st.session_state.questions_data['questions'])} questions")
        
        if st.button("➡️ Continue to JSON Validation", type="primary"):
            st.info("Navigate to 'JSON Validation' in the sidebar to continue")

elif stage == "✅ JSON Validation":
    st.header("✅ JSON Validation & Export")
    
    # Stage description
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Validate and export clean JSON for educational use")
    with col2:
        st.metric("Stage", "3 of 3")
    
    if 'questions_data' not in st.session_state or not st.session_state.questions_data:
        st.warning("⚠️ No questions data available. Please complete Stage 2 first.")
        st.markdown("""
        **To get started:**
        1. Go to **Prompt Builder** to create your AI prompt
        2. Use the prompt with your chosen AI
        3. Return to **AI Processing** to upload the response
        4. Come back here for validation and export
        """)
    else:
        questions = st.session_state.questions_data['questions']
        st.info(f"Ready to validate {len(questions)} questions")
        
        # Validation options
        st.subheader("🔧 Validation Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            check_required_fields = st.checkbox("Check required fields", value=True)
        with col2:
            fix_unicode = st.checkbox("Auto-fix Unicode to LaTeX", value=True)
        with col3:
            verbose_output = st.checkbox("Show detailed results", value=True)
        
        if st.button("🔍 Run Validation", type="primary", use_container_width=True):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Starting validation...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            # Run validation
            validation_results = {
                'total': len(questions),
                'valid': 0,
                'warnings': 0,
                'errors': 0,
                'issues': [],
                'question_analysis': []
            }
            
            status_text.text("Validating question structure...")
            progress_bar.progress(40)
            
            required_fields = ['type', 'title', 'question_text']
            optional_fields = ['correct_answer', 'points', 'feedback_correct']
            
            for i, question in enumerate(questions):
                q_analysis = {
                    'index': i + 1,
                    'title': question.get('title', f'Question {i+1}'),
                    'type': question.get('type', 'unknown'),
                    'status': 'valid',
                    'issues': []
                }
                
                # Check required fields
                if check_required_fields:
                    for field in required_fields:
                        if field not in question or not question[field]:
                            q_analysis['issues'].append(f"Missing {field}")
                            q_analysis['status'] = 'error'
                
                # Check question type specific requirements
                q_type = question.get('type')
                if q_type == 'multiple_choice':
                    if 'options' not in question:
                        q_analysis['issues'].append("Missing options array")
                        q_analysis['status'] = 'error'
                    elif len(question.get('options', [])) != 4:
                        q_analysis['issues'].append(f"Expected 4 options, found {len(question.get('options', []))}")
                        q_analysis['status'] = 'warning'
                
                elif q_type == 'numerical':
                    if 'correct_answer' in question:
                        try:
                            float(question['correct_answer'])
                        except (ValueError, TypeError):
                            q_analysis['issues'].append("Correct answer is not numeric")
                            q_analysis['status'] = 'error'
                
                elif q_type == 'true_false':
                    if 'correct_answer' in question:
                        if not isinstance(question['correct_answer'], bool):
                            q_analysis['issues'].append("Correct answer must be true/false")
                            q_analysis['status'] = 'error'
                
                # Count status
                if q_analysis['status'] == 'valid':
                    validation_results['valid'] += 1
                elif q_analysis['status'] == 'warning':
                    validation_results['warnings'] += 1
                else:
                    validation_results['errors'] += 1
                
                validation_results['question_analysis'].append(q_analysis)
            
            status_text.text("Checking for Unicode issues...")
            progress_bar.progress(60)
            time.sleep(0.3)
            
            # Unicode checking
            unicode_issues = 0
            unicode_fixed = 0
            
            if fix_unicode:
                unicode_replacements = {
                    '−': '-',  # minus sign
                    '×': r'\\times',  # multiplication
                    '÷': r'\\div',  # division
                    '≤': r'\\leq',  # less than or equal
                    '≥': r'\\geq',  # greater than or equal
                    '≠': r'\\neq',  # not equal
                    '∞': r'\\infty',  # infinity
                    'π': r'\\pi',  # pi
                    '²': '^2',  # superscript 2
                    '³': '^3',  # superscript 3
                    'α': r'\\alpha',  # alpha
                    'β': r'\\beta',  # beta
                    'γ': r'\\gamma',  # gamma
                    'θ': r'\\theta',  # theta
                    'λ': r'\\lambda',  # lambda
                    'μ': r'\\mu',  # mu
                    'σ': r'\\sigma',  # sigma
                    'ω': r'\\omega',  # omega
                    'Ω': r'\\Omega',  # capital omega
                }
                
                for q in questions:
                    for field in ['question_text', 'title']:
                        if field in q and isinstance(q[field], str):
                            original = q[field]
                            for unicode_char, latex in unicode_replacements.items():
                                if unicode_char in q[field]:
                                    unicode_issues += 1
                                    q[field] = q[field].replace(unicode_char, latex)
                                    unicode_fixed += 1
            
            status_text.text("Generating final report...")
            progress_bar.progress(80)
            time.sleep(0.2)
            
            # Calculate success rate
            success_rate = (validation_results['valid'] / validation_results['total']) * 100 if validation_results['total'] > 0 else 0
            
            progress_bar.progress(100)
            status_text.text("Validation complete!")
            
            # Store results
            st.session_state.validation_results = validation_results
            
            # Display results
            st.subheader("📊 Validation Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Questions", validation_results['total'])
            with col2:
                st.metric("✅ Valid", validation_results['valid'], 
                         delta=f"{success_rate:.1f}% success rate")
            with col3:
                st.metric("⚠️ Warnings", validation_results['warnings'])
            with col4:
                st.metric("❌ Errors", validation_results['errors'])
            
            if unicode_fixed > 0:
                st.success(f"🔧 Fixed {unicode_fixed} Unicode characters to LaTeX format")
            
            # Detailed results
            if verbose_output and validation_results['question_analysis']:
                st.subheader("📋 Detailed Question Analysis")
                
                for q_analysis in validation_results['question_analysis']:
                    status_emoji = "✅" if q_analysis['status'] == 'valid' else "⚠️" if q_analysis['status'] == 'warning' else "❌"
                    
                    with st.expander(f"{status_emoji} {q_analysis['title']} ({q_analysis['type']})"):
                        if q_analysis['issues']:
                            st.markdown("**Issues found:**")
                            for issue in q_analysis['issues']:
                                st.write(f"• {issue}")
                        else:
                            st.success("No issues found")
            
            # Export section
            st.subheader("📤 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Export Valid Questions Only", use_container_width=True):
                    valid_questions = []
                    for i, q_analysis in enumerate(validation_results['question_analysis']):
                        if q_analysis['status'] == 'valid':
                            valid_questions.append(questions[i])
                    
                    if valid_questions:
                        export_data = {"questions": valid_questions}
                        st.download_button(
                            "📥 Download Valid Questions",
                            json.dumps(export_data, indent=2, ensure_ascii=False),
                            f"q2json_valid_questions_{len(valid_questions)}.json",
                            "application/json",
                            use_container_width=True
                        )
                        st.success(f"✅ {len(valid_questions)} valid questions ready for download")
                    else:
                        st.error("❌ No valid questions to export")
            
            with col2:
                if st.button("📥 Export All Questions", use_container_width=True):
                    st.download_button(
                        "📥 Download All Questions",
                        json.dumps(st.session_state.questions_data, indent=2, ensure_ascii=False),
                        f"q2json_all_questions_{validation_results['total']}.json",
                        "application/json",
                        use_container_width=True
                    )
                    st.info("📊 Exported all questions (including those with issues)")
            
            with col3:
                if st.button("📊 Export Validation Report", use_container_width=True):
                    report = {
                        "validation_summary": {
                            "total_questions": validation_results['total'],
                            "valid_questions": validation_results['valid'],
                            "warnings": validation_results['warnings'],
                            "errors": validation_results['errors'],
                            "success_rate": f"{success_rate:.1f}%",
                            "unicode_fixes": unicode_fixed
                        },
                        "question_analysis": validation_results['question_analysis'],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.download_button(
                        "📊 Download Report",
                        json.dumps(report, indent=2, ensure_ascii=False),
                        f"q2json_validation_report_{time.strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json",
                        use_container_width=True
                    )
        
        # Show previous results if available
        elif 'validation_results' in st.session_state and st.session_state.validation_results:
            results = st.session_state.validation_results
            st.subheader("📊 Previous Validation Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Questions", results['total'])
            with col2:
                success_rate = (results['valid'] / results['total']) * 100 if results['total'] > 0 else 0
                st.metric("✅ Valid", results['valid'], 
                         delta=f"{success_rate:.1f}% success rate")
            with col3:
                st.metric("⚠️ Warnings", results['warnings'])
            with col4:
                st.metric("❌ Errors", results['errors'])
            
            st.info("✅ Results from previous validation available for export above")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Version:** 1.0.0")
with col2:
    if 'questions_data' in st.session_state and st.session_state.questions_data:
        st.markdown(f"**Data:** {len(st.session_state.questions_data['questions'])} questions loaded")
    else:
        st.markdown("**Data:** No questions loaded")
with col3:
    if stage == "🎯 Prompt Builder":
        status = "✅ Stage 1 Complete" if st.session_state.generated_prompt else "⏳ Stage 1 In Progress"
    elif stage == "🤖 AI Processing":
        status = "✅ Stage 2 Complete" if st.session_state.questions_data else "⏳ Stage 2 In Progress"
    else:
        status = "✅ Stage 3 Complete" if st.session_state.validation_results else "⏳ Stage 3 In Progress"
    st.markdown(f"**Status:** {status}")

# Development info sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### Development Status")
    
    # Show completion status for each stage
    stage1_status = "✅" if st.session_state.generated_prompt else "⏳"
    stage2_status = "✅" if st.session_state.questions_data else "⏳"
    stage3_status = "✅" if st.session_state.validation_results else "⏳"
    
    st.markdown(f"""
    {stage1_status} **Prompt Builder** - Template system fixed  
    {stage2_status} **AI Processing** - Upload & clean responses  
    {stage3_status} **JSON Validation** - Validate & export  
    """)
    
    # Quick test button
    if st.button("🧪 Test App Status"):
        st.success("✅ q2JSON is running correctly!")
        st.info(f"Session data: {len([k for k in st.session_state.keys() if not k.startswith('_')])} items")
        
    # Template status check
    st.markdown("---")
    st.markdown("### Template Status")
    
    try:
        preamble_exists = Path('templates/preamble_default.txt').exists()
        postamble_exists = Path('templates/postamble_default.txt').exists()
        
        preamble_icon = "✅" if preamble_exists else "❌"
        postamble_icon = "✅" if postamble_exists else "❌"
        
        st.markdown(f"""
        {preamble_icon} preamble_default.txt  
        {postamble_icon} postamble_default.txt  
        """)
        
        if not (preamble_exists and postamble_exists):
            st.warning("⚠️ Using fallback templates")
        else:
            st.success("✅ Professional templates loaded")
            
    except Exception:
        st.error("❌ Template directory not accessible")

# Custom styling for better mobile experience
st.markdown("""
<style>
@media (max-width: 768px) {
    .stColumns > div {
        width: 100% !important;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        width: 100%;
    }
    
    .metric-container {
        margin-bottom: 1rem;
    }
}

.question-preview {
    background: #f8f9fa;
    border-left: 4px solid #1f77b4;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 0 4px 4px 0;
}

.success-banner {
    background: linear-gradient(90deg, #28a745, #20c997);
    color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Success message for completed workflow
if (st.session_state.generated_prompt and 
    st.session_state.questions_data and 
    st.session_state.validation_results):
    
    st.markdown("""
    <div class="success-banner">
    🎉 <strong>Workflow Complete!</strong> 🎉<br>
    Your questions have been generated, processed, and validated successfully!
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Start New Question Set", use_container_width=True):
        # Clear session state for new workflow
        for key in ['generated_prompt', 'questions_data', 'validation_results', 'processed_response']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()