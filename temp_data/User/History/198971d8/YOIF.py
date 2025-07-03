# navigation/state.py
import streamlit as st
import time

def initialize_session_state():
    """Initialize required session state keys with defaults."""
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 0
    if "navigation_timestamp" not in st.session_state:
        st.session_state.navigation_timestamp = time.time()
    if "generated_prompt" not in st.session_state:
        st.session_state.generated_prompt = None
    if "raw_extracted_json" not in st.session_state:
        st.session_state.raw_extracted_json = None
    if "questions_data" not in st.session_state:
        st.session_state.questions_data = None
    if "processing_completed" not in st.session_state:
        st.session_state.processing_completed = False
    if "processing_steps" not in st.session_state:
        st.session_state.processing_steps = []
    if "edited_questions_data" not in st.session_state:
        st.session_state.edited_questions_data = None
    if "review_completed" not in st.session_state:
        st.session_state.review_completed = False
    if "validation_results" not in st.session_state:
        st.session_state.validation_results = None

def validate_session_state():
    """Ensure all required session state keys exist and stage is valid."""
    required_keys = [
        "current_stage",
        "navigation_timestamp", 
        "generated_prompt",
        "raw_extracted_json"
    ]
    
    for key in required_keys:
        if key not in st.session_state:
            st.session_state[key] = None if key != "current_stage" else 0
    
    stage = st.session_state.get("current_stage", 0)
    if not (0 <= stage <= 2):
        st.session_state.current_stage = 0
        st.error("Invalid stage detected. Resetting to Stage 0.")