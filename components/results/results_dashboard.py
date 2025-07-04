import streamlit as st

def render_results_metrics(total_questions, corrections_made, math_valid, math_invalid):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total Questions",
            value=total_questions,
            help="Number of questions processed in this session."
        )
    with col2:
        st.metric(
            label="LaTeX Corrections",
            value=corrections_made,
            help="Number of LaTeX issues automatically corrected."
        )
    with col3:
        st.metric(
            label="Math Consistency",
            value=f"{math_valid} ✅ / {math_invalid} ❌",
            help="Questions passing/failing mathematical validation."
        )