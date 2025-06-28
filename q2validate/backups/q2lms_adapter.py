#!/usr/bin/env python3
"""
Simplified Q2LMS Adapter for Q2Validate
Uses basic preview functionality while Q2LMS integration is being developed
"""

import streamlit as st

class Q2LMSAdapter:
    """Simplified adapter for Q2LMS-style question preview"""
    
    def __init__(self):
        """Initialize with basic LaTeX conversion capability"""
        self.latex_converter = BasicLaTeXConverter()
    
    def is_available(self) -> bool:
        """Always available with basic functionality"""
        return True
    
    def preview_question(self, question_data):
        """Basic question preview using Streamlit"""
        return self._display_basic_preview(question_data)
    
    def render_latex(self, text: str) -> str:
        """Basic LaTeX rendering"""
        return self.latex_converter.convert_for_display(text)
    
    def determine_correct_answer(self, correct_answer_text, choice_texts):
        """Determine correct answer letter from text"""
        if not correct_answer_text:
            return 'A'
        
        answer_clean = str(correct_answer_text).strip()
        
        # Case 1: Already a letter (A, B, C, D)
        if answer_clean.upper() in ['A', 'B', 'C', 'D']:
            return answer_clean.upper()
        
        # Case 2: Exact text match (case insensitive)
        answer_lower = answer_clean.lower()
        for letter, choice_text in choice_texts.items():
            if str(choice_text).lower().strip() == answer_lower:
                return letter
        
        # Default fallback
        return 'A'
    
    def _display_basic_preview(self, question_data):
        """Display question preview using Streamlit"""
        
        # Header with metadata
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            title = question_data.get('title', 'Untitled')
            st.markdown(f"**{self.render_latex(title)}**")
        
        with col2:
            question_type = question_data.get('type', 'unknown')
            st.markdown(f"🏷️ **{question_type.replace('_', ' ').title()}**")
        
        with col3:
            difficulty = question_data.get('difficulty', 'Medium')
            difficulty_colors = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}
            icon = difficulty_colors.get(difficulty, '⚪')
            st.markdown(f"{icon} **{difficulty}**")
        
        with col4:
            points = question_data.get('points', 1)
            st.markdown(f"**{points} pts**")
        
        # Topic info
        topic = question_data.get('topic', 'General')
        subtopic = question_data.get('subtopic', '')
        topic_info = f"📚 {topic}"
        if subtopic:
            topic_info += f" → {subtopic}"
        st.markdown(f"*{topic_info}*")
        
        st.markdown("---")
        
        # Question text
        question_text = question_data.get('question_text', '')
        rendered_text = self.render_latex(question_text)
        st.markdown(f"**Question:** {rendered_text}")
        
        # Handle different question types
        if question_data.get('type') == 'multiple_choice':
            st.markdown("**Choices:**")
            choices = question_data.get('choices', [])
            correct_answer = question_data.get('correct_answer', '')
            
            choice_texts = {}
            for i, choice in enumerate(choices):
                letter = chr(65 + i)  # A, B, C, D
                choice_texts[letter] = str(choice)
            
            correct_letter = self.determine_correct_answer(correct_answer, choice_texts)
            
            for i, choice in enumerate(choices):
                letter = chr(65 + i)
                rendered_choice = self.render_latex(str(choice))
                
                if letter == correct_letter:
                    st.markdown(f"• **{letter}:** {rendered_choice} ✅")
                else:
                    st.markdown(f"• **{letter}:** {rendered_choice}")
        
        elif question_data.get('type') == 'numerical':
            correct_answer = self.render_latex(str(question_data.get('correct_answer', '')))
            st.markdown(f"**Correct Answer:** {correct_answer} ✅")
            
            tolerance = question_data.get('tolerance', 0)
            if tolerance and float(tolerance) > 0:
                st.markdown(f"**Tolerance:** ±{tolerance}")
        
        elif question_data.get('type') == 'true_false':
            correct_answer = question_data.get('correct_answer', '')
            st.markdown(f"**Correct Answer:** {correct_answer} ✅")
        
        elif question_data.get('type') == 'fill_in_multiple_blanks':
            correct_answer = self.render_latex(str(question_data.get('correct_answer', '')))
            st.markdown(f"**Correct Answer:** {correct_answer} ✅")
        
        # Feedback
        correct_feedback = question_data.get('feedback_correct', '')
        incorrect_feedback = question_data.get('feedback_incorrect', '')
        
        if correct_feedback or incorrect_feedback:
            with st.expander("💡 View Feedback"):
                if correct_feedback:
                    rendered_correct = self.render_latex(correct_feedback)
                    st.markdown(f"**Correct:** {rendered_correct}")
                if incorrect_feedback:
                    rendered_incorrect = self.render_latex(incorrect_feedback)
                    st.markdown(f"**Incorrect:** {rendered_incorrect}")


class BasicLaTeXConverter:
    """Basic LaTeX to display conversion for preview"""
    
    def __init__(self):
        # Basic LaTeX symbol mapping for display
        self.latex_to_display = {
            r'\Omega': 'Ω', r'\omega': 'ω', r'\pi': 'π', r'\phi': 'φ', r'\theta': 'θ',
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ', r'\lambda': 'λ',
            r'\mu': 'μ', r'\sigma': 'σ', r'\tau': 'τ', r'\rho': 'ρ',
            r'\pm': '±', r'\times': '×', r'\cdot': '·', r'\div': '÷',
            r'\neq': '≠', r'\leq': '≤', r'\geq': '≥', r'\approx': '≈',
            r'^\circ': '°', r'^2': '²', r'^3': '³'
        }
    
    def convert_for_display(self, text: str) -> str:
        """Convert LaTeX notation to Unicode for basic display"""
        if not text or not isinstance(text, str):
            return text
        
        result = text
        
        # Convert LaTeX symbols to Unicode for display
        for latex_cmd, display_char in self.latex_to_display.items():
            # Handle both $...$ wrapped and unwrapped versions
            result = result.replace(f'${latex_cmd}$', display_char)
            result = result.replace(latex_cmd, display_char)
        
        # Remove any remaining $ symbols for basic display
        result = result.replace('$', '')
        
        # Handle \text{} commands
        import re
        result = re.sub(r'\\text\{([^}]+)\}', r'\1', result)
        
        return result
