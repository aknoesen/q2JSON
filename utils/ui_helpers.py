# utils/ui_helpers.py
import streamlit as st
from navigation.manager import NavigationManager

def load_css():
    """Load custom CSS for better styling"""
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stage-header {
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
    }
    
    .question-preview {
        background: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def create_sidebar():
    """Create the sidebar with progress and navigation"""
    # Map stage index to names
    stage_names = ["🎯 Prompt Builder", "🤖 AI Processing", "✅ JSON Validation"]
    
    # Sidebar as STATUS INDICATOR only
    st.sidebar.markdown("### 📍 Workflow Progress")

    for i, name in enumerate(stage_names):
        if i == st.session_state.current_stage:
            st.sidebar.markdown(f"**🔄 {name}**")  # Current stage (in progress)
        elif i < st.session_state.current_stage:
            st.sidebar.markdown(f"✅ {name}")       # Completed stages
        else:
            st.sidebar.markdown(f"⏳ {name}")       # Future stages

    # Add manual and debug navigation options to sidebar
    NavigationManager.create_manual_navigation()
    NavigationManager.create_debug_info()
    NavigationManager.create_emergency_reset()


def create_main_header():
    """Create the main application header"""
    st.title("📝 q2JSON Generator")
    st.markdown("*Convert AI Responses to Clean Educational JSON*")
    st.markdown("""
    Transform messy AI responses into perfectly formatted JSON questions ready for educational use.
    This tool bridges the gap between AI-generated content and educational deployment.
    """)