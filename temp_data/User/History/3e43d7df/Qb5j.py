# stages/stage_2_validation.py
import streamlit as st
from modules.json_processor import JSONProcessor
from navigation.manager import NavigationManager
from utils.ui_helpers import show_stage_banner

def render_json_validation():
    """Render the complete JSON Validation & Export stage"""
    # Change all "of 5" to "of 4"
    st.caption(f"Stage 3 of 4")

    # Change total_stages=5 to total_stages=4
    show_stage_banner(3, total_stages=4)

    st.header("✅ Validate and Autocorrect")
    
    # Check if we have raw JSON from Stage 2
    if not has_raw_json():
        render_no_json_warning()
        return
    
    # Process and validate JSON
    success, questions_data = process_and_validate_json()
    
    if success and questions_data:
        render_validation_success(questions_data)
    
    # Workflow completion
    render_workflow_completion()


def has_raw_json():
    """Check if we have raw JSON from previous stage"""
    return ('raw_extracted_json' in st.session_state and 
            st.session_state.raw_extracted_json)


def render_no_json_warning():
    """Render warning when no JSON is available"""
    st.warning("⚠️ No extracted JSON available. Please complete Stage 2 first.")
    st.markdown("""
    **To get started:**
    1. Go to **Prompt Builder** to create your AI prompt
    2. Use the prompt with your chosen AI
    3. Return to **AI Processing** to upload the response
    4. Come back here for validation and export
    """)


def process_and_validate_json():
    """Process and validate the raw JSON"""
    raw_json = st.session_state.raw_extracted_json
    
    st.subheader("📋 Extracted JSON Preview")
    preview_text = raw_json[:500] + "..." if len(raw_json) > 500 else raw_json
    st.code(preview_text, language="json")
    
    # Process with JSONProcessor
    processor = JSONProcessor()
    st.write("🔍 Processing JSON with enhanced auto-repair...")
    
    success, questions_data, messages = processor.process_raw_json(raw_json, "chatgpt")
    
    # Display processing messages
    display_processing_messages(messages)
    
    if success and questions_data:
        st.session_state.questions_data = questions_data
    
    return success, questions_data


def display_processing_messages(messages):
    """Display processing messages with appropriate styling"""
    for message in messages:
        if "✅" in message:
            st.success(message)
        elif "❌" in message:
            st.error(message)
        elif "🔧" in message:
            st.info(message)
        else:
            st.write(message)


def render_validation_success(questions_data):
    """Render validation success UI"""
    questions = questions_data['questions']
    
    # Show summary
    render_questions_summary(questions)
    
    # Show sample question
    render_sample_question(questions)
    
    # Export section
    render_export_section(questions_data)


def render_questions_summary(questions):
    """Render questions summary metrics"""
    st.subheader("📊 Questions Summary")
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


def render_sample_question(questions):
    """Render sample question display"""
    if questions:
        st.subheader("📝 Sample Question")
        st.json(questions[0])


def render_export_section(questions_data):
    """Render export functionality"""
    st.subheader("📤 Export Your Questions")

    export_filename = st.text_input(
        "Enter filename for your questions:",
        value="my_antenna_questions",
        help="Enter filename without .json extension"
    )

    if export_filename and export_filename.strip():
        render_export_download(export_filename, questions_data)
    else:
        st.warning("⚠️ Please enter a filename above to enable download")


def render_export_download(export_filename, questions_data):
    """Render download functionality"""
    # Clean the filename
    clean_filename = "".join(c for c in export_filename.strip() 
                           if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if not clean_filename:
        clean_filename = "questions"
    
    final_filename = f"{clean_filename}.json"
    
    # Show preview
    st.info(f"📁 Will save as: **{final_filename}**")
    
    # Generate JSON string
    processor = JSONProcessor()
    json_string = processor.export_json(questions_data)
    
    # Download button
    st.download_button(
        "📥 Download Questions File",
        json_string,
        file_name=final_filename,
        mime="application/json",
        use_container_width=True,
        type="primary"
    )
    
    questions = questions_data['questions']
    st.success(f"✅ Ready to download {len(questions)} questions as {final_filename}!")


def render_workflow_completion():
    """Render workflow completion options"""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        NavigationManager.create_navigation_selector(
            target_stage=3,
            label="➡️ Human Review and Editing"
        )
    with col2:
        NavigationManager.create_navigation_selector(
            target_stage=4,
            label="➡️ Output"
        )
    with col3:
        st.success("🎉 Validation Complete!")

    # Auto-advance to Stage 3 after validation complete
    # Ensure questions_data is in session state before advancing
    if 'questions_data' in st.session_state and st.session_state.questions_data:
        NavigationManager.advance_stage(3, source="auto-advance-validation")