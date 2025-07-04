"""
Debug Utilities for Q2JSON Stage 3 Human Review
Debug and utility functions
"""

import streamlit as st

class DebugUtils:
    """Debug and utility functions"""
    
    def debug_widget_state(self, question_idx):
        """Debug function to show widget state"""
        st.write(f"Debug info for question {question_idx}")
    
    def show_question_info(self, question, question_idx):
        """Show question information"""
        st.write(f"Question {question_idx + 1} info:")
        st.json(question)
