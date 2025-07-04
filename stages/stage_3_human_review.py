# stages/stage_3_human_review.py
import streamlit as st
import json
import copy
from navigation.manager import NavigationManager

# Import Q2JSON Stage 4 components
try:
    from extracted_components.editor_framework import Q2JSONEditorFramework
    from extracted_components.latex_processor import Q2JSONLaTeXProcessor
    from extracted_components.question_renderer import Q2JSONQuestionRenderer
    from extracted_components.validation_manager import Q2JSONValidationManager
except ImportError:
    # Fallback if components not available
    st.error("Q2JSON Stage 4 components not found. Please ensure extracted_components are available.")
    Q2JSONEditorFramework = None
    Q2JSONLaTeXProcessor = None
    Q2JSONQuestionRenderer = None
    Q2JSONValidationManager = None


def render_human_review():
    """Render the complete Human Review & Editing stage"""
    
    # Progress indicator
    progress = (st.session_state.current_stage + 1) / 4
    st.progress(progress)
    st.markdown(f"**Stage {st.session_state.current_stage + 1} of 4**: Human Review & Editing")

    st.header("👥 Human Review & Editing")
    
    # Check if we have validated questions from Stage 2
    if not has_validated_questions():
        render_no_questions_warning()
        return
    
    # Skip the Q2JSON component check since we know they don't exist
    # and go directly to the working editor
    
    # Render the editor interface
    render_editor_interface()
    
    # Workflow completion
    render_workflow_completion()


def has_validated_questions():
    """Check if we have validated questions from Stage 2"""
    return ('questions_data' in st.session_state and 
            st.session_state.questions_data and
            'questions' in st.session_state.questions_data)


def components_available():
    """Check if Q2JSON Stage 4 components are available"""
    # Since we know these don't exist, always return False
    # This function is kept for compatibility but not used
    return False

def initialize_stage4_components():
    """Initialize available components (working components, not Q2JSON)"""
    
    if 'stage4_components' not in st.session_state:
        try:
            # Import working components
            from modules.json_processor import JSONProcessor
            from modules.mathematical_consistency_detector import MathematicalConsistencyDetector
            
            processor = JSONProcessor()
            math_detector = MathematicalConsistencyDetector()
            
            st.session_state.stage4_components = {
                'json_processor': processor,
                'math_detector': math_detector,
                'status': 'initialized'
            }
            
            return True
            
        except Exception as e:
            st.session_state.stage4_components = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    return st.session_state.stage4_components.get('status') == 'initialized'

def render_no_questions_warning():
    """Render warning when no validated questions are available"""
    st.warning("⚠️ No validated questions available. Please complete previous stages first.")
    st.markdown("""
    **To get started with Human Review:**
    1. Complete **Stage 1: Prompt Builder** to create your AI prompt
    2. Complete **Stage 2: AI Processing** to upload and process the AI response
    3. Complete **Stage 3: JSON Validation** to validate the questions
    4. Return here for human review and editing
    """)


def render_component_error():
    """Render error when Q2JSON components are not available"""
    # This function is kept for compatibility but not used in the main flow
    st.error("❌ Q2JSON Stage 4 Components Not Available")
    st.markdown("""
    **Missing Components:**
    - Editor Framework
    - LaTeX Processor  
    - Question Renderer
    - Validation Manager
    
    **Using fallback components instead.**
    """)


def render_editor_interface():
    """Render the main Q2JSON Stage 4 editor interface"""
    
    # Get questions from session state
    questions_data = st.session_state.get('questions_data', {})
    questions = questions_data.get('questions', [])
    
    if not questions:
        st.warning("No questions found in the validated data")
        return
    
    # Debug section - show that choices exist
    st.subheader("🔍 Debug: Question Data Verification")
    first_question = questions[0]
    choices = first_question.get('choices', [])
    st.write(f"**First question:** {first_question.get('title', 'No title')[:50]}...")
    st.write(f"**Question type:** {first_question.get('type', 'No type')}")
    st.write(f"**Choices count:** {len(choices)}")
    
    if choices:
        st.success(f"✅ Choices data is present ({len(choices)} choices)")
    else:
        st.error("❌ No choices found in question data")
    
    # Since Q2JSON components don't exist, use working components
    st.subheader("📝 Question Editor")
    
    try:
        # Import working components
        from modules.json_processor import JSONProcessor
        from modules.mathematical_consistency_detector import MathematicalConsistencyDetector
        
        processor = JSONProcessor()
        math_detector = MathematicalConsistencyDetector()
        
        st.success("✅ Using JSONProcessor and MathematicalConsistencyDetector")
        
        # Create the editor interface
        render_working_editor(questions, processor, math_detector)
        
    except ImportError as e:
        st.error(f"❌ Could not import working components: {e}")
        render_simple_fallback_editor(questions)
    except Exception as e:
        st.error(f"❌ Error with components: {e}")
        render_simple_fallback_editor(questions)

def render_working_editor(questions, processor, math_detector):
    """Render editor using working components with proper layout and view options"""
    
    st.write("Using working components for question editing")
    
    # Question navigation section
    st.subheader("🔢 Question Navigation")
    
    # Create navigation columns
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        # Previous button
        if st.button("⬅️ Previous", key="nav_previous", disabled=st.session_state.get('current_question_idx', 0) == 0):
            if 'current_question_idx' in st.session_state:
                st.session_state.current_question_idx = max(0, st.session_state.current_question_idx - 1)
            st.rerun()
    
    with nav_col2:
        # Question selector (dropdown + quick jump buttons)
        question_idx = st.selectbox(
            "Select Question to Edit",
            range(len(questions)),
            format_func=lambda x: f"Question {x + 1}: {questions[x].get('title', 'Untitled')[:40]}...",
            key="question_selector",
            index=st.session_state.get('current_question_idx', 0)
        )
        
        # Update session state
        st.session_state.current_question_idx = question_idx
        
        # Quick jump buttons - show all 10 questions
        st.write("**Quick Jump:**")
        jump_cols = st.columns(10)
        for i in range(len(questions)):
            with jump_cols[i]:
                # Fix the button type logic
                if i == question_idx:
                    button_type = "primary"
                else:
                    button_type = "secondary"
                
                if st.button(f"{i+1}", key=f"jump_{i}", type=button_type):
                    st.session_state.current_question_idx = i
                    st.rerun()
    
    with nav_col3:
        # Next button
        if st.button("Next ➡️", key="nav_next", disabled=st.session_state.get('current_question_idx', 0) == len(questions) - 1):
            if 'current_question_idx' in st.session_state:
                st.session_state.current_question_idx = min(len(questions) - 1, st.session_state.current_question_idx + 1)
            st.rerun()
    
    # Show current question info
    selected_question = questions[question_idx]
    st.info(f"📝 Currently editing: **Question {question_idx + 1}** of {len(questions)} | Type: {selected_question.get('type', 'Unknown')}")
    
    # Progress indicator
    progress_value = (question_idx + 1) / len(questions)
    st.progress(progress_value)
    st.caption(f"Question {question_idx + 1} of {len(questions)}")
    
    # View mode selector
    view_mode = st.radio(
        "Select View Mode:",
        ["👨‍🏫 Teacher View", "👨‍🎓 Student View", "🔧 Raw Data View", "📊 Analysis View"],
        horizontal=True,
        key="view_mode"
    )
    
    # Create layout based on view mode
    if view_mode == "👨‍🏫 Teacher View":
        render_teacher_view(selected_question, question_idx, questions)
    elif view_mode == "👨‍🎓 Student View":
        render_student_view(selected_question, question_idx, questions)
    elif view_mode == "🔧 Raw Data View":
        render_raw_data_view(selected_question, question_idx, questions)
    elif view_mode == "📊 Analysis View":
        render_analysis_view(selected_question, question_idx, questions)
    
    # REMOVED: Bottom navigation section
    # The bottom navigation with all question buttons has been removed
    # Only the top navigation remains for cleaner interface

def render_teacher_view(selected_question, question_idx, questions):
    """Render teacher view with editing capabilities and live preview"""
    
    # Create two-column layout: Preview on left, Editor on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"📖 Question {question_idx + 1} - Live Preview")
        
        # Add mini navigation in preview
        mini_nav_col1, mini_nav_col2, mini_nav_col3 = st.columns([1, 2, 1])
        
        with mini_nav_col1:
            if st.button("⬅️", key="mini_prev", disabled=question_idx == 0):
                st.session_state.current_question_idx = max(0, question_idx - 1)
                st.rerun()
        
        with mini_nav_col2:
            st.write(f"**Question {question_idx + 1} of {len(questions)}**")
        
        with mini_nav_col3:
            if st.button("➡️", key="mini_next", disabled=question_idx == len(questions) - 1):
                st.session_state.current_question_idx = min(len(questions) - 1, question_idx + 1)
                st.rerun()
        
        # **Show live preview with current edits**
        # Get the current edit state or fall back to saved version
        if f'edit_question_{question_idx}' in st.session_state:
            preview_question = st.session_state[f'edit_question_{question_idx}']
            st.success("📝 Live Preview - showing current edits")
        else:
            preview_question = selected_question
            st.info("💾 Saved Version - no current edits")
        
        # Display question with current edits
        st.write(f"**Title:** {preview_question.get('title', 'No title')}")
        st.write(f"**Type:** {preview_question.get('type', 'No type')}")
        st.write(f"**Difficulty:** {preview_question.get('difficulty', 'Medium')}")
        st.write(f"**Points:** {preview_question.get('points', 1)}")
        
        # Question text
        st.write("**Question:**")
        st.write(preview_question.get('question_text', 'No text'))
        
        # Show choices with correct answer highlighted
        question_type = preview_question.get('type', 'No type')
        
        if question_type == 'multiple_choice':
            choices = preview_question.get('choices', [])
            st.write("**Answer Choices:**")
            
            if choices:
                for i, choice in enumerate(choices):
                    if choice == preview_question.get('correct_answer'):
                        st.write(f"  **{i+1}. {choice}** ✅ (Correct)")
                    else:
                        st.write(f"  {i+1}. {choice}")
                st.success(f"✅ {len(choices)} choices available")
            else:
                st.error("❌ No choices found")
        
        elif question_type == 'numerical':
            st.write("**Answer Type:** Numerical")
            st.write(f"**Correct Answer:** {preview_question.get('correct_answer', 'Not specified')}")
            tolerance = preview_question.get('tolerance', 0.05)
            st.write(f"**Tolerance:** ±{tolerance}")
        
        elif question_type == 'true_false':
            st.write("**Answer Type:** True/False")
            correct_answer = preview_question.get('correct_answer', 'Not specified')
            st.write(f"**Correct Answer:** {correct_answer} ✅")
        
        # Show feedback if available
        if preview_question.get('feedback_correct') or preview_question.get('feedback_incorrect'):
            st.write("**Feedback:**")
            if preview_question.get('feedback_correct'):
                st.success(f"✅ Correct: {preview_question.get('feedback_correct')}")
            if preview_question.get('feedback_incorrect'):
                st.error(f"❌ Incorrect: {preview_question.get('feedback_incorrect')}")
        
        # Show modification status
        if f'edit_question_{question_idx}' in st.session_state:
            if st.session_state[f'edit_question_{question_idx}'] != selected_question:
                st.warning("⚠️ You have unsaved changes")
            else:
                st.success("✅ All changes saved")
        
        if question_idx in st.session_state.get('modified_questions', set()):
            st.success("✅ Question has been modified and saved")
        
        # Show last modified time
        if 'last_modified' in st.session_state:
            st.caption(f"Last modified: {st.session_state.last_modified}")
    
    with col2:
        render_question_editor(selected_question, question_idx)

def render_question_editor(selected_question, question_idx):
    """Render the question editor with live preview updates"""
    
    st.subheader(f"✏️ Edit Question {question_idx + 1}")
    
    # Create a copy of the question for editing
    if f'edit_question_{question_idx}' not in st.session_state:
        st.session_state[f'edit_question_{question_idx}'] = copy.deepcopy(selected_question)
    
    edit_question = st.session_state[f'edit_question_{question_idx}']
    
    # Question title - with live update
    new_title = st.text_input(
        "Question Title",
        value=edit_question.get('title', ''),
        key=f"title_{question_idx}",
        help="Changes appear in preview immediately"
    )
    # Update immediately for live preview
    edit_question['title'] = new_title
    
    # Question text - with live update
    new_text = st.text_area(
        "Question Text",
        value=edit_question.get('question_text', ''),
        height=100,
        key=f"text_{question_idx}",
        help="Changes appear in preview immediately"
    )
    # Update immediately for live preview
    edit_question['question_text'] = new_text
    
    # Question type - with live update
    current_type = edit_question.get('type', 'multiple_choice')
    new_type = st.selectbox(
        "Question Type",
        ["multiple_choice", "numerical", "true_false", "short_answer"],
        index=["multiple_choice", "numerical", "true_false", "short_answer"].index(current_type),
        key=f"type_{question_idx}",
        help="Changes appear in preview immediately"
    )
    # Update immediately for live preview
    edit_question['type'] = new_type
    
    # Type-specific editors
    if new_type == 'multiple_choice':
        render_multiple_choice_editor(edit_question, question_idx)
    elif new_type == 'numerical':
        render_numerical_editor(edit_question, question_idx)
    elif new_type == 'true_false':
        render_true_false_editor(edit_question, question_idx)
    else:
        render_text_editor(edit_question, question_idx)
    
    # Common fields
    render_common_fields(edit_question, question_idx)
    
    # Save and navigation section
    st.divider()
    st.subheader("💾 Save & Navigate")
    
    # Check if there are unsaved changes
    has_changes = edit_question != selected_question
    
    if has_changes:
        st.warning("⚠️ You have unsaved changes - click Save to permanently store them")
        
        # Show what changed
        with st.expander("📋 Show Changes"):
            changes_found = False
            
            if edit_question.get('title') != selected_question.get('title'):
                st.write(f"**Title changed:** '{selected_question.get('title', '')}' → '{edit_question.get('title', '')}'")
                changes_found = True
            
            if edit_question.get('question_text') != selected_question.get('question_text'):
                st.write(f"**Question text changed**")
                changes_found = True
            
            if edit_question.get('type') != selected_question.get('type'):
                st.write(f"**Type changed:** '{selected_question.get('type', '')}' → '{edit_question.get('type', '')}'")
                changes_found = True
            
            if edit_question.get('choices') != selected_question.get('choices'):
                st.write(f"**Choices changed:** {len(selected_question.get('choices', []))} → {len(edit_question.get('choices', []))} choices")
                changes_found = True
            
            if edit_question.get('correct_answer') != selected_question.get('correct_answer'):
                st.write(f"**Correct answer changed:** '{selected_question.get('correct_answer', '')}' → '{edit_question.get('correct_answer', '')}'")
                changes_found = True
            
            if not changes_found:
                st.write("No changes detected")
    else:
        st.success("✅ All changes saved")
    
    # Save and navigation buttons
    save_col1, save_col2, save_col3 = st.columns(3)
    
    with save_col1:
        if st.button(f"💾 Save & Previous", key=f"save_prev_{question_idx}", disabled=question_idx == 0):
            save_question_changes(edit_question, question_idx)
            st.session_state.current_question_idx = max(0, question_idx - 1)
            st.rerun()
    
    with save_col2:
        if st.button(f"💾 Save Question", key=f"save_{question_idx}", type="primary"):
            if save_question_changes(edit_question, question_idx):
                st.success(f"✅ Question {question_idx + 1} saved successfully!")
                st.balloons()  # Visual feedback
            st.rerun()
    
    with save_col3:
        if st.button(f"💾 Save & Next", key=f"save_next_{question_idx}", disabled=question_idx == len(st.session_state.questions_data['questions']) - 1):
            save_question_changes(edit_question, question_idx)
            st.session_state.current_question_idx = min(len(st.session_state.questions_data['questions']) - 1, question_idx + 1)
            st.rerun()
    
    # Reset and discard buttons
    reset_col1, reset_col2 = st.columns(2)
    
    with reset_col1:
        if st.button(f"🔄 Reset to Saved", key=f"reset_{question_idx}"):
            # Reset to saved version
            st.session_state[f'edit_question_{question_idx}'] = copy.deepcopy(selected_question)
            st.success("Changes reset to saved version")
            st.rerun()
    
    with reset_col2:
        if st.button(f"🗑️ Discard Changes", key=f"discard_{question_idx}"):
            # Clear the edit state
            if f'edit_question_{question_idx}' in st.session_state:
                del st.session_state[f'edit_question_{question_idx}']
            st.success("Changes discarded")
            st.rerun()
    
    # Auto-save option
    st.divider()
    auto_save = st.checkbox(
        "🔄 Auto-save changes",
        value=st.session_state.get('auto_save_enabled', False),
        key=f"auto_save_{question_idx}",
        help="Automatically save changes as you type"
    )
    
    if auto_save:
        st.session_state.auto_save_enabled = True
        # Auto-save if there are changes
        if has_changes:
            save_question_changes(edit_question, question_idx)
            st.caption("🔄 Auto-saved")
    else:
        st.session_state.auto_save_enabled = False

def render_multiple_choice_editor(edit_question, question_idx):
    """Render multiple choice editor with live preview updates"""
    
    st.subheader("📋 Answer Choices")
    
    # Initialize choices if not present
    if 'choices' not in edit_question:
        edit_question['choices'] = []
    
    current_choices = edit_question.get('choices', [])
    
    # Show current choices count
    st.write(f"**Current Choices ({len(current_choices)}):**")
    
    # Edit choices with live update
    st.write("**Edit Choices:**")
    new_choices = []
    
    # Create choice input fields
    num_fields = max(4, len(current_choices))
    
    for i in range(num_fields):
        choice_value = current_choices[i] if i < len(current_choices) else ""
        
        # Use a unique key that includes the question index
        choice_key = f"choice_{question_idx}_{i}"
        
        new_choice = st.text_input(
            f"Choice {i+1}",
            value=choice_value,
            key=choice_key,
            placeholder=f"Enter choice {i+1}...",
            help="Changes appear in preview immediately"
        )
        
        if new_choice.strip():
            new_choices.append(new_choice.strip())
    
    # Update choices immediately for live preview
    edit_question['choices'] = new_choices
    
    # Validation
    if new_choices:
        if len(new_choices) >= 2:
            st.success(f"✅ {len(new_choices)} choices defined")
        else:
            st.warning(f"⚠️ Multiple choice questions should have at least 2 choices")
    else:
        st.error("❌ No choices defined")
    
    # Correct answer selector with live update
    if new_choices:
        st.subheader("✅ Correct Answer")
        
        current_correct = edit_question.get('correct_answer', '')
        correct_idx = 0
        
        if current_correct in new_choices:
            correct_idx = new_choices.index(current_correct)
        
        new_correct = st.selectbox(
            "Select Correct Answer",
            new_choices,
            index=correct_idx,
            key=f"correct_{question_idx}",
            help="Changes appear in preview immediately"
        )
        
        # Update immediately for live preview
        edit_question['correct_answer'] = new_correct

def render_common_fields(edit_question, question_idx):
    """Render common fields with live preview updates"""
    
    st.subheader("📊 Additional Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_points = st.number_input(
            "Points",
            value=edit_question.get('points', 1),
            min_value=0,
            max_value=10,
            key=f"points_{question_idx}",
            help="Changes appear in preview immediately"
        )
        # Update immediately for live preview
        edit_question['points'] = new_points
    
    with col2:
        new_difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(edit_question.get('difficulty', 'Medium')),
            key=f"difficulty_{question_idx}",
            help="Changes appear in preview immediately"
        )
        # Update immediately for live preview
        edit_question['difficulty'] = new_difficulty
    
    # Feedback with live update
    with st.expander("📝 Feedback Settings"):
        new_feedback_correct = st.text_area(
            "Feedback for Correct Answer",
            value=edit_question.get('feedback_correct', ''),
            height=75,
            key=f"feedback_correct_{question_idx}",
            help="Changes appear in preview immediately"
        )
        
        new_feedback_incorrect = st.text_area(
            "Feedback for Incorrect Answer",
            value=edit_question.get('feedback_incorrect', ''),
            height=75,
            key=f"feedback_incorrect_{question_idx}",
            help="Changes appear in preview immediately"
        )
        
        # Update immediately for live preview
        edit_question['feedback_correct'] = new_feedback_correct
        edit_question['feedback_incorrect'] = new_feedback_incorrect

def save_question_changes(edit_question, question_idx):
    """Save changes to the question in session state"""
    
    try:
        # Update the main questions data
        st.session_state.questions_data['questions'][question_idx] = copy.deepcopy(edit_question)
        
        # Clear the edit state since changes are saved
        if f'edit_question_{question_idx}' in st.session_state:
            del st.session_state[f'edit_question_{question_idx}']
        
        # Mark as modified
        if 'modified_questions' not in st.session_state:
            st.session_state.modified_questions = set()
        st.session_state.modified_questions.add(question_idx)
        
        # Update timestamp
        import datetime
        st.session_state.last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return True
        
    except Exception as e:
        st.error(f"Error saving question: {e}")
        return False

def render_numerical_editor(edit_question, question_idx):
    """Render numerical question editor with live preview updates"""
    
    st.subheader("🔢 Numerical Answer")
    
    current_answer = edit_question.get('correct_answer', '')
    try:
        numeric_value = float(current_answer) if current_answer else 0.0
    except (ValueError, TypeError):
        numeric_value = 0.0
    
    new_correct = st.number_input(
        "Correct Answer",
        value=numeric_value,
        format="%.4f",
        key=f"correct_num_{question_idx}",
        help="Changes appear in preview immediately"
    )
    
    new_tolerance = st.number_input(
        "Tolerance (±)",
        value=edit_question.get('tolerance', 0.05),
        min_value=0.0,
        max_value=1.0,
        format="%.4f",
        key=f"tolerance_{question_idx}",
        help="Changes appear in preview immediately"
    )
    
    # Update immediately for live preview
    edit_question['correct_answer'] = str(new_correct)
    edit_question['tolerance'] = new_tolerance

def render_true_false_editor(edit_question, question_idx):
    """Render true/false question editor with live preview updates"""
    
    st.subheader("✅❌ True/False Answer")
    
    current_answer = edit_question.get('correct_answer', 'True')
    new_correct = st.selectbox(
        "Correct Answer",
        ["True", "False"],
        index=0 if current_answer == 'True' else 1,
        key=f"correct_tf_{question_idx}",
        help="Changes appear in preview immediately"
    )
    
    # Update immediately for live preview
    edit_question['correct_answer'] = new_correct

def render_text_editor(edit_question, question_idx):
    """Render text answer editor with live preview updates"""
    
    st.subheader("📝 Text Answer")
    
    new_correct = st.text_input(
        "Correct Answer",
        value=edit_question.get('correct_answer', ''),
        key=f"correct_text_{question_idx}",
        help="Changes appear in preview immediately"
    )
    
    # Update immediately for live preview
    edit_question['correct_answer'] = new_correct

def render_simple_fallback_editor(questions):
    """Simple fallback editor with two-panel layout"""
    
    st.warning("🔧 Using simple fallback editor")
    
    # Two-column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Questions")
        
        # Question selector
        question_idx = st.radio(
            "Select Question:",
            range(len(questions)),
            format_func=lambda x: f"Q{x + 1}: {questions[x].get('title', 'Untitled')[:30]}...",
            key="fallback_question_selector"
        )
        
        # Show question info
        selected_question = questions[question_idx]
        st.write(f"**Type:** {selected_question.get('type', 'No type')}")
        
        # Show choices preview
        choices = selected_question.get('choices', [])
        if choices:
            st.write(f"**Choices:** {len(choices)}")
            for i, choice in enumerate(choices[:2]):
                st.write(f"  {i+1}. {choice[:25]}...")
            if len(choices) > 2:
                st.write(f"  ... and {len(choices) - 2} more")
    
    with col2:
        st.subheader(f"👁️ View Question {question_idx + 1}")
        
        # Display question
        st.write(f"**Title:** {selected_question.get('title', 'No title')}")
        st.write(f"**Type:** {selected_question.get('type', 'No type')}")
        
        # Question text
        st.write("**Question Text:**")
        st.write(selected_question.get('question_text', 'No text'))
        
        # **CRITICAL - DISPLAY CHOICES**
        choices = selected_question.get('choices', [])
        
        st.write("**Answer Choices:**")
        
        if choices:
            for i, choice in enumerate(choices):
                # Highlight correct answer
                if choice == selected_question.get('correct_answer'):
                    st.write(f"  **{i+1}. {choice}** ✅")
                else:
                    st.write(f"  {i+1}. {choice}")
            st.success(f"✅ {len(choices)} choices displayed successfully!")
        else:
            st.error("❌ No choices found")
        
        # Correct answer
        st.write(f"**Correct Answer:** {selected_question.get('correct_answer', 'Not specified')}")
        
        # Additional info
        st.write(f"**Points:** {selected_question.get('points', 'Not specified')}")
        st.write(f"**Difficulty:** {selected_question.get('difficulty', 'Not specified')}")
        
        # Raw JSON
        with st.expander("🔍 Raw Question Data"):
            st.json(selected_question)

def render_student_view(selected_question, question_idx, questions):
    """Render student view - how the question appears to students"""
    
    # Create two-column layout: Student view on left, Quick edit on right
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"👨‍🎓 Student View - Question {question_idx + 1}")
        
        # Simulate student interface
        st.markdown("---")
        
        # Question title (if shown to students)
        if selected_question.get('title'):
            st.write(f"**{selected_question.get('title')}**")
        
        # Question text
        st.write(selected_question.get('question_text', 'No question text'))
        
        # Answer interface based on type
        question_type = selected_question.get('type', 'No type')
        
        if question_type == 'multiple_choice':
            choices = selected_question.get('choices', [])
            if choices:
                st.write("**Select your answer:**")
                # Simulate radio button selection
                student_answer = st.radio(
                    "Choose one:",
                    choices,
                    key=f"student_answer_{question_idx}",
                    label_visibility="collapsed"
                )
                
                # Show if answer is correct (for preview)
                if student_answer == selected_question.get('correct_answer'):
                    st.success("✅ This would be correct!")
                else:
                    st.error("❌ This would be incorrect")
            else:
                st.error("No choices available")
        
        elif question_type == 'numerical':
            st.write("**Enter your numerical answer:**")
            student_numerical = st.number_input(
                "Answer:",
                key=f"student_numerical_{question_idx}",
                format="%.4f"
            )
            
            # Check if within tolerance
            try:
                correct_value = float(selected_question.get('correct_answer', 0))
                tolerance = selected_question.get('tolerance', 0.05)
                if abs(student_numerical - correct_value) <= tolerance:
                    st.success(f"✅ Within tolerance of {correct_value}")
                else:
                    st.error(f"❌ Outside tolerance of {correct_value} ± {tolerance}")
            except:
                st.warning("Cannot validate - check correct answer format")
        
        elif question_type == 'true_false':
            st.write("**Select True or False:**")
            student_tf = st.radio(
                "Your answer:",
                ["True", "False"],
                key=f"student_tf_{question_idx}"
            )
            
            if student_tf == selected_question.get('correct_answer'):
                st.success("✅ This would be correct!")
            else:
                st.error("❌ This would be incorrect")
        
        else:
            st.write("**Enter your answer:**")
            student_text = st.text_input(
                "Answer:",
                key=f"student_text_{question_idx}"
            )
        
        st.markdown("---")
        st.caption(f"Points: {selected_question.get('points', 1)} | Difficulty: {selected_question.get('difficulty', 'Medium')}")
    
    with col2:
        st.subheader("🔧 Quick Edit")
        
        # Quick editing options
        quick_edit_title = st.text_input(
            "Title:",
            value=selected_question.get('title', ''),
            key=f"quick_title_{question_idx}"
        )
        
        quick_edit_type = st.selectbox(
            "Type:",
            ["multiple_choice", "numerical", "true_false", "short_answer"],
            index=["multiple_choice", "numerical", "true_false", "short_answer"].index(
                selected_question.get('type', 'multiple_choice')
            ),
            key=f"quick_type_{question_idx}"
        )
        
        quick_edit_points = st.number_input(
            "Points:",
            value=selected_question.get('points', 1),
            min_value=0,
            max_value=10,
            key=f"quick_points_{question_idx}"
        )
        
        if st.button("🔄 Switch to Teacher View", key=f"switch_teacher_{question_idx}"):
            st.session_state.view_mode = "👨‍🏫 Teacher View"
            st.rerun()
        
        if st.button("📝 Full Edit Mode", key=f"full_edit_{question_idx}"):
            st.session_state.view_mode = "👨‍🏫 Teacher View"
            st.rerun()

def render_raw_data_view(selected_question, question_idx, questions):
    """Render raw data view for debugging"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"🔧 Raw Data - Question {question_idx + 1}")
        
        # Show complete JSON structure
        st.json(selected_question)
    
    with col2:
        st.subheader("📊 Data Analysis")
        
        # Analyze question structure
        st.write("**Field Analysis:**")
        
        required_fields = ['title', 'question_text', 'type', 'correct_answer']
        optional_fields = ['choices', 'points', 'difficulty', 'feedback_correct', 'feedback_incorrect', 'tolerance']
        
        st.write("**Required Fields:**")
        for field in required_fields:
            if field in selected_question and selected_question[field]:
                st.write(f"  ✅ {field}: Present")
            else:
                st.write(f"  ❌ {field}: Missing")
        
        st.write("**Optional Fields:**")
        for field in optional_fields:
            if field in selected_question and selected_question[field]:
                st.write(f"  ✅ {field}: Present")
            else:
                st.write(f"  ⚪ {field}: Not set")
        
        # Type-specific validation
        question_type = selected_question.get('type', 'No type')
        
        if question_type == 'multiple_choice':
            choices = selected_question.get('choices', [])
            correct_answer = selected_question.get('correct_answer', '')
            
            st.write("**Multiple Choice Validation:**")
            st.write(f"  Choices count: {len(choices)}")
            st.write(f"  Correct answer in choices: {correct_answer in choices}")
            
            if len(choices) < 2:
                st.error("❌ Multiple choice needs at least 2 choices")
            if correct_answer not in choices:
                st.error("❌ Correct answer not in choices list")

def render_analysis_view(selected_question, question_idx, questions):
    """Render analysis view with statistics and insights"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"📊 Question Analysis - Question {question_idx + 1}")
        
        # Question statistics
        st.write("**Question Statistics:**")
        
        question_text = selected_question.get('question_text', '')
        st.write(f"Text length: {len(question_text)} characters")
        st.write(f"Word count: {len(question_text.split()) if question_text else 0}")
        
        # Type distribution
        question_type = selected_question.get('type', 'No type')
        st.write(f"Question type: {question_type}")
        
        # Difficulty analysis
        difficulty = selected_question.get('difficulty', 'Medium')
        st.write(f"Difficulty level: {difficulty}")
        
        # Points analysis
        points = selected_question.get('points', 1)
        st.write(f"Point value: {points}")
        
        # Choice analysis for multiple choice
        if question_type == 'multiple_choice':
            choices = selected_question.get('choices', [])
            st.write(f"Number of choices: {len(choices)}")
            
            if choices:
                avg_choice_length = sum(len(choice) for choice in choices) / len(choices)
                st.write(f"Average choice length: {avg_choice_length:.1f} characters")
    
    with col2:
        st.subheader("📈 Dataset Overview")
        
        # Analyze all questions
        total_questions = len(questions)
        st.write(f"**Total Questions:** {total_questions}")
        
        # Type distribution
        type_counts = {}
        difficulty_counts = {}
        total_points = 0
        
        for q in questions:
            q_type = q.get('type', 'unknown')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
            
            difficulty = q.get('difficulty', 'Medium')
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            
            total_points += q.get('points', 1)
        
        st.write("**Question Types:**")
        for q_type, count in type_counts.items():
            percentage = (count / total_questions) * 100
            st.write(f"  {q_type}: {count} ({percentage:.1f}%)")
        
        st.write("**Difficulty Distribution:**")
        for difficulty, count in difficulty_counts.items():
            percentage = (count / total_questions) * 100
            st.write(f"  {difficulty}: {count} ({percentage:.1f}%)")
        
        st.write(f"**Total Points:** {total_points}")
        st.write(f"**Average Points per Question:** {total_points / total_questions:.1f}")

def render_workflow_completion():
    """Render the workflow completion section"""
    
    st.subheader("🎯 Workflow Completion")
    
    # Check if we have questions to work with
    questions_data = st.session_state.get('questions_data', {})
    questions = questions_data.get('questions', [])
    
    if not questions:
        st.warning("No questions available for completion")
        return
    
    # Show summary
    st.write(f"**Total Questions:** {len(questions)}")
    
    # Check question completeness
    complete_questions = 0
    for question in questions:
        if (question.get('title') and 
            question.get('question_text') and 
            question.get('type') and
            question.get('correct_answer')):
            
            # For multiple choice, also check choices
            if question.get('type') == 'multiple_choice':
                if question.get('choices') and len(question.get('choices', [])) > 0:
                    complete_questions += 1
            else:
                complete_questions += 1
    
    st.write(f"**Complete Questions:** {complete_questions}/{len(questions)}")
    
    # Progress bar
    completion_progress = complete_questions / len(questions) if questions else 0
    st.progress(completion_progress)
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Stage 2", key="back_to_stage2"):
            st.session_state.current_stage = 1
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Editor", key="refresh_editor"):
            st.rerun()
    
    with col3:
        if complete_questions == len(questions):
            if st.button("✅ Complete Stage 3", key="complete_stage3"):
                st.session_state.current_stage = 3  # Move to Stage 4
                st.success("Stage 3 completed! Moving to Stage 4...")
                st.rerun()
        else:
            st.button("⏳ Complete All Questions", disabled=True, key="complete_disabled")
            st.caption(f"Complete {len(questions) - complete_questions} more questions to proceed")
    
    # Export options
    st.subheader("📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Export JSON", key="export_json"):
            # Create download button for JSON
            json_str = json.dumps(questions_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download JSON File",
                data=json_str,
                file_name="edited_questions.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Export Summary", key="export_summary"):
            # Create summary report
            summary = create_question_summary(questions)
            st.download_button(
                label="Download Summary Report",
                data=summary,
                file_name="question_summary.txt",
                mime="text/plain"
            )

def create_question_summary(questions):
    """Create a text summary of all questions"""
    
    summary_lines = []
    summary_lines.append("QUESTION SUMMARY REPORT")
    summary_lines.append("=" * 50)
    summary_lines.append(f"Generated: {st.session_state.get('timestamp', 'Unknown')}")
    summary_lines.append(f"Total Questions: {len(questions)}")
    summary_lines.append("")
    
    for i, question in enumerate(questions):
        summary_lines.append(f"QUESTION {i+1}")
        summary_lines.append("-" * 20)
        summary_lines.append(f"Title: {question.get('title', 'No title')}")
        summary_lines.append(f"Type: {question.get('type', 'No type')}")
        summary_lines.append(f"Text: {question.get('question_text', 'No text')[:100]}...")
        
        # Add choices for multiple choice
        if question.get('type') == 'multiple_choice':
            choices = question.get('choices', [])
            summary_lines.append(f"Choices ({len(choices)}):")
            for j, choice in enumerate(choices):
                summary_lines.append(f"  {j+1}. {choice}")
        
        summary_lines.append(f"Correct Answer: {question.get('correct_answer', 'Not specified')}")
        summary_lines.append(f"Points: {question.get('points', 'Not specified')}")
        summary_lines.append(f"Difficulty: {question.get('difficulty', 'Not specified')}")
        summary_lines.append("")
    
    return "\n".join(summary_lines)
