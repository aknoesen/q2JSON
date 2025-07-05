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
        # Auto-advance to Output stage after download
        if download_clicked:
            target_stage = 4  # Output is stage 4 in app.py routing
            st.write(f"DEBUG: Setting stage to {target_stage} after download")
            st.session_state.current_stage = target_stage
            st.rerun()
    else:
        st.warning("No validated data to download.")