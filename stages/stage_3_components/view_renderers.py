"""
View Renderers for Q2JSON Stage 3 Human Review
Handles different view modes (teacher, student, etc.)
"""

import streamlit as st
import re

class ViewRenderers:
    """Handles different view modes (teacher, student, etc.)"""
    
    def __init__(self):
        # This class should NOT auto-correct LaTeX errors
        # LaTeX should be corrected in an earlier stage before Human Review
        pass
    
    def render_teacher_view(self, selected_question, question_idx, questions):
        """Render teacher view with live preview"""
        
        # NO LaTeX validation/correction here - JSON should already be clean
        # Just render the editor and preview as-is
        
        # Create two columns for preview and editor
        preview_col, editor_col = st.columns([1, 1])
        
        with preview_col:
            st.subheader("👁️ Preview")
            
            # Show exactly what's in the JSON/session state
            self._render_student_preview(selected_question, question_idx)
        
        with editor_col:
            st.subheader("📝 Editor")
            
            # Allow editing of the question
            self._render_editable_form(selected_question, question_idx, questions)
    
    def _render_student_preview(self, selected_question, question_idx):
        """Render how the question would appear to a student - EXACTLY as in JSON"""
        
        discard_counter = st.session_state.get(f"discard_counter_{question_idx}", 0)
        
        # Get current values from session state OR original JSON (NO modifications)
        current_title = st.session_state.get(f"title_{question_idx}_{discard_counter}", selected_question.get('title', ''))
        current_text = st.session_state.get(f"text_{question_idx}_{discard_counter}", selected_question.get('question_text', ''))
        current_type = st.session_state.get(f"type_{question_idx}_{discard_counter}", selected_question.get('type', 'multiple_choice'))
        current_points = st.session_state.get(f"points_{question_idx}_{discard_counter}", selected_question.get('points', 1))
        
        # NO LaTeX fixes applied - show exactly what's in the data
        
        # Question title and text
        st.write(f"**Question {question_idx + 1}**")
        
        if current_title:
            st.write(f"*{current_title}*")
        else:
            st.write("*No title*")
        
        # Render question text with LaTeX (but don't modify the text)
        if current_text:
            st.markdown(current_text)
        else:
            st.write('No question text')
        
        # Show question type specific interface
        if current_type == 'multiple_choice':
            st.write("**Select the correct answer:**")
            
            # Get current choices from session state with versioned keys
            current_choices = []
            original_choices = selected_question.get('choices', [])
            
            for i in range(10):
                choice_key = f"choice_{question_idx}_{i}_{discard_counter}"
                choice_value = st.session_state.get(choice_key, "")
                
                # If no value in session state, get from original question
                if not choice_value and i < len(original_choices):
                    choice_value = original_choices[i]
                
                if choice_value and choice_value.strip():
                    # NO LaTeX fixes - show exactly as-is
                    current_choices.append(choice_value.strip())
            
            if current_choices:
                # Show choices as radio buttons
                choice_labels = [f"{chr(65+i)}. {choice}" for i, choice in enumerate(current_choices)]
                
                # Get current correct answer
                current_correct = st.session_state.get(f"correct_{question_idx}_{discard_counter}", selected_question.get('correct_answer', ''))
                
                # Find which choice is correct
                correct_idx = 0
                if current_correct in current_choices:
                    correct_idx = current_choices.index(current_correct)
                
                st.radio(
                    "Options:",
                    choice_labels,
                    index=correct_idx,
                    key=f"student_preview_{question_idx}_{discard_counter}",
                    disabled=False
                )
                
                # Show which is correct
                st.caption(f"✅ Correct answer: {current_correct}")
            else:
                st.warning("No choices defined")
        
        elif current_type == 'numerical':
            st.write("**Enter your numerical answer:**")
            
            current_num_answer = st.session_state.get(f"correct_num_{question_idx}_{discard_counter}", None)
            if current_num_answer is None:
                try:
                    current_num_answer = float(selected_question.get('correct_answer', 0.0))
                except (ValueError, TypeError):
                    current_num_answer = 0.0
            
            st.number_input(
                "Answer:",
                key=f"student_num_preview_{question_idx}_{discard_counter}",
                disabled=True
            )
            
            current_tolerance = st.session_state.get(f"tolerance_{question_idx}_{discard_counter}", selected_question.get('tolerance', 0.05))
            if current_tolerance > 0:
                st.caption(f"Tolerance: ±{current_tolerance}")
            
            st.caption(f"✅ Correct answer: {current_num_answer}")
        
        elif current_type == 'true_false':
            st.write("**Select True or False:**")
            
            current_tf_answer = st.session_state.get(f"correct_tf_{question_idx}_{discard_counter}", selected_question.get('correct_answer', 'True'))
            
            st.radio(
                "Answer:",
                ["True", "False"],
                key=f"student_tf_preview_{question_idx}_{discard_counter}",
                disabled=False
            )
            
            st.caption(f"✅ Correct answer: {current_tf_answer}")
        
        elif current_type == 'short_answer':
            st.write("**Enter your answer:**")
            
            current_text_answer = st.session_state.get(f"correct_text_{question_idx}_{discard_counter}", selected_question.get('correct_answer', ''))
            
            st.text_input(
                "Answer:",
                key=f"student_text_preview_{question_idx}_{discard_counter}",
                disabled=True
            )
            
            st.caption(f"✅ Correct answer: {current_text_answer}")
        
        # Show points and difficulty
        st.caption(f"Points: {current_points}")
        
        current_difficulty = st.session_state.get(f"difficulty_{question_idx}_{discard_counter}", selected_question.get('difficulty', 'Medium'))
        st.caption(f"Difficulty: {current_difficulty}")

    def _render_editable_form(self, selected_question, question_idx, questions):
        """Render the editable form in the editor column"""
        
        # Check if we just discarded changes
        just_discarded = st.session_state.get(f'discarded_{question_idx}', False)
        if just_discarded:
            st.success("✅ Changes discarded - editor reset to original values")
            del st.session_state[f'discarded_{question_idx}']
        
        # Get discard counter for unique keys
        discard_counter = st.session_state.get(f"discard_counter_{question_idx}", 0)
        
        # Question Title - Editable (with versioned key)
        title_key = f"title_{question_idx}_{discard_counter}"
        new_title = st.text_input(
            "Question Title",
            value=selected_question.get('title', ''),
            key=title_key,
            help="Changes appear in preview immediately"
        )
        
        # Question Text - Editable (with versioned key)
        text_key = f"text_{question_idx}_{discard_counter}"
        new_text = st.text_area(
            "Question Text",
            value=selected_question.get('question_text', ''),
            height=100,
            key=text_key,
            help="Changes appear in preview immediately"
        )
        
        # Question Type - Editable (with versioned key)
        type_key = f"type_{question_idx}_{discard_counter}"
        current_type = selected_question.get('type', 'multiple_choice')
        
        try:
            type_index = ["multiple_choice", "numerical", "true_false", "short_answer"].index(current_type)
        except ValueError:
            type_index = 0
        
        new_type = st.selectbox(
            "Question Type",
            ["multiple_choice", "numerical", "true_false", "short_answer"],
            index=type_index,
            key=type_key,
            help="Changes appear in preview immediately"
        )
        
        # Type-specific editors
        if new_type == 'multiple_choice':
            self._render_multiple_choice_editor(selected_question, question_idx, discard_counter)
        elif new_type == 'numerical':
            self._render_numerical_editor(selected_question, question_idx, discard_counter)
        elif new_type == 'true_false':
            self._render_true_false_editor(selected_question, question_idx, discard_counter)
        else:
            self._render_text_editor(selected_question, question_idx, discard_counter)
        
        # Points and Difficulty (with versioned keys)
        col1, col2 = st.columns(2)
        
        with col1:
            points_key = f"points_{question_idx}_{discard_counter}"
            st.number_input(
                "Points",
                value=selected_question.get('points', 1),
                min_value=0,
                max_value=10,
                key=points_key,
                help="Changes appear in preview immediately"
            )
    
        with col2:
            difficulty_key = f"difficulty_{question_idx}_{discard_counter}"
            current_difficulty = selected_question.get('difficulty', 'Medium')
            
            try:
                difficulty_index = ["Easy", "Medium", "Hard"].index(current_difficulty)
            except ValueError:
                difficulty_index = 1
            
            st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
                index=difficulty_index,
                key=difficulty_key,
                help="Changes appear in preview immediately"
            )
    
        # Action buttons
        st.divider()
    
        save_col1, save_col2 = st.columns(2)
    
        with save_col1:
            if st.button(f"💾 Save Question", key=f"save_{question_idx}_{discard_counter}", type="primary"):
                # Here we would save the question
                # For now, just show a success message
                st.success("✅ Question saved!")
    
        with save_col2:
            if st.button(f"🗑️ Discard Changes", key=f"discard_{question_idx}_{discard_counter}"):
                # Actually discard changes by clearing session state
                self._discard_changes(selected_question, question_idx)
                st.rerun()

    def _discard_changes(self, selected_question, question_idx):
        """Actually discard changes by clearing session state"""
        
        # List of all possible widget keys to clear
        keys_to_clear = [
            f"title_{question_idx}",
            f"text_{question_idx}",
            f"type_{question_idx}",
            f"points_{question_idx}",
            f"difficulty_{question_idx}",
            f"tolerance_{question_idx}"
        ]
        
        # Add choice keys
        for i in range(10):
            keys_to_clear.append(f"choice_{question_idx}_{i}")
        
        # Clear correct answer keys
        correct_keys_to_clear = [
            f"correct_{question_idx}",
            f"correct_num_{question_idx}",
            f"correct_tf_{question_idx}",
            f"correct_text_{question_idx}"
        ]
        
        # Clear versioned keys
        discard_counter = st.session_state.get(f"discard_counter_{question_idx}", 0)
        for i in range(discard_counter + 2):
            for base_key in keys_to_clear + correct_keys_to_clear:
                versioned_key = f"{base_key}_{i}"
                if versioned_key in st.session_state:
                    del st.session_state[versioned_key]
        
        # Clear all keys from session state
        for key in keys_to_clear + correct_keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Increment discard counter to force widget recreation
        st.session_state[f"discard_counter_{question_idx}"] = discard_counter + 1
        
        # Set a flag to indicate we just discarded changes
        st.session_state[f'discarded_{question_idx}'] = True

    def _render_multiple_choice_editor(self, selected_question, question_idx, discard_counter):
        """Render multiple choice editor"""
        
        st.write("**Answer Choices:**")
        
        current_choices = selected_question.get('choices', [])
        num_fields = max(4, len(current_choices))
        
        current_choices_for_dropdown = []
        for i in range(num_fields):
            choice_key = f"choice_{question_idx}_{i}_{discard_counter}"
            choice_value = current_choices[i] if i < len(current_choices) else ""
            
            st.text_input(
                f"Choice {i+1}",
                value=choice_value,
                key=choice_key,
                placeholder=f"Enter choice {i+1}...",
                help="Changes appear in preview immediately"
            )
            
            widget_value = st.session_state.get(choice_key, choice_value)
            if widget_value and widget_value.strip():
                current_choices_for_dropdown.append(widget_value.strip())
        
        # Correct answer selector
        if current_choices_for_dropdown:
            st.write("**Correct Answer:**")
            
            current_correct = selected_question.get('correct_answer', '')
            correct_idx = 0
            if current_correct in current_choices_for_dropdown:
                correct_idx = current_choices_for_dropdown.index(current_correct)
            
            st.selectbox(
                "Select Correct Answer",
                current_choices_for_dropdown,
                index=correct_idx,
                key=f"correct_{question_idx}_{discard_counter}",
                help="Changes appear in preview immediately"
            )
        else:
            st.warning("Please add at least 2 choices")

    def _render_numerical_editor(self, selected_question, question_idx, discard_counter):
        """Render numerical question editor"""
        
        st.write("**Numerical Answer:**")
        
        current_answer = selected_question.get('correct_answer', '')
        try:
            numeric_value = float(current_answer) if current_answer else 0.0
        except (ValueError, TypeError):
            numeric_value = 0.0
        
        st.number_input(
            "Correct Answer",
            value=numeric_value,
            format="%.4f",
            key=f"correct_num_{question_idx}_{discard_counter}",
            help="Changes appear in preview immediately"
        )
        
        st.number_input(
            "Tolerance (±)",
            value=selected_question.get('tolerance', 0.05),
            min_value=0.0,
            max_value=1.0,
            format="%.4f",
            key=f"tolerance_{question_idx}_{discard_counter}",
            help="Acceptable margin of error"
        )

    def _render_true_false_editor(self, selected_question, question_idx, discard_counter):
        """Render true/false question editor"""
        
        st.write("**True/False Answer:**")
        
        current_answer = selected_question.get('correct_answer', 'True')
        if current_answer not in ['True', 'False']:
            current_answer = 'True'
        
        st.selectbox(
            "Correct Answer",
            ["True", "False"],
            index=0 if current_answer == 'True' else 1,
            key=f"correct_tf_{question_idx}_{discard_counter}",
            help="Changes appear in preview immediately"
        )

    def _render_text_editor(self, selected_question, question_idx, discard_counter):
        """Render text answer editor"""
        
        st.write("**Text Answer:**")
        
        st.text_input(
            "Correct Answer",
            value=selected_question.get('correct_answer', ''),
            key=f"correct_text_{question_idx}_{discard_counter}",
            help="Changes appear in preview immediately"
        )
