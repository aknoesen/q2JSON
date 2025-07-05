# stages/stage_4_output.py
import streamlit as st
from utils.ui_helpers import show_stage_banner

def render_output_completion():
    """Render the final Output/Completion stage"""
    show_stage_banner(4, total_stages=4)
    st.balloons()
    st.header("🎉 Workflow Complete!")
    st.success("All steps are finished. Your questions are ready for use!")
    st.markdown("""
    ## Project Summary
    - **Questions processed:** {questions_count}
    - **LaTeX corrections applied:** {latex_corrections}
    - **Download status:** ✅ Completed
    """)
    st.markdown("---")
    st.markdown("Thank you for using the Q2JSON Generator! You may now close this window or start a new project.")

    # Optionally, show more metrics or a restart button
    if st.button("Start New Project"):
        st.session_state.clear()
        st.rerun()

def get_completion_metrics():
    """Gather metrics for the completion summary"""
    questions_data = st.session_state.get("questions_data", {})
    questions_count = len(questions_data.get("questions", []))
    latex_corrections = st.session_state.get("latex_corrections", 0)
    return questions_count, latex_corrections

# Usage in app.py:
# from stages.stage_4_output import render_output_completion
# render_output_completion()
