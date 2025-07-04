"""
Question Editor for Q2JSON Stage 3 Human Review
Handles question editing functionality
"""

import streamlit as st

class QuestionEditor:
    """Handles question editing functionality"""
    
    def render_editor(self, selected_question, question_idx):
        """Render the main question editor"""
        st.write("Question editor - Coming soon!")
        st.json(selected_question)
