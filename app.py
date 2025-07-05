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
from utils.ui_helpers import load_css, create_sidebar, create_main_header, show_stage_banner
from modules.latex_corrector import LaTeXCorrector

def main():
    st.write(f"DEBUG: App starting - current_stage = {st.session_state.get('current_stage', 'NOT_SET')}")
    # Initialize session state
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 0
        st.write("DEBUG: Initialized current_stage to 0")
    else:
        st.write(f"DEBUG: Found existing current_stage = {st.session_state.current_stage}")
    """Main application entry point - Clean and Simple!"""
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 0

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

    # --- DEBUG: Show current stage before routing ---
    previous_stage = st.session_state.get('_previous_stage', None)
    current_stage = st.session_state.get('current_stage', 0)
    if previous_stage is not None and previous_stage != current_stage:
        st.write(f"DEBUG: Stage changed from {previous_stage} to {current_stage}")
    st.session_state['_previous_stage'] = current_stage

    st.write(f"🔍 DEBUG: app.py - current_stage = {current_stage}")

    # Route to correct stage - NO COMPLEX INDENTATION!
    if current_stage == 0:
        st.write("🔍 DEBUG: app.py - Calling render_prompt_builder()")
        render_prompt_builder()
    elif current_stage == 1:
        st.write("🔍 DEBUG: app.py - Calling render_ai_processing()")
        render_ai_processing()
    elif current_stage == 2:
        st.write("🔍 DEBUG: app.py - Calling render_json_validation()")
        render_json_validation()
    elif current_stage == 3:
        st.write("🔍 DEBUG: app.py - Calling render_human_review()")
        render_human_review()
    elif current_stage == 4:
        st.write("🔍 DEBUG: app.py - Calling render_output_completion()")
        from stages.stage_4_output import render_output_completion
        render_output_completion()
    else:
        st.error("Unknown stage. Please reset the application.")

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
        ">
            <div style="margin-top:0.2rem;">
                <div style="font-size:2rem;font-weight:700;letter-spacing:1px;color:white;">Q2JSON Generator</div>
                <div style="font-size:1.1rem;font-weight:400;margin-top:0.2rem;color:white;">AI-to-LMS Educational Question Pipeline</div>
                <div style="font-size:0.95rem;font-weight:300;margin-top:0.2rem;color:white;">Institutional Edition &mdash; <span style="font-weight:500;">Faculty Use Only</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()