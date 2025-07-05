import streamlit as st
import json

def render_download_button(questions_data):
    if questions_data:
        download_clicked = st.download_button(
            label="⬇️ Download Validated JSON",
            data=json.dumps(questions_data, indent=2),
            file_name="q2json_validated_questions.json",
            mime="application/json",
            use_container_width=True
        )
        # Only set completion flag, do NOT auto-advance or rerun
        if download_clicked:
            st.session_state["human_review_downloaded"] = True
    else:
        st.warning("No validated data to download.")

def trigger_human_review_download(json_data, filename="questions.json"):
    """Download handler for Human Review & Editing stage."""
    import streamlit as st

    # Download button (existing logic)
    download_clicked = st.download_button(
        label="Download Validated Questions",
        data=json_data,
        file_name=filename,
        mime="application/json",
        key="human_review_download_btn"
    )

    # --- FIX: Set completion flag when download is triggered ---
    if download_clicked:
        st.session_state["human_review_downloaded"] = True  # <-- Completion flag for sidebar
        # (Optional) Advance stage here if desired, or keep as manual navigation

    return download_clicked

# Example fix for headers/banners in all stage render functions:
# filepath: c:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON\stages\stage_0_prompt.py
def render_prompt_builder():
    # ...existing code...
    show_stage_banner(st.session_state.current_stage + 1, total_stages=4)
    # ...existing code...

# filepath: c:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON\stages\stage_1_processing.py
def render_ai_processing():
    # ...existing code...
    show_stage_banner(st.session_state.current_stage + 1, total_stages=4)
    # ...existing code...

# filepath: c:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON\stages\stage_2_validation.py
def render_json_validation():
    # ...existing code...
    show_stage_banner(st.session_state.current_stage + 1, total_stages=4)
    # ...existing code...

# filepath: c:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON\stages\stage_3_human_review.py
def render_human_review():
    # ...existing code...
    show_stage_banner(st.session_state.current_stage + 1, total_stages=4)
    # ...existing code...

# Sidebar mapping fix:
# filepath: c:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON\utils\ui_helpers.py
def render_sidebar(current_stage):
    st.sidebar.markdown("## Workflow Progress")
    stages = [
        "Prompt Builder",
        "AI Processing",
        "Human Review and Editing",
        "Output"
    ]
    for idx, stage_name in enumerate(stages):
        display_number = idx + 1  # 1-based for display
        if idx < current_stage:
            st.sidebar.success(f"✅ Stage {display_number} of 4: {stage_name}\nCompleted successfully")
        elif idx == current_stage:
            st.sidebar.info(f"🟢 Stage {display_number} of 4: {stage_name}\nCurrently active")
        else:
            st.sidebar.warning(f"⏳ Stage {display_number} of 4: {stage_name}\nPending completion")

# Any other display components:
# Always use st.session_state.current_stage + 1 for user-facing stage numbers.