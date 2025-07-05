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
        # Auto-advance to Stage 4 after download
        if download_clicked:
            st.session_state.current_stage = 3  # Stage 4 (0-based index)
            st.experimental_rerun()
    else:
        st.warning("No validated data to download.")