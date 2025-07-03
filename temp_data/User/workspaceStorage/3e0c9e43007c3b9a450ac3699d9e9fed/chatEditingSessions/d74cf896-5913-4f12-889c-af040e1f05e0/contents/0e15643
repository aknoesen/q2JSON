# stages/stage_1_processing.py
import streamlit as st
import re
from navigation.manager import NavigationManager

def render_ai_processing():
    """Render the complete AI Processing stage - JSON Processing Focus"""
    
    # Progress indicator
    progress = (st.session_state.current_stage + 1) / 4
    st.progress(progress)
    st.markdown(f"**Stage {st.session_state.current_stage + 1} of 4**: AI Processing")

    st.header("🤖 Process AI JSON Response")
    
    # Stage description  
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Upload and process JSON responses from AI question generation")
        st.markdown("**This stage accepts only JSON files or JSON content**")
    with col2:
        st.metric("Stage", "2 of 4")
    
    st.subheader("📥 Upload AI Response")
    
    # Information about expected JSON format
    with st.expander("📋 Expected JSON Format"):
        st.markdown("""
        **This stage expects JSON content from AI responses containing educational questions.**
        
        **✅ Supported JSON structures:**
        - Questions wrapped in `{"questions": [...]}`
        - Direct question arrays `[{question1}, {question2}, ...]`
        - AI responses with JSON blocks (will be auto-extracted)
        
        **📝 Typical JSON from AI:**
        ```json
        {
          "questions": [
            {
              "question": "What is the primary function of...",
              "type": "multiple_choice",
              "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
              "correct_answer": "B) Option 2"
            }
          ]
        }
        ```
        """)
    
    # File upload option - JSON only
    st.markdown("**Option 1: Upload JSON File**")
    uploaded_file = st.file_uploader(
        "Upload JSON Response File:",
        type=['json'],
        help="Upload the JSON file containing your AI's response. Only .json files are accepted."
    )
    
    # File validation and feedback
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension != 'json':
            st.error(f"❌ **Invalid file type detected: .{file_extension}**")
            st.error("🚫 Only JSON files (.json) are allowed in this stage")
            st.info("💡 **Tip:** If you have a text file with JSON content, please:")
            st.markdown("""
            - Copy the JSON content from your file
            - Paste it in the text area below
            - Or save your file with a .json extension
            """)
            uploaded_file = None  # Clear the invalid file
        else:
            st.success(f"✅ Valid JSON file detected: **{uploaded_file.name}**")
    
    st.markdown("---")
    st.markdown("**Option 2: Paste JSON Content**")
    
    # Or paste directly
    ai_response = st.text_area(
        "Paste JSON response directly:",
        height=200,
        placeholder="Paste the complete JSON response from your AI here...\n\nExample:\n{\n  \"questions\": [\n    {\n      \"question\": \"What is...\",\n      \"type\": \"multiple_choice\"\n    }\n  ]\n}",
        help="Copy and paste JSON content from ChatGPT, Claude, etc."
    )
    
    # Get response text with validation
    response_text = get_response_text(uploaded_file, ai_response)
    
    # Help section for users with non-JSON files
    if not response_text and not uploaded_file:
        st.markdown("---")
        st.markdown("### 🆘 Need Help Getting JSON from Your AI?")
        
        with st.expander("💡 How to Get JSON from Different AI Providers"):
            st.markdown("""
            **If your AI gave you a text file instead of JSON:**
            
            **📝 From ChatGPT/Claude/Copilot:**
            1. Ask your AI: *"Please provide the output in JSON format"*
            2. Copy the JSON response (usually starts with `{` or `[`)
            3. Paste it in the text area above
            
            **💾 From a downloaded file:**
            1. Open your text file
            2. Look for JSON content (starts with `{` or `[`)
            3. Copy the JSON portion
            4. Paste it in the text area above
            
            **🔧 Quick Fix:**
            - If you have a `.txt` file with JSON content, simply copy the content and paste it above
            - Or rename your file from `.txt` to `.json` and upload it
            """)
    
    if response_text:
        render_processing_options(response_text)
    
    # Display results if processing completed
    display_processing_results()


def get_response_text(uploaded_file, ai_response):
    """Extract and validate JSON response text from file upload or direct input"""
    response_text = ""
    
    if uploaded_file:
        try:
            # Read file content
            response_text = str(uploaded_file.read(), "utf-8")
            
            # Additional JSON validation
            import json
            try:
                # Test if it's valid JSON
                json.loads(response_text)
                st.success(f"✅ **Valid JSON file loaded:** {uploaded_file.name}")
                st.info(f"📊 **File size:** {len(response_text)} characters")
            except json.JSONDecodeError as je:
                st.warning(f"⚠️ **JSON syntax warning in {uploaded_file.name}:**")
                st.warning(f"```\n{str(je)}\n```")
                st.info("🔧 **Don't worry!** The processing stage can often fix common JSON issues automatically.")
                
        except UnicodeDecodeError:
            st.error(f"❌ **Encoding error:** Cannot read {uploaded_file.name}")
            st.error("💡 **Tip:** Ensure your file is saved as UTF-8 text")
            return ""
        except Exception as e:
            st.error(f"❌ **File read error:** {str(e)}")
            return ""
            
    elif ai_response.strip():
        response_text = ai_response
        
        # Validate pasted JSON content
        import json
        try:
            json.loads(response_text)
            st.success("✅ **Valid JSON content detected**")
        except json.JSONDecodeError as je:
            st.warning("⚠️ **JSON syntax warning in pasted content:**")
            st.warning(f"```\n{str(je)}\n```")
            st.info("🔧 **Don't worry!** The processing stage can often fix common JSON issues automatically.")
    
    return response_text


def render_processing_options(response_text):
    """Render JSON processing options and handle processing button"""
    
    st.subheader("🔧 JSON Processing Options")
    
    # Show content preview
    with st.expander("👀 Preview JSON Content"):
        preview_length = min(500, len(response_text))
        st.code(response_text[:preview_length] + ("..." if len(response_text) > preview_length else ""), language="json")
        st.caption(f"Showing first {preview_length} characters of {len(response_text)} total")
    
    # Auto-advance notification
    st.info("🚀 **Auto-Advance Enabled:** After processing, you'll automatically move to the Download Questions stage")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_extract = st.checkbox("Auto-extract JSON", value=True, 
                                 help="Automatically find JSON blocks in AI responses")
        clean_markdown = st.checkbox("Clean markdown", value=True, 
                                    help="Remove ```json and ``` code block markers")
    with col2:
        fix_quotes = st.checkbox("Fix quotes", value=True, 
                               help="Fix smart quotes and apostrophes in JSON")
        fix_chatgpt = st.checkbox("Fix ChatGPT quirks", value=True, 
                                help="Fix escaped underscores and brackets from ChatGPT")
    
    # Processing button with JSON validation and auto-advance
    if st.button("� Process JSON & Continue to Download", type="primary", use_container_width=True):
        # Pre-processing validation
        if not response_text.strip():
            st.error("❌ No JSON content to process. Please upload a file or paste JSON content.")
            return
            
        # Check if content looks like JSON
        stripped_content = response_text.strip()
        if not (stripped_content.startswith('{') or stripped_content.startswith('[')):
            st.warning("⚠️ Content doesn't appear to start with JSON. Processing anyway...")
            
        process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_chatgpt)


def process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_chatgpt):
    """Process the AI response with selected options and auto-advance to stage 2"""
    
    with st.spinner("Processing JSON response..."):
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
        
        # Step 6: Auto-advance to Stage 2 (JSON Validation & Download)
        if processed_text and processed_text.strip():
            st.success("🎉 JSON processing completed successfully!")
            st.info("🚀 **Automatically advancing to JSON Validation & Download stage...**")
            
            # Show brief processing summary
            st.markdown("**Processing Summary:**")
            for step in processing_steps:
                st.write(f"- {step}")
            
            # Auto-advance to stage 2
            import time
            time.sleep(1)  # Brief pause for user to see the message
            NavigationManager.advance_stage(2, source="auto_advance")
        else:
            st.error("❌ Processing failed - no valid JSON content extracted")
            st.warning("Please check your input and try again")


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
    """Display processing results if completed (legacy function - auto-advance now used)"""
    
    # This function is now primarily for displaying results when user navigates back
    if st.session_state.get("processing_completed"):
        st.info("🔄 **Processing already completed** - results are stored and ready for validation")
        
        # Show processing steps
        if st.session_state.get("processing_steps"):
            with st.expander("📋 View Processing Summary"):
                for step in st.session_state.get("processing_steps", []):
                    st.write(f"- {step}")
        
        # Show JSON preview
        if st.session_state.get("raw_extracted_json"):
            with st.expander("� View Processed JSON Preview"):
                preview = st.session_state.get("raw_extracted_json", "")
                preview_text = preview[:500] + "..." if len(preview) > 500 else preview
                st.code(preview_text, language="json")
            
            # Manual navigation option (backup)
            st.markdown("---")
            st.markdown("**Manual Navigation:**")
            NavigationManager.create_navigation_selector(
                target_stage=2,
                label="Go to JSON Validation & Download"
            )