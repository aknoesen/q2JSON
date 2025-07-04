# stages/stage_3_components/editor_interface.py
import streamlit as st
from .question_editor import QuestionEditor
from .view_renderers import ViewRenderers
from .debug_utils import DebugUtils

class EditorInterface:
    """Main editor interface coordinator"""
    
    def __init__(self):
        self.question_editor = QuestionEditor()
        self.view_renderers = ViewRenderers()
        self.debug_utils = DebugUtils()
    
    def render(self):
        """Render the complete editor interface"""
        
        questions_data = st.session_state.get('questions_data', {})
        questions = questions_data.get('questions', [])
        
        if not questions:
            st.warning("No questions found in the validated data")
            return
        
        # Debug verification
        self._render_debug_verification(questions)
        
        # Main editor
        st.subheader("📝 Question Editor")
        self._render_navigation(questions)
        self._render_view_modes(questions)
    
    def _render_debug_verification(self, questions):
        """Render debug verification section"""
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
    
    def _render_navigation(self, questions):
        """Render question navigation"""
        
        # Initialize current question index
        if 'current_question_idx' not in st.session_state:
            st.session_state.current_question_idx = 0
        
        # Question navigation section
        st.subheader("🔢 Question Navigation")
        
        # Current question info
        current_idx = st.session_state.current_question_idx
        total_questions = len(questions)
        
        # Navigation columns
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 2, 1, 1])
        
        with nav_col1:
            if st.button("⬅️ Previous", disabled=current_idx == 0):
                st.session_state.current_question_idx = max(0, current_idx - 1)
                st.rerun()
        
        with nav_col2:
            # Question selector
            question_options = []
            for i, q in enumerate(questions):
                title = q.get('title', f'Question {i+1}')
                status = "🟢" if i in st.session_state.get('modified_questions', set()) else "⚪"
                question_options.append(f"{status} Q{i+1}: {title[:30]}...")
            
            selected_idx = st.selectbox(
                "Select Question",
                range(len(question_options)),
                index=current_idx,
                format_func=lambda x: question_options[x],
                key="question_selector"
            )
            
            if selected_idx != current_idx:
                st.session_state.current_question_idx = selected_idx
                st.rerun()
        
        with nav_col3:
            if st.button("➡️ Next", disabled=current_idx == total_questions - 1):
                st.session_state.current_question_idx = min(total_questions - 1, current_idx + 1)
                st.rerun()
        
        with nav_col4:
            st.write(f"**{current_idx + 1}/{total_questions}**")
    
    def _render_view_modes(self, questions):
        """Render different view modes"""
        
        # View mode selection
        st.subheader("👁️ View Mode")
        
        view_options = [
            "📚 Teacher View (Edit + Preview)",
            "🎓 Student View",
            "🔍 Raw Data View",
            "📊 Analysis View"
        ]
        
        selected_view = st.selectbox(
            "Choose View Mode",
            view_options,
            index=0,
            key="view_mode_selector"
        )
        
        # Get current question
        current_idx = st.session_state.current_question_idx
        selected_question = questions[current_idx]
        
        # Render based on selected view
        if selected_view.startswith("📚"):
            self.view_renderers.render_teacher_view(selected_question, current_idx, questions)
        elif selected_view.startswith("🎓"):
            self.view_renderers.render_student_view(selected_question, current_idx, questions)
        elif selected_view.startswith("🔍"):
            self.view_renderers.render_raw_data_view(selected_question, current_idx, questions)
        elif selected_view.startswith("📊"):
            self.view_renderers.render_analysis_view(selected_question, current_idx, questions)