# extracted_components/editor_framework.py
"""
Q2JSON Editor Framework
Extracted and enhanced from Q2LMS side-by-side editing components

Provides sophisticated question editing with live preview and mathematical validation.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
from .question_renderer import Q2JSONQuestionRenderer
from .latex_processor import Q2JSONLaTeXProcessor


class Q2JSONEditorFramework:
    """
    Enhanced editor framework combining Q2LMS editing patterns with Q2JSON validation.
    
    Extracted from:
    - Q2LMS interface_delete_questions._render_question_edit_form()
    - Q2LMS question_editor.side_by_side_question_editor()
    
    Enhanced with:
    - Real-time mathematical validation
    - Q2JSON-specific validation rules
    - Enhanced user feedback and guidance
    """
    
    def __init__(self, save_callback: Optional[Callable] = None):
        self.question_renderer = Q2JSONQuestionRenderer()
        self.latex_processor = Q2JSONLaTeXProcessor()
        self.save_callback = save_callback or self._default_save_callback
        
        # Question type configurations
        self.question_types = {
            'multiple_choice': {
                'display_name': 'Multiple Choice',
                'fields': ['question_text', 'choice_a', 'choice_b', 'choice_c', 'choice_d', 'correct_answer'],
                'renderer': self._render_multiple_choice_editor
            },
            'numerical': {
                'display_name': 'Numerical',
                'fields': ['question_text', 'correct_answer', 'tolerance'],
                'renderer': self._render_numerical_editor
            },
            'true_false': {
                'display_name': 'True/False',
                'fields': ['question_text', 'correct_answer'],
                'renderer': self._render_true_false_editor
            },
            'fill_in_blank': {
                'display_name': 'Fill in Blank',
                'fields': ['question_text', 'correct_answer'],
                'renderer': self._render_fill_blank_editor
            }
        }
    
    def render_side_by_side_editor(self, 
                                 question_data: Dict[str, Any], 
                                 question_index: int,
                                 session_prefix: str = "q2json_edit",
                                 show_validation: bool = True) -> Dict[str, Any]:
        """
        Render side-by-side question editor with live preview.
        
        Args:
            question_data: Question data to edit
            question_index: Question index for session state
            session_prefix: Prefix for session state keys
            show_validation: Whether to show validation indicators
            
        Returns:
            Dict with current question data and validation results
        """
        try:
            # Initialize session state
            self._initialize_session_state(question_data, question_index, session_prefix)
            
            # Get current values from session state
            current_data = self._get_current_edit_values(question_index, session_prefix)
            
            # Validate current data
            validation_results = None
            if show_validation:
                validation_results = self._validate_question_data(current_data)
            
            # Side-by-side layout (extracted from Q2LMS pattern)
            col_preview, col_edit = st.columns([1, 1])
            
            with col_preview:
                st.markdown("#### 👁️ Live Preview")
                if validation_results and validation_results.get('status') == 'critical':
                    st.warning("⚠️ Mathematical issues detected - preview may not render correctly")
                
                # Render live preview with validation
                self.question_renderer.render_question_with_validation(
                    current_data, 
                    validation_results, 
                    show_validation_indicators=show_validation
                )
            
            with col_edit:
                st.markdown("#### ✏️ Edit Question")
                if show_validation and validation_results:
                    self._render_validation_status_indicator(validation_results)
                
                # Render edit form
                self._render_edit_form(current_data, question_index, session_prefix)
            
            # Show save controls
            if self._render_save_controls(question_index, session_prefix, validation_results):
                # Save was triggered
                saved_data = self._get_current_edit_values(question_index, session_prefix)
                return {
                    'question_data': saved_data,
                    'validation_results': validation_results,
                    'saved': True
                }
            
            return {
                'question_data': current_data,
                'validation_results': validation_results,
                'saved': False
            }
            
        except Exception as e:
            st.error(f"❌ Error in editor framework: {e}")
            with st.expander("🔍 Error Details"):
                st.exception(e)
            return {'error': str(e)}
    
    def render_compact_editor(self, 
                            question_data: Dict[str, Any], 
                            question_index: int,
                            session_prefix: str = "q2json_compact") -> Dict[str, Any]:
        """
        Render compact editor for quick edits (extracted from Q2LMS delete interface pattern).
        
        Args:
            question_data: Question data to edit
            question_index: Question index for session state
            session_prefix: Prefix for session state keys
            
        Returns:
            Dict with current question data and save status
        """
        try:
            # Initialize session state
            self._initialize_session_state(question_data, question_index, session_prefix)
            
            # Compact form layout
            st.markdown("**Quick Edit:**")
            
            # Title and question text
            title_key = f"{session_prefix}_title_{question_index}"
            question_text_key = f"{session_prefix}_question_text_{question_index}"
            
            title = st.text_input("Title", key=title_key, help="Brief descriptive title")
            question_text = st.text_area("Question Text", key=question_text_key, height=80, 
                                       help="Use $...$ for mathematical expressions")
            
            # Quick validation for question text
            if question_text:
                _, text_validation = self.latex_processor.render_latex_with_validation(question_text)
                if text_validation.get('status') == 'critical':
                    st.error("🚨 Critical mathematical issues detected in question text")
                elif text_validation.get('status') == 'warning':
                    st.warning("⚠️ Mathematical warnings in question text")
            
            # Type and points
            col_type, col_points = st.columns(2)
            with col_type:
                type_key = f"{session_prefix}_type_{question_index}"
                question_type = st.selectbox(
                    "Type", 
                    list(self.question_types.keys()),
                    format_func=lambda x: self.question_types[x]['display_name'],
                    key=type_key
                )
            
            with col_points:
                points_key = f"{session_prefix}_points_{question_index}"
                points = st.number_input("Points", min_value=0.1, key=points_key, step=0.1)
            
            # Quick save button
            if st.button(f"💾 Save Changes", key=f"{session_prefix}_save_{question_index}", 
                        type="primary"):
                current_data = self._get_current_edit_values(question_index, session_prefix)
                save_result = self.save_callback(question_index, current_data)
                
                if save_result:
                    st.success("✅ Changes saved successfully!")
                    return {'question_data': current_data, 'saved': True}
                else:
                    st.error("❌ Failed to save changes")
                    return {'question_data': current_data, 'saved': False}
            
            # Return current state
            current_data = self._get_current_edit_values(question_index, session_prefix)
            return {'question_data': current_data, 'saved': False}
            
        except Exception as e:
            st.error(f"❌ Error in compact editor: {e}")
            return {'error': str(e)}
    
    def _initialize_session_state(self, question_data: Dict[str, Any], question_index: int, session_prefix: str) -> None:
        """Initialize session state with question data"""
        # Common fields
        common_keys = ['title', 'question_text', 'type', 'points', 'difficulty', 'topic', 'subtopic']
        
        for key in common_keys:
            session_key = f"{session_prefix}_{key}_{question_index}"
            if session_key not in st.session_state:
                # Try different possible field names
                value = (question_data.get(key) or 
                        question_data.get(key.title()) or
                        question_data.get(f"question_{key}") or
                        self._get_default_value(key))
                st.session_state[session_key] = value
        
        # Question-type specific fields
        question_type = question_data.get('type', question_data.get('question_type', 'multiple_choice'))
        if question_type in self.question_types:
            for field in self.question_types[question_type]['fields']:
                session_key = f"{session_prefix}_{field}_{question_index}"
                if session_key not in st.session_state:
                    value = question_data.get(field, self._get_default_value(field))
                    st.session_state[session_key] = value
    
    def _get_current_edit_values(self, question_index: int, session_prefix: str) -> Dict[str, Any]:
        """Get current values from session state"""
        current_data = {}
        
        # Extract all session state values for this question
        for key, value in st.session_state.items():
            if key.startswith(f"{session_prefix}_") and key.endswith(f"_{question_index}"):
                field_name = key[len(session_prefix)+1:-len(str(question_index))-1]
                current_data[field_name] = value
        
        return current_data
    
    def _render_edit_form(self, question_data: Dict[str, Any], question_index: int, session_prefix: str) -> None:
        """Render the main edit form"""
        # Basic metadata
        self._render_basic_metadata_form(question_index, session_prefix)
        
        st.markdown("---")
        
        # Question text with validation
        self._render_question_text_form(question_index, session_prefix)
        
        st.markdown("---")
        
        # Question type specific fields
        question_type = st.session_state.get(f"{session_prefix}_type_{question_index}", 'multiple_choice')
        if question_type in self.question_types:
            self.question_types[question_type]['renderer'](question_index, session_prefix)
        
        st.markdown("---")
        
        # Feedback fields
        self._render_feedback_form(question_index, session_prefix)
    
    def _render_basic_metadata_form(self, question_index: int, session_prefix: str) -> None:
        """Render basic metadata form fields"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Title", 
                key=f"{session_prefix}_title_{question_index}",
                help="Brief descriptive title for the question"
            )
        
        with col2:
            st.selectbox(
                "Question Type",
                list(self.question_types.keys()),
                format_func=lambda x: self.question_types[x]['display_name'],
                key=f"{session_prefix}_type_{question_index}"
            )
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.number_input(
                "Points", 
                min_value=0.1, 
                step=0.1,
                key=f"{session_prefix}_points_{question_index}"
            )
        
        with col4:
            st.selectbox(
                "Difficulty",
                ['Easy', 'Medium', 'Hard'],
                key=f"{session_prefix}_difficulty_{question_index}"
            )
        
        with col5:
            st.text_input(
                "Topic",
                key=f"{session_prefix}_topic_{question_index}",
                help="Main topic or subject area"
            )
    
    def _render_question_text_form(self, question_index: int, session_prefix: str) -> None:
        """Render question text form with validation"""
        st.markdown("**Question Text:**")
        
        question_text = st.text_area(
            "Question Text", 
            key=f"{session_prefix}_question_text_{question_index}",
            height=120,
            help="Enter your question. Use $...$ for mathematical expressions.",
            label_visibility="collapsed"
        )
        
        # Real-time validation for question text
        if question_text:
            _, validation = self.latex_processor.render_latex_with_validation(question_text)
            if validation.get('status') == 'critical':
                st.error("🚨 Critical mathematical issues detected")
                with st.expander("View Issues"):
                    for issue in validation['flags']['critical']:
                        st.markdown(f"• {issue.get('message', 'Unknown issue')}")
            elif validation.get('status') == 'warning':
                st.warning("⚠️ Mathematical warnings detected")
                with st.expander("View Warnings"):
                    for issue in validation['flags']['warning']:
                        st.markdown(f"• {issue.get('message', 'Unknown warning')}")
    
    def _render_multiple_choice_editor(self, question_index: int, session_prefix: str) -> None:
        """Render multiple choice specific editor"""
        st.markdown("**Answer Choices:**")
        
        choices = ['A', 'B', 'C', 'D']
        for choice in choices:
            choice_key = f"{session_prefix}_choice_{choice.lower()}_{question_index}"
            choice_text = st.text_input(
                f"Choice {choice}",
                key=choice_key,
                help="Use $...$ for mathematical expressions"
            )
            
            # Validate choice text
            if choice_text:
                _, validation = self.latex_processor.render_latex_with_validation(choice_text)
                if validation.get('status') in ['critical', 'warning']:
                    icon = '🚨' if validation['status'] == 'critical' else '⚠️'
                    st.caption(f"{icon} Mathematical issues in choice {choice}")
        
        st.selectbox(
            "Correct Answer",
            choices,
            key=f"{session_prefix}_correct_answer_{question_index}",
            help="Select the correct answer choice"
        )
    
    def _render_numerical_editor(self, question_index: int, session_prefix: str) -> None:
        """Render numerical question specific editor"""
        col1, col2 = st.columns(2)
        
        with col1:
            answer_text = st.text_input(
                "Correct Answer",
                key=f"{session_prefix}_correct_answer_{question_index}",
                help="Enter the numerical answer. Use $...$ for mathematical expressions."
            )
            
            # Validate answer
            if answer_text:
                _, validation = self.latex_processor.render_latex_with_validation(answer_text)
                if validation.get('status') in ['critical', 'warning']:
                    icon = '🚨' if validation['status'] == 'critical' else '⚠️'
                    st.caption(f"{icon} Mathematical issues in answer")
        
        with col2:
            st.number_input(
                "Tolerance",
                min_value=0.0,
                step=0.01,
                key=f"{session_prefix}_tolerance_{question_index}",
                help="Acceptable margin of error for the answer"
            )
    
    def _render_true_false_editor(self, question_index: int, session_prefix: str) -> None:
        """Render true/false specific editor"""
        st.selectbox(
            "Correct Answer",
            ['True', 'False'],
            key=f"{session_prefix}_correct_answer_{question_index}"
        )
    
    def _render_fill_blank_editor(self, question_index: int, session_prefix: str) -> None:
        """Render fill-in-blank specific editor"""
        answer_text = st.text_input(
            "Correct Answer",
            key=f"{session_prefix}_correct_answer_{question_index}",
            help="Enter the correct answer. Use $...$ for mathematical expressions."
        )
        
        # Validate answer
        if answer_text:
            _, validation = self.latex_processor.render_latex_with_validation(answer_text)
            if validation.get('status') in ['critical', 'warning']:
                icon = '🚨' if validation['status'] == 'critical' else '⚠️'
                st.caption(f"{icon} Mathematical issues in answer")
    
    def _render_feedback_form(self, question_index: int, session_prefix: str) -> None:
        """Render feedback form fields"""
        with st.expander("💡 Feedback (Optional)"):
            st.text_area(
                "Correct Answer Feedback",
                key=f"{session_prefix}_correct_feedback_{question_index}",
                height=60,
                help="Feedback shown when student answers correctly"
            )
            
            st.text_area(
                "Incorrect Answer Feedback",
                key=f"{session_prefix}_incorrect_feedback_{question_index}",
                height=60,
                help="Feedback shown when student answers incorrectly"
            )
    
    def _render_save_controls(self, question_index: int, session_prefix: str, validation_results: Optional[Dict[str, Any]]) -> bool:
        """Render save controls and return True if save was triggered"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            save_clicked = st.button(
                "💾 Save Changes", 
                key=f"{session_prefix}_save_{question_index}",
                type="primary",
                disabled=(validation_results and validation_results.get('status') == 'critical')
            )
        
        with col2:
            if st.button("🔄 Reset", key=f"{session_prefix}_reset_{question_index}"):
                # Clear session state for this question
                keys_to_clear = [key for key in st.session_state.keys() 
                               if key.startswith(f"{session_prefix}_") and key.endswith(f"_{question_index}")]
                for key in keys_to_clear:
                    del st.session_state[key]
                st.rerun()
        
        with col3:
            if validation_results and validation_results.get('status') == 'critical':
                st.error("🚨 Cannot save: Critical mathematical issues must be resolved")
            elif validation_results and validation_results.get('status') == 'warning':
                st.warning("⚠️ Mathematical warnings detected - review before saving")
        
        return save_clicked
    
    def _render_validation_status_indicator(self, validation_results: Dict[str, Any]) -> None:
        """Render validation status indicator"""
        status = validation_results.get('status', 'unknown')
        
        if status == 'critical':
            st.error("🚨 **Critical Issues:** Mathematical problems prevent saving")
        elif status == 'warning':
            st.warning("⚠️ **Warnings:** Mathematical issues detected")
        elif status == 'valid':
            st.success("✅ **Valid:** No mathematical issues detected")
    
    def _validate_question_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete question data"""
        all_validations = {}
        
        # Validate question text
        question_text = question_data.get('question_text', '')
        if question_text:
            _, validation = self.latex_processor.render_latex_with_validation(question_text)
            all_validations['question_text'] = validation
        
        # Validate choices (for multiple choice)
        question_type = question_data.get('type', 'multiple_choice')
        if question_type == 'multiple_choice':
            for choice in ['a', 'b', 'c', 'd']:
                choice_text = question_data.get(f'choice_{choice}', '')
                if choice_text:
                    _, validation = self.latex_processor.render_latex_with_validation(choice_text)
                    all_validations[f'choice_{choice}'] = validation
        
        # Validate correct answer
        correct_answer = question_data.get('correct_answer', '')
        if correct_answer and question_type in ['numerical', 'fill_in_blank']:
            _, validation = self.latex_processor.render_latex_with_validation(str(correct_answer))
            all_validations['correct_answer'] = validation
        
        # Validate feedback
        for feedback_type in ['correct_feedback', 'incorrect_feedback']:
            feedback_text = question_data.get(feedback_type, '')
            if feedback_text:
                _, validation = self.latex_processor.render_latex_with_validation(feedback_text)
                all_validations[feedback_type] = validation
        
        # Aggregate results
        overall_status = 'valid'
        total_critical = sum(len(v.get('flags', {}).get('critical', [])) for v in all_validations.values())
        total_warning = sum(len(v.get('flags', {}).get('warning', [])) for v in all_validations.values())
        
        if total_critical > 0:
            overall_status = 'critical'
        elif total_warning > 0:
            overall_status = 'warning'
        
        return {
            'status': overall_status,
            'field_validations': all_validations,
            'summary': {
                'critical_issues': total_critical,
                'warnings': total_warning,
                'fields_with_issues': len([v for v in all_validations.values() if v.get('status') in ['critical', 'warning']])
            }
        }
    
    def _get_default_value(self, field_name: str) -> Any:
        """Get default value for a field"""
        defaults = {
            'title': 'Untitled Question',
            'question_text': '',
            'type': 'multiple_choice',
            'points': 1.0,
            'difficulty': 'Medium',
            'topic': 'General',
            'subtopic': '',
            'correct_answer': 'A',
            'tolerance': 0.0,
            'choice_a': '',
            'choice_b': '',
            'choice_c': '',
            'choice_d': '',
            'correct_feedback': '',
            'incorrect_feedback': ''
        }
        return defaults.get(field_name, '')
    
    def _default_save_callback(self, question_index: int, question_data: Dict[str, Any]) -> bool:
        """Default save callback - just shows success message"""
        st.info(f"🔄 Default save: Question {question_index} data: {list(question_data.keys())}")
        return True
