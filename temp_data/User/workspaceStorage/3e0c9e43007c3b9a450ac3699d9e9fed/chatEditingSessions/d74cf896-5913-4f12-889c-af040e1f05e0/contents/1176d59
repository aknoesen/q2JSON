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
    else:
        st.error(f"Invalid stage: {current_stage}")
        st.session_state.current_stage = 0
        st.rerun()


if __name__ == "__main__":
    main()