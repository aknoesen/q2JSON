# extracted_components/question_renderer.py
"""
Q2JSON Question Renderer
Extracted and enhanced from Q2LMS question rendering components

Provides sophisticated question display with LaTeX support and validation indicators.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from .latex_processor import Q2JSONLaTeXProcessor


class Q2JSONQuestionRenderer:
    """
    Enhanced question renderer combining Q2LMS display logic with Q2JSON validation.
    
    Extracted from:
    - Q2LMS interface_delete_questions._render_question_preview()
    - Q2LMS question_editor.display_live_question_preview()
    
    Enhanced with:
    - Mathematical validation indicators
    - Q2JSON-specific flagging system
    - Enhanced accessibility features
    """
    
    def __init__(self):
        self.latex_processor = Q2JSONLaTeXProcessor()
        self.question_types = {
            'multiple_choice': self._render_multiple_choice_preview,
            'numerical': self._render_numerical_preview,
            'true_false': self._render_true_false_preview,
            'fill_in_blank': self._render_fill_blank_preview
        }
    
    def render_question_with_validation(self, 
                                      question_data: Dict[str, Any], 
                                      validation_results: Optional[Dict[str, Any]] = None,
                                      show_validation_indicators: bool = True) -> None:
        """
        Render question with mathematical validation indicators.
        
        Args:
            question_data: Question data dictionary
            validation_results: Optional validation results
            show_validation_indicators: Whether to show validation indicators
        """
        try:
            # Render question header with metadata
            self._render_question_header(question_data, validation_results)
            
            # Main question content
            self._render_question_content(question_data, validation_results, show_validation_indicators)
            
            # Question-type specific content
            question_type = question_data.get('question_type', question_data.get('type', 'multiple_choice'))
            if question_type in self.question_types:
                self.question_types[question_type](question_data, validation_results)
            else:
                st.warning(f"⚠️ Unknown question type: {question_type}")
            
            # Feedback section
            self._render_feedback_preview(question_data, validation_results)
            
            # Validation summary (if requested)
            if show_validation_indicators and validation_results:
                self._render_validation_summary(validation_results)
                
        except Exception as e:
            st.error(f"❌ Error rendering question: {e}")
            with st.expander("🔍 Error Details"):
                st.exception(e)
    
    def _render_question_header(self, question_data: Dict[str, Any], validation_results: Optional[Dict[str, Any]] = None) -> None:
        """Render question header with metadata"""
        # Header with metadata (enhanced from Q2LMS)
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            title = question_data.get('title', question_data.get('Title', 'Untitled'))
            
            # Add validation indicator to title if available
            if validation_results and validation_results.get('status') == 'critical':
                st.markdown(f"🚨 **{title}** *(Mathematical issues detected)*")
            elif validation_results and validation_results.get('status') == 'warning':
                st.markdown(f"⚠️ **{title}** *(Mathematical warnings)*")
            else:
                st.markdown(f"**{title}**")
        
        with col2:
            question_type = question_data.get('question_type', question_data.get('Type', 'multiple_choice'))
            type_display = question_type.replace('_', ' ').title()
            st.markdown(f"🏷️ **{type_display}**")
        
        with col3:
            difficulty = question_data.get('difficulty', question_data.get('Difficulty', 'Medium'))
            difficulty_colors = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}
            difficulty_icon = difficulty_colors.get(difficulty, '⚪')
            st.markdown(f"{difficulty_icon} **{difficulty}**")
        
        with col4:
            points = question_data.get('points', question_data.get('Points', 1))
            st.markdown(f"**{points} pts**")
        
        # Topic information
        topic = question_data.get('topic', question_data.get('Topic', 'General'))
        subtopic = question_data.get('subtopic', question_data.get('Subtopic', ''))
        topic_info = f"📚 {topic}"
        if subtopic and subtopic not in ['', 'N/A', 'empty']:
            topic_info += f" → {subtopic}"
        st.markdown(f"*{topic_info}*")
        
        st.markdown("---")
    
    def _render_question_content(self, 
                               question_data: Dict[str, Any], 
                               validation_results: Optional[Dict[str, Any]] = None,
                               show_validation_indicators: bool = True) -> None:
        """Render main question content with LaTeX and validation"""
        question_text = question_data.get('question_text', question_data.get('Question_Text', ''))
        
        if not question_text:
            st.warning("⚠️ No question text provided")
            return
        
        # Render with LaTeX processing and validation
        rendered_text, text_validation = self.latex_processor.render_latex_with_validation(question_text)
        
        # Display question text
        st.markdown(f"**Question:** {rendered_text}")
        
        # Show validation indicators if requested
        if show_validation_indicators and text_validation.get('flags'):
            self._render_inline_validation_indicators(text_validation, "Question Text")
    
    def _render_multiple_choice_preview(self, 
                                      question_data: Dict[str, Any], 
                                      validation_results: Optional[Dict[str, Any]] = None) -> None:
        """Render multiple choice preview with validation"""
        st.markdown("**Choices:**")
        
        choices_list = ['A', 'B', 'C', 'D']
        correct_answer = question_data.get('correct_answer', 'A')
        
        # Extract choice texts
        choice_texts = {}
        for choice_letter in choices_list:
            choice_key = f'choice_{choice_letter.lower()}'
            choice_text = question_data.get(choice_key, '')
            if choice_text and str(choice_text).strip():
                choice_texts[choice_letter] = str(choice_text).strip()
        
        # Determine correct answer letter
        if correct_answer not in ['A', 'B', 'C', 'D']:
            correct_letter = self._determine_correct_answer_letter(correct_answer, choice_texts)
        else:
            correct_letter = correct_answer
        
        # Render choices with LaTeX and validation
        choice_validations = {}
        for choice_letter in choices_list:
            if choice_letter in choice_texts:
                choice_text_clean = choice_texts[choice_letter]
                
                # Process LaTeX with validation
                choice_text_html, choice_validation = self.latex_processor.render_latex_with_validation(choice_text_clean)
                choice_validations[choice_letter] = choice_validation
                
                is_correct = (choice_letter == correct_letter)
                
                # Display choice with validation indicators
                if is_correct:
                    choice_display = f"• **{choice_letter}:** {choice_text_html} ✅"
                else:
                    choice_display = f"• **{choice_letter}:** {choice_text_html}"
                
                # Add validation warning if needed
                if choice_validation.get('status') in ['critical', 'warning']:
                    choice_display += f" {self._get_validation_icon(choice_validation['status'])}"
                
                st.markdown(choice_display)
        
        # Show choice validation summary if any issues
        choice_issues = [v for v in choice_validations.values() if v.get('flags') and (v['flags']['critical'] or v['flags']['warning'])]
        if choice_issues:
            with st.expander(f"⚠️ Choice Validation Issues ({len(choice_issues)} choices affected)"):
                for letter, validation in choice_validations.items():
                    if validation.get('flags') and (validation['flags']['critical'] or validation['flags']['warning']):
                        st.markdown(f"**Choice {letter}:**")
                        self._render_validation_details(validation)
    
    def _render_numerical_preview(self, 
                                question_data: Dict[str, Any], 
                                validation_results: Optional[Dict[str, Any]] = None) -> None:
        """Render numerical preview with validation"""
        correct_answer = str(question_data.get('correct_answer', ''))
        
        # Process answer with LaTeX validation
        correct_answer_html, answer_validation = self.latex_processor.render_latex_with_validation(correct_answer)
        
        # Display answer
        answer_display = f"**Correct Answer:** {correct_answer_html} ✅"
        if answer_validation.get('status') in ['critical', 'warning']:
            answer_display += f" {self._get_validation_icon(answer_validation['status'])}"
        
        st.markdown(answer_display)
        
        # Show tolerance if available
        tolerance = question_data.get('tolerance', 0)
        if tolerance and float(tolerance) > 0:
            st.markdown(f"**Tolerance:** ±{tolerance}")
        
        # Show validation details if issues
        if answer_validation.get('flags') and (answer_validation['flags']['critical'] or answer_validation['flags']['warning']):
            with st.expander("⚠️ Answer Validation Issues"):
                self._render_validation_details(answer_validation)
    
    def _render_true_false_preview(self, 
                                 question_data: Dict[str, Any], 
                                 validation_results: Optional[Dict[str, Any]] = None) -> None:
        """Render true/false preview"""
        correct_answer = str(question_data.get('correct_answer', '')).strip()
        st.markdown(f"**Correct Answer:** {correct_answer} ✅")
    
    def _render_fill_blank_preview(self, 
                                 question_data: Dict[str, Any], 
                                 validation_results: Optional[Dict[str, Any]] = None) -> None:
        """Render fill-in-blank preview with validation"""
        correct_answer = str(question_data.get('correct_answer', ''))
        
        # Process answer with LaTeX validation
        correct_answer_html, answer_validation = self.latex_processor.render_latex_with_validation(correct_answer)
        
        # Display answer
        answer_display = f"**Correct Answer:** {correct_answer_html} ✅"
        if answer_validation.get('status') in ['critical', 'warning']:
            answer_display += f" {self._get_validation_icon(answer_validation['status'])}"
        
        st.markdown(answer_display)
        
        # Show validation details if issues
        if answer_validation.get('flags') and (answer_validation['flags']['critical'] or answer_validation['flags']['warning']):
            with st.expander("⚠️ Answer Validation Issues"):
                self._render_validation_details(answer_validation)
    
    def _render_feedback_preview(self, 
                               question_data: Dict[str, Any], 
                               validation_results: Optional[Dict[str, Any]] = None) -> None:
        """Render feedback with validation"""
        correct_feedback = question_data.get('correct_feedback', question_data.get('feedback_correct', ''))
        incorrect_feedback = question_data.get('incorrect_feedback', question_data.get('feedback_incorrect', ''))
        
        if correct_feedback or incorrect_feedback:
            feedback_validations = {}
            
            with st.expander("💡 View Feedback"):
                if correct_feedback:
                    rendered_correct_html, correct_validation = self.latex_processor.render_latex_with_validation(str(correct_feedback))
                    feedback_validations['correct'] = correct_validation
                    
                    correct_display = f"**Correct:** {rendered_correct_html}"
                    if correct_validation.get('status') in ['critical', 'warning']:
                        correct_display += f" {self._get_validation_icon(correct_validation['status'])}"
                    
                    st.markdown(correct_display)
                
                if incorrect_feedback:
                    rendered_incorrect_html, incorrect_validation = self.latex_processor.render_latex_with_validation(str(incorrect_feedback))
                    feedback_validations['incorrect'] = incorrect_validation
                    
                    incorrect_display = f"**Incorrect:** {rendered_incorrect_html}"
                    if incorrect_validation.get('status') in ['critical', 'warning']:
                        incorrect_display += f" {self._get_validation_icon(incorrect_validation['status'])}"
                    
                    st.markdown(incorrect_display)
                
                # Show validation issues for feedback
                feedback_issues = [v for v in feedback_validations.values() if v.get('flags') and (v['flags']['critical'] or v['flags']['warning'])]
                if feedback_issues:
                    st.markdown("**Feedback Validation Issues:**")
                    for feedback_type, validation in feedback_validations.items():
                        if validation.get('flags') and (validation['flags']['critical'] or validation['flags']['warning']):
                            st.markdown(f"*{feedback_type.title()} feedback:*")
                            self._render_validation_details(validation, compact=True)
    
    def _render_validation_summary(self, validation_results: Dict[str, Any]) -> None:
        """Render comprehensive validation summary"""
        if not validation_results:
            return
        
        status = validation_results.get('status', 'unknown')
        
        with st.expander(f"🔍 Mathematical Validation Summary ({status.upper()})"):
            summary = self.latex_processor.validator.get_validation_summary(validation_results)
            st.markdown(summary)
    
    def _render_inline_validation_indicators(self, validation_results: Dict[str, Any], field_name: str) -> None:
        """Render compact validation indicators"""
        flags = validation_results.get('flags', {})
        
        if flags.get('critical'):
            st.error(f"🚨 **{field_name}:** {len(flags['critical'])} critical mathematical issues")
        elif flags.get('warning'):
            st.warning(f"⚠️ **{field_name}:** {len(flags['warning'])} mathematical warnings")
        elif flags.get('info'):
            st.info(f"ℹ️ **{field_name}:** {len(flags['info'])} optimization suggestions")
    
    def _render_validation_details(self, validation_results: Dict[str, Any], compact: bool = False) -> None:
        """Render detailed validation information"""
        flags = validation_results.get('flags', {})
        
        for level in ['critical', 'warning', 'info']:
            issues = flags.get(level, [])
            if issues:
                level_icon = {'critical': '🚨', 'warning': '⚠️', 'info': 'ℹ️'}[level]
                if not compact:
                    st.markdown(f"**{level_icon} {level.title()} Issues:**")
                
                for issue in issues[:3 if compact else len(issues)]:  # Limit in compact mode
                    message = issue.get('message', 'Unknown issue')
                    if compact:
                        st.caption(f"• {message}")
                    else:
                        st.markdown(f"• {message}")
                        if 'suggestion' in issue:
                            st.caption(f"  💡 {issue['suggestion']}")
                
                if compact and len(issues) > 3:
                    st.caption(f"• ... and {len(issues) - 3} more")
    
    def _get_validation_icon(self, status: str) -> str:
        """Get validation status icon"""
        icons = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️',
            'valid': '✅'
        }
        return icons.get(status, '❓')
    
    def _determine_correct_answer_letter(self, correct_answer_text: str, choice_texts: Dict[str, str]) -> str:
        """
        Determine the correct answer letter (A, B, C, D) from the correct answer text.
        Extracted from Q2LMS logic.
        """
        if not correct_answer_text:
            return 'A'
        
        answer_clean = str(correct_answer_text).strip()
        
        # Case 1: Already a letter (A, B, C, D)
        if answer_clean.upper() in ['A', 'B', 'C', 'D']:
            return answer_clean.upper()
        
        # Case 2: Exact text match (case insensitive)
        answer_lower = answer_clean.lower()
        for letter, choice_text in choice_texts.items():
            if choice_text.lower().strip() == answer_lower:
                return letter
        
        # Case 3: Partial match for long answers
        if len(answer_clean) > 10:
            for letter, choice_text in choice_texts.items():
                if (len(choice_text) > 10 and answer_lower in choice_text.lower()):
                    return letter
        
        # Default fallback
        return 'A'
