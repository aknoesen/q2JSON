import streamlit as st
import json

def render_download_button(questions_data):
    if questions_data:
        st.download_button(
            label="⬇️ Download Validated JSON",
            data=json.dumps(questions_data, indent=2),
            file_name="q2json_validated_questions.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.warning("No validated data to download.")