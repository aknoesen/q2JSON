import streamlit as st

def render_latex_correction_examples(corrections_made, latex_examples):
    if corrections_made > 0 and latex_examples:
        st.markdown(
            """
            <div style="margin-top:1.5rem;">
                <h4 style="color:#764ba2;">LaTeX Correction Examples</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for ex in latex_examples[:2]:
            before = ex.get('before', '')
            after = ex.get('after', '')
            st.markdown(
                f"""
                <div style="background:#f8f9fa;border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
                    <b>Before:</b> <span style="color:#b22222;">{before}</span><br>
                    <b>After:</b> <span style="color:#228B22;">{after}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )