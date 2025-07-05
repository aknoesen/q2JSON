# stages/stage_1_processing.py
import streamlit as st
import re
import json
from navigation.manager import NavigationManager
from utils.ui_helpers import show_stage_banner


def render_ai_processing():
    st.write(f"DEBUG: json module available: {json}")
    """Render the complete AI Processing stage - JSON Processing Focus"""
    # Progress indicator for 4 stages
    progress = (st.session_state.current_stage + 1) / 4
    st.progress(progress)

    # --- FIXED: Stage Banner at TOP, now shows "Stage 2 of 4" ---
    show_stage_banner(2, total_stages=4)

    st.header("🤖 AI Processing")
    st.markdown("**This stage accepts only JSON files or JSON content**")
    st.subheader("📤 Upload AI Response")

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

    # Option 1: Upload JSON file
    st.markdown("**Option 1: Upload JSON File**")
    uploaded_file = st.file_uploader(
        "Upload JSON Response File:",
        type=['json'],
        help="Upload the JSON file containing your AI's response. Only .json files are accepted."
    )

    # File validation and feedback
    file_valid = False
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
            file_valid = True

    st.markdown("---")
    st.markdown("**Option 2: Paste JSON Content**")
    ai_response = st.text_area(
        "Paste JSON response directly:",
        height=100,  # Reduced height from 200 to 100
        placeholder="Paste the complete JSON response from your AI here...",
        help="Copy and paste JSON content from ChatGPT, Claude, etc."
    )

    # Get response text with validation
    response_text = get_response_text(uploaded_file, ai_response)

    # Show file success/info only if file is valid and before processing
    if file_valid and response_text and not st.session_state.get("processing_completed"):
        st.success(f"✅ Valid JSON file loaded: {uploaded_file.name}")
        st.info(f"📊 File size: {len(response_text)} characters")

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
    st.info("🚀 **Auto-Advance Enabled:** After validation, you'll automatically move to the Download Questions stage")

    col1, col2 = st.columns(2)
    with col1:
        auto_extract = st.checkbox("Auto-extract JSON", value=True,
                                   help="Automatically find JSON blocks in AI responses")
        clean_markdown = st.checkbox("Clean markdown", value=True,
                                     help="Remove ```json and ``` code block markers")
    with col2:
        fix_quotes = st.checkbox("Fix quotes", value=True,
                                 help="Fix smart quotes and apostrophes in JSON")
        fix_llm = st.checkbox("Fix LLM quirks", value=True,
                              help="Fix escaped underscores and brackets from LLMs")

    # --- AUTO-VALIDATE if response_text is present and not already processed ---
    if response_text and not st.session_state.get("processing_completed"):
        # Immediately process and auto-advance
        process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_llm)
        return  # Prevent rendering the manual button below

    # (Manual button fallback, only shown if auto-processing is not triggered)
    validate_clicked = st.button("Validate JSON", use_container_width=True)
    if validate_clicked:
        if not response_text.strip():
            st.error("❌ No JSON content to validate. Please upload a file or paste JSON content.")
            return
        stripped_content = response_text.strip()
        if not (stripped_content.startswith('{') or stripped_content.startswith('[')):
            st.warning("⚠️ Content doesn't appear to start with JSON. Validating anyway...")
        process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_llm)


def process_ai_response(response_text, auto_extract, clean_markdown, fix_quotes, fix_llm):
    """Process the AI response with selected options and auto-advance to stage 3 (Human Review)"""
    
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
        if fix_llm:
            processed_text, step_msg = fix_chatgpt_quirks(processed_text)
            if step_msg:
                processing_steps.append(step_msg)

        # Step 5: Store results
        st.session_state.raw_extracted_json = processed_text
        st.session_state.processing_steps = processing_steps
        st.session_state.processing_completed = True

        # --- NEW: Parse and store validated questions for Stage 3 ---
        try:
            # Try to parse the processed JSON and extract questions
            parsed = json.loads(processed_text)
            if isinstance(parsed, dict) and "questions" in parsed:
                validated_questions = parsed["questions"]
                # Store as dict for Stage 3 compatibility
                st.session_state["questions_data"] = {"questions": validated_questions}
            elif isinstance(parsed, list):
                # Store as dict for Stage 3 compatibility
                st.session_state["questions_data"] = {"questions": parsed}
            else:
                st.session_state["questions_data"] = {"questions": []}
        except Exception as e:
            st.session_state["questions_data"] = {"questions": []}
            st.warning(f"Could not parse questions for review: {e}")

        # Step 6: Auto-advance to Stage 3 (Human Review & Editing) immediately if successful
        if processed_text and processed_text.strip() and st.session_state["questions_data"]["questions"]:
            st.session_state.current_stage = 2  # Stage 3 (Human Review) in UI
            st.rerun()
            return  # Prevent any UI rendering
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
    """Display processing results if completed (clean, clear next steps)"""


    if st.session_state.get("processing_completed"):
        questions_data = st.session_state.get("questions_data")
        has_questions = bool(questions_data and questions_data.get("questions"))

        if has_questions:
            st.success("✅ **Validation complete!** Your JSON has been processed and is ready for the next step.")
        else:
            st.error("❌ **Processing failed** - No valid questions extracted from JSON")

        # Show processing steps summary
        if st.session_state.get("processing_steps"):
            with st.expander("📋 View Processing Summary"):
                for step in st.session_state.get("processing_steps", []):
                    st.write(f"- {step}")

        # Show JSON preview
        if st.session_state.get("raw_extracted_json"):
            with st.expander("👀 View Processed JSON Preview"):
                preview = st.session_state.get("raw_extracted_json", "")
                preview_text = preview[:500] + "..." if len(preview) > 500 else preview
                st.code(preview_text, language="json")

        # Only show manual navigation buttons if processing was successful (has_questions)
        if has_questions:
            # Inject CSS for red and secondary action bars
            st.markdown(
                """
                <style>
                .red-action-bar button {
                    width: 100%;
                    background-color: #e53935;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                    border: none;
                    border-radius: 8px;
                    height: 3rem;
                    box-shadow: 0 2px 8px rgba(229,57,53,0.08);
                    transition: background 0.2s;
                    cursor: pointer;
                    margin-top: 2rem;
                    margin-bottom: 1rem;
                }
                .red-action-bar button:hover {
                    background-color: #b71c1c;
                }
                .secondary-action-bar button {
                    width: 100%;
                    background-color: #f5f5f5;
                    color: #333;
                    font-weight: bold;
                    font-size: 1.1rem;
                    border: 2px solid #bdbdbd;
                    border-radius: 8px;
                    height: 2.8rem;
                    margin-bottom: 2rem;
                    margin-top: 0.5rem;
                    transition: background 0.2s;
                    cursor: pointer;
                }
                .secondary-action-bar button:hover {
                    background-color: #e0e0e0;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Layout for next step buttons
            col1, col2 = st.columns([2, 1])
            with col1:
                continue_btn = st.markdown(
                    """
                    <form action="" method="post" class="red-action-bar">
                        <button type="submit" name="continue_human_review">Continue to Human Review and Editing</button>
                    </form>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                skip_btn = st.markdown(
                    """
                    <form action="" method="post" class="secondary-action-bar">
                        <button type="submit" name="skip_to_output">Skip to Output</button>
                    </form>
                    """,
                    unsafe_allow_html=True,
                )

            # Button logic using Streamlit's session state
            continue_clicked = st.button(" ", key="continue_human_review_hidden", help="hidden", use_container_width=True)
            skip_clicked = st.button(" ", key="skip_to_output_hidden", help="hidden", use_container_width=True)

            # Navigation logic (replace with your navigation manager as needed)
            if continue_clicked:
                NavigationManager.advance_stage(4, source="continue_human_review")
            elif skip_clicked:
                NavigationManager.advance_stage(4, source="skip_to_output")  # Was 5, now 4

    show_stage_banner(2, total_stages=4)


def render_sidebar(current_stage):
    """Render the sidebar with ONLY 4 stages. Human Review is only marked complete after download."""

    st.sidebar.markdown("## Workflow Progress")

    stages = [
        "Prompt Builder",
        "AI Processing",
        "Human Review and Editing",
        "Output"
    ]

    # Determine if Human Review is completed (tied to download action)
    human_review_complete = st.session_state.get("human_review_downloaded", False)

    for idx, label in enumerate(stages, 1):
        # Special handling for Human Review (Stage 3)
        if idx == 3:
            if current_stage == 3:
                # Currently in Human Review
                st.sidebar.markdown(
                    f"<div style='color: #1976d2; font-weight: bold;'>➡️ Stage {idx} of 4: {label} (In Progress)</div>",
                    unsafe_allow_html=True,
                )
            elif idx < current_stage:
                # Only mark as complete if download flag is set
                if human_review_complete:
                    st.sidebar.markdown(
                        f"<div style='color: #388e3c; font-weight: bold;'>✔️ Stage {idx} of 4: {label} (Completed)</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.sidebar.markdown(
                        f"<div style='color: #bdbdbd;'>Stage {idx} of 4: {label} (Not Completed)</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.sidebar.markdown(
                    f"<div style='color: #bdbdbd;'>Stage {idx} of 4: {label}</div>",
                    unsafe_allow_html=True,
                )
        else:
            # All other stages: normal logic
            if idx == current_stage:
                st.sidebar.markdown(
                    f"<div style='color: #1976d2; font-weight: bold;'>➡️ Stage {idx} of 4: {label}</div>",
                    unsafe_allow_html=True,
                )
            elif idx < current_stage:
                st.sidebar.markdown(
                    f"<div style='color: #388e3c; font-weight: bold;'>✔️ Stage {idx} of 4: {label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.sidebar.markdown(
                    f"<div style='color: #bdbdbd;'>Stage {idx} of 4: {label}</div>",
                    unsafe_allow_html=True,
                )

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Current: {stages[current_stage-1]}**")
    st.sidebar.markdown("### Manual Navigation")
    nav_options = stages
    nav_stage_map = {label: idx for idx, label in enumerate(stages, 1)}
    selected = st.sidebar.radio(
        "Jump to stage:",
        nav_options,
        index=current_stage-1,
        key="manual_nav"
    )
    if nav_stage_map[selected] != current_stage:
        NavigationManager.goto_stage(nav_stage_map[selected])

# Call this function at the top of your main render function for Stage 3:
# render_sidebar(current_stage=3)