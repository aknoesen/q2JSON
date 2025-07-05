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
    
    /* Stage indicator styles */
    .stage-current {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        border-left: 4px solid #198754;
        box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
        animation: pulse 2s infinite;
    }
    
    .stage-completed {
        background: linear-gradient(135deg, #6f42c1, #8f63d4);
        color: white;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        border-left: 4px solid #5a2d91;
        box-shadow: 0 2px 4px rgba(111, 66, 193, 0.3);
    }
    
    .stage-pending {
        background: linear-gradient(135deg, #6c757d, #868e96);
        color: white;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        border-left: 4px solid #495057;
        opacity: 0.7;
    }
    
    .stage-progress-bar {
        height: 4px;
        background: #e9ecef;
        border-radius: 2px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .stage-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #28a745, #20c997);
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
        }
        50% {
            box-shadow: 0 4px 8px rgba(40, 167, 69, 0.6);
        }
        100% {
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
        }
    }
    </style>
    """, unsafe_allow_html=True)


def create_sidebar():
    """Create the sidebar with enhanced visual progress indicators"""
    st.sidebar.image("assets/json2lms_logo.svg", width=600)
    # Map stage index to names and icons
    stage_data = [
        {"name": "Prompt Builder", "icon": "🎯", "desc": "Create AI prompts"},
        {"name": "AI Processing", "icon": "🤖", "desc": "Process AI responses"}, 
        {"name": "Human Review and Editing", "icon": "📝", "desc": "Manual review and editing"},
        {"name": "Output", "icon": "📤", "desc": "Export and download output"}
    ]
    
    current_stage = st.session_state.current_stage
    
    # Sidebar header with overall progress
    st.sidebar.markdown("### 📍 Workflow Progress")
    
    # Get correct user stage mapping for progress calculation
    user_stage, total_stages = get_user_stage_display(current_stage)
    
    # Overall progress bar
    progress_percentage = (user_stage / total_stages) * 100
    st.sidebar.markdown(f"""
    <div class="stage-progress-bar">
        <div class="stage-progress-fill" style="width: {progress_percentage}%;"></div>
    </div>
    <small style="color: #6c757d;">Stage {user_stage} of {total_stages} ({progress_percentage:.0f}% complete)</small>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Get the active stage index using the mapping function
    active_stage_idx = user_stage - 1  # Convert back to 0-based for comparison
    
    # Individual stage indicators with enhanced visuals
    for i, stage in enumerate(stage_data):
        if i == active_stage_idx:
            # Current stage - green with animation
            st.sidebar.markdown(f"""
            <div class="stage-current">
                <strong>{stage['icon']} {stage['name']}</strong><br>
                <small>🔄 Currently active</small><br>
                <small style="opacity: 0.8;">{stage['desc']}</small>
            </div>
            """, unsafe_allow_html=True)
        elif i < active_stage_idx:
            # Completed stages - purple/blue 
            st.sidebar.markdown(f"""
            <div class="stage-completed">
                <strong>✅ {stage['name']}</strong><br>
                <small>Completed successfully</small><br>
                <small style="opacity: 0.8;">{stage['desc']}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Future stages - gray
            st.sidebar.markdown(f"""
            <div class="stage-pending">
                <strong>⏳ {stage['name']}</strong><br>
                <small>Pending completion</small><br>
                <small style="opacity: 0.8;">{stage['desc']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")

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

def show_stage_banner(current_stage, total_stages=4):
    # Use the mapping function for all banners
    user_stage, total_stages = get_user_stage_display(current_stage)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #1f77b4 0%, #764ba2 100%);
            padding: 1rem 0;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
        ">
            Stage {user_stage} of {total_stages}
        </div>
        """,
        unsafe_allow_html=True,
    )

def get_user_stage_display(current_stage):
    """Map internal stages to 4 user-facing stages"""
    if current_stage == 0:
        return (1, 4)  # "Stage 1 of 4: Prompt Builder"
    elif current_stage == 1 or current_stage == 2:
        return (2, 4)  # "Stage 2 of 4: AI Processing" (validation is internal)
    elif current_stage == 3:
        return (3, 4)  # "Stage 3 of 4: Human Review"
    elif current_stage == 4:
        return (4, 4)  # "Stage 4 of 4: Output"
    else:
        return (1, 4)  # Fallback

def render_sidebar(current_stage):
    st.sidebar.markdown("## Workflow Progress")
    stages = [
        "Prompt Builder",
        "AI Processing",
        "Human Review and Editing",
        "Output"
    ]
    
    # Get correct user stage mapping
    user_stage, total_stages = get_user_stage_display(current_stage)
    
    # FIXED LOGIC: Use correct comparison for highlighting
    for idx, stage_name in enumerate(stages):
        display_number = idx + 1  # 1-based for display
        
        # Convert user_stage back to 0-based index for comparison with idx
        active_stage_idx = user_stage - 1
        
        if idx < active_stage_idx:
            st.sidebar.success(f"✅ Stage {display_number} of {total_stages}: {stage_name}\nCompleted successfully")
        elif idx == active_stage_idx:
            st.sidebar.info(f"🟢 Stage {display_number} of {total_stages}: {stage_name}\nCurrently active")
        else:
            st.sidebar.warning(f"⏳ Stage {display_number} of {total_stages}: {stage_name}\nPending completion")