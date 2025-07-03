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
    
    # Check if Q2JSON components are available
    if not components_available():
        render_component_error()
        return
    
    # Initialize Stage 4 components if not already done
    initialize_stage4_components()
    
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
    return all([
        Q2JSONEditorFramework is not None,
        Q2JSONLaTeXProcessor is not None,
        Q2JSONQuestionRenderer is not None,
        Q2JSONValidationManager is not None
    ])


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
    st.error("❌ Q2JSON Stage 4 Components Not Available")
    st.markdown("""
    **Missing Components:**
    - Editor Framework
    - LaTeX Processor  
    - Question Renderer
    - Validation Manager
    
    **To fix this:**
    1. Ensure the `extracted_components/` directory exists
    2. Verify all component files are present
    3. Check import paths in the application
    """)


def initialize_stage4_components():
    """Initialize Q2JSON Stage 4 components in session state"""
    if 'stage4_components' not in st.session_state:
        try:
            # Initialize LaTeX processor
            latex_processor = Q2JSONLaTeXProcessor()
            
            # Initialize question renderer
            question_renderer = Q2JSONQuestionRenderer(latex_processor)
            
            # Initialize validation manager
            validation_manager = Q2JSONValidationManager(latex_processor)
            
            # Initialize editor framework
            editor_framework = Q2JSONEditorFramework(
                latex_processor=latex_processor,
                question_renderer=question_renderer,
                validation_manager=validation_manager
            )
            
            # Store in session state
            st.session_state.stage4_components = {
                'latex_processor': latex_processor,
                'question_renderer': question_renderer,
                'validation_manager': validation_manager,
                'editor_framework': editor_framework
            }
            
        except Exception as e:
            st.error(f"Failed to initialize Stage 4 components: {str(e)}")
            st.session_state.stage4_components = None


def render_editor_interface():
    """Render the main Q2JSON Stage 4 editor interface"""
    components = st.session_state.get('stage4_components')
    
    if not components:
        st.error("Failed to initialize editor components")
        return
    
    st.subheader("✏️ Question Editor")
    
    # Get questions from Stage 2
    questions_data = st.session_state.questions_data
    questions = questions_data.get('questions', [])
    
    if not questions:
        st.warning("No questions found in the validated data")
        return
    
    # Show summary
    render_questions_summary(questions)
    
    # Use Q2JSON editor framework
    try:
        editor_framework = components['editor_framework']
        
        # Create editor interface
        updated_questions = editor_framework.create_editor_interface(
            questions=questions,
            title="",  # No title since we have our own header
            allow_batch_ops=True
        )
        
        # Update session state with edited questions
        if updated_questions != questions:
            st.session_state.edited_questions_data = {
                'questions': updated_questions,
                'metadata': questions_data.get('metadata', {}),
                'edited_timestamp': st.session_state.navigation_timestamp,
                'review_completed': True
            }
            st.session_state.review_completed = True
        
    except Exception as e:
        st.error(f"Editor error: {str(e)}")
        render_fallback_editor(questions)


def render_questions_summary(questions):
    """Render questions summary for Stage 3"""
    st.markdown("### 📊 Questions Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", len(questions))
    
    with col2:
        question_types = [q.get('type', 'unknown') for q in questions]
        unique_types = len(set(question_types))
        st.metric("Question Types", unique_types)
    
    with col3:
        has_math = sum(1 for q in questions 
                      if any('$' in str(q.get(field, '')) 
                            for field in ['question_text', 'options', 'feedback_correct']))
        st.metric("With Math", has_math)
    
    with col4:
        # Quick validation check
        components = st.session_state.get('stage4_components')
        if components:
            validation_manager = components['validation_manager']
            total_issues = 0
            for question in questions:
                result = validation_manager.validate_question(question)
                total_issues += len(result.issues)
            st.metric("Validation Issues", total_issues)
        else:
            st.metric("Validation", "N/A")


def render_fallback_editor(questions):
    """Render a simple fallback editor if Stage 4 components fail"""
    st.warning("🔧 Using fallback editor due to component issues")
    
    # Simple question selector and JSON editor
    if questions:
        question_idx = st.selectbox(
            "Select Question to Edit",
            range(len(questions)),
            format_func=lambda x: f"Question {x + 1}: {questions[x].get('title', 'Untitled')[:50]}..."
        )
        
        # JSON editor
        st.subheader(f"Edit Question {question_idx + 1}")
        
        current_question = questions[question_idx]
        json_str = json.dumps(current_question, indent=2)
        
        edited_json = st.text_area(
            "Question JSON",
            value=json_str,
            height=400,
            help="Edit the question as JSON. Be careful with syntax!"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Validate JSON"):
                try:
                    parsed_question = json.loads(edited_json)
                    st.success("✅ Valid JSON structure")
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")
        
        with col2:
            if st.button("Update Question"):
                try:
                    parsed_question = json.loads(edited_json)
                    questions[question_idx] = parsed_question
                    
                    # Update session state
                    st.session_state.edited_questions_data = {
                        'questions': questions,
                        'metadata': st.session_state.questions_data.get('metadata', {}),
                        'edited_timestamp': st.session_state.navigation_timestamp,
                        'review_completed': True
                    }
                    st.session_state.review_completed = True
                    
                    st.success("✅ Question updated")
                    st.rerun()
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Cannot update: Invalid JSON: {str(e)}")


def render_workflow_completion():
    """Render workflow completion options"""
    st.markdown("---")
    st.subheader("🎯 Review Complete")
    
    # Show review status
    if st.session_state.get('review_completed', False):
        st.success("✅ Questions have been reviewed and edited")
        
        # Export options
        render_export_options()
    else:
        st.info("📝 Make edits above to complete the review process")
    
    # Navigation options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        NavigationManager.create_navigation_selector(
            target_stage=2,
            label="⬅️ Back to Validation"
        )
    
    with col2:
        if st.session_state.get('review_completed', False):
            st.success("🎉 Review Complete!")
        else:
            st.info("🔄 Continue Editing")
    
    with col3:
        NavigationManager.create_navigation_selector(
            target_stage=0,
            label="🔄 Start New Project"
        )


def render_export_options():
    """Render export options for reviewed questions"""
    st.markdown("### 📤 Export Reviewed Questions")
    
    edited_data = st.session_state.get('edited_questions_data')
    if not edited_data:
        return
    
    export_filename = st.text_input(
        "Export filename:",
        value="reviewed_questions",
        help="Enter filename without .json extension"
    )
    
    if export_filename and export_filename.strip():
        # Clean filename
        clean_filename = "".join(c for c in export_filename.strip() 
                               if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not clean_filename:
            clean_filename = "reviewed_questions"
        
        final_filename = f"{clean_filename}.json"
        
        # Generate export data
        export_data = {
            'questions': edited_data['questions'],
            'metadata': {
                **edited_data.get('metadata', {}),
                'reviewed': True,
                'review_timestamp': edited_data.get('edited_timestamp'),
                'stage4_processing': True,
                'export_timestamp': st.session_state.navigation_timestamp
            }
        }
        
        json_string = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Download button
        st.download_button(
            "📥 Download Reviewed Questions",
            json_string,
            file_name=final_filename,
            mime="application/json",
            use_container_width=True,
            type="primary"
        )
        
        questions_count = len(edited_data['questions'])
        st.success(f"✅ Ready to download {questions_count} reviewed questions as {final_filename}!")
    else:
        st.warning("⚠️ Please enter a filename to enable download")
