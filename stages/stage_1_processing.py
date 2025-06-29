# stages/stage_1_processing.py
import streamlit as st
import re
from navigation.manager import NavigationManager

def render_ai_processing():
    """Render the complete AI Processing stage - NO MORE INDENTATION HELL!"""
    
    # Progress indicator
    progress = (st.session_state.current_stage + 1) / 3
    st.progress(progress)
    st.markdown(f"**Stage {st.session_state.current_stage + 1} of 3**: AI Processing")

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
    response_text = get_response_text(uploaded_file, ai_response)
    
    if response_text:
        render_processing_options(response_text)
    
    # Display results if processing completed
    display_processing_results()


def get_response_text(uploaded_file, ai_response):
    """Extract response text from file upload or direct input"""
    response_text = ""
    
    if uploaded_file:
        try:
            response_text = str(uploaded_file.read(), "utf-8")
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    elif ai_response.strip():
        response_text = ai_response
    
    return response_text


def render_processing_options(response_text):
    """Render processing options and handle processing button"""
    
    st.subheader("🔧 Processing Options")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_extract = st.checkbox("Auto-extract JSON", value=True, 
                                 help="Automatically find JSON in the response")
        clean_markdown = st.checkbox("Clean markdown", value=True, 
                                    help="Remove ```json and ``` markers")
    with col2:
        fix_quotes = st.checkbox("Fix quotes", value=True, 
                               help="Fix smart quotes and apostrophes")
        fix_chatgpt = st.checkbox("Fix ChatGPT quirks", value=True, 
                                help="Fix escaped underscores and brackets")
    
    if st.button("🔧 Process Response", type="primary", use_container_width=True):
        process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_chatgpt)


def process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_chatgpt):
    """Process the AI response with selected options"""
    
    with st.spinner("Processing AI response..."):
        processed_text = response_text
        processing_steps = []
        
        # Step 1: Auto-extract JSON
        if auto_extract:
            processed_text, step_msg = extract_json_from_response(processed_text)
            processing_steps.append(step_msg)
        
        # Step 2: Clean markdown
        if clean_markdown:
            processed_text, step_msg = clean_markdown_formatting(processed_text)
            if step_msg:
                processing_steps.append(step_msg)
        
        # Step 3: Fix quotes
        if fix_quotes:
            processed_text, step_msg = fix_quote_characters(processed_text)
            if step_msg:
                processing_steps.append(step_msg)
        
        # Step 4: Fix ChatGPT quirks  
        if fix_chatgpt:
            processed_text, step_msg = fix_chatgpt_quirks(processed_text)
            if step_msg:
                processing_steps.append(step_msg)

        # Step 5: Store results
        st.session_state.raw_extracted_json = processed_text
        st.session_state.processing_steps = processing_steps
        st.session_state.processing_completed = True


def extract_json_from_response(text):
    """Extract JSON from AI response text"""
    
    # Method 1: Try to find complete JSON object with proper brace counting
    def extract_complete_json(text):
        start = text.find('{')
        if start == -1:
            return None
            
        brace_count = 0
        for i, char in enumerate(text[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start:i+1]
        return None
    
    # Try to extract complete JSON
    extracted_json = extract_complete_json(text)
    
    if extracted_json:
        return extracted_json, "✅ Complete JSON object extracted"
    else:
        # Fallback: look for JSON between triple backticks
        json_block_pattern = r'```json\s*(\{.*?\})\s*```'
        json_match = re.search(json_block_pattern, text, re.DOTALL)
        if json_match:
            return json_match.group(1), "✅ JSON extracted from code block"
        else:
            return text, "⚠️ No complete JSON found - using full response"


def clean_markdown_formatting(text):
    """Remove markdown formatting from text"""
    original_length = len(text)
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    if len(text) != original_length:
        return text, "✅ Markdown cleaned"
    else:
        return text, None


def fix_quote_characters(text):
    """Fix smart quotes and apostrophes"""
    original_text = text
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    if text != original_text:
        return text, "✅ Quotes fixed"
    else:
        return text, None


def fix_chatgpt_quirks(text):
    """Fix common ChatGPT formatting issues"""
    original_text = text
    # Basic escape fixes only - let modular processor handle complex repairs
    text = text.replace('\\_', '_')
    text = text.replace('\\[', '[').replace('\\]', ']')
    
    if text != original_text:
        return text, "✅ Basic ChatGPT fixes applied"
    else:
        return text, None


def display_processing_results():
    """Display processing results if completed - CLEAN FUNCTION, NO INDENTATION ISSUES!"""
    
    if st.session_state.get("processing_completed"):
        st.success("🎉 Processing completed successfully!")
        
        # Show processing steps
        for step in st.session_state.get("processing_steps", []):
            st.write(step)
        
        # Show JSON preview
        st.subheader("📋 Extracted JSON Preview")
        preview = st.session_state.get("raw_extracted_json", "")
        preview_text = preview[:500] + "..." if len(preview) > 500 else preview
        st.code(preview_text, language="json")
        
        # Show navigation if we have JSON
        if st.session_state.get("raw_extracted_json"):
            st.info("✅ JSON extracted and ready for validation!")
            NavigationManager.create_navigation_selector(
                target_stage=2,
                label="Next: JSON Validation"
            )