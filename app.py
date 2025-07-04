# app.py - Clean Modular Version
# NO MORE INDENTATION HELL! 🎉

import streamlit as st

# Import our clean, modular components
from navigation.state import initialize_session_state, validate_session_state
from navigation.manager import NavigationManager
from stages.stage_0_prompt import render_prompt_builder
from stages.stage_1_processing import render_ai_processing  
from stages.stage_2_validation import render_json_validation
from stages.stage_3_human_review import render_human_review
from utils.ui_helpers import load_css, create_sidebar, create_main_header
from modules.latex_corrector import LaTeXCorrector

def main():
    """Main application entry point - Clean and Simple!"""
    
    # Page configuration
    st.set_page_config(
        page_title="q2JSON Generator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize application
    initialize_session_state()
    validate_session_state()
    load_css()
    
    # Create UI components
    create_sidebar()
    create_main_header()
    
    # Route to correct stage - NO COMPLEX INDENTATION!
    current_stage = st.session_state.current_stage
    
    if current_stage == 0:
        render_prompt_builder()
    elif current_stage == 1:
        render_ai_processing()  # This was your problem stage - now clean!
    elif current_stage == 2:
        render_json_validation()
    elif current_stage == 3:
        render_human_review()
    else:
        st.error(f"Invalid stage: {current_stage}")
        st.session_state.current_stage = 0
        st.rerun()


def create_main_header():
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #1f77b4 0%, #764ba2 100%);
            padding: 1.5rem 1rem 1rem 1rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 2px 8px rgba(30, 60, 120, 0.08);
            display: flex;
            align-items: center;
        ">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Univ_logo.png" alt="Institution Logo" style="height:48px;margin-right:1.5rem;">
            <div>
                <div style="font-size:2rem;font-weight:700;letter-spacing:1px;">Q2JSON Generator</div>
                <div style="font-size:1.1rem;font-weight:400;margin-top:0.2rem;">AI-to-LMS Educational Question Pipeline</div>
                <div style="font-size:0.95rem;font-weight:300;margin-top:0.2rem;">Institutional Edition &mdash; <span style="font-weight:500;">Faculty Use Only</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()