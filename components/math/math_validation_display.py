import streamlit as st

def render_math_validation(math_results):
    math_valid = math_results.get('valid', 0)
    math_invalid = math_results.get('invalid', 0)
    st.markdown(
        """
        <div style="margin-top:1.5rem;">
            <h4 style="color:#764ba2;">Mathematical Validation</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if math_invalid > 0:
        st.error(f"{math_invalid} question(s) failed mathematical consistency checks.")
    else:
        st.success("All questions passed mathematical validation.")