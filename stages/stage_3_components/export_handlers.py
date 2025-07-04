"""
Export Handlers for Q2JSON Stage 3 Human Review
Manages data export and file generation functionality
"""

import streamlit as st
import json
import datetime

class ExportHandlers:
    """Handles export functionality and workflow completion"""
    
    def render_workflow_completion(self):
        """Render workflow completion section"""
        
        st.divider()
        st.subheader("🎯 Workflow Completion")
        
        # Check if any questions have been modified
        modified_count = len(st.session_state.get('modified_questions', set()))
        total_questions = len(st.session_state.get('questions_data', {}).get('questions', []))
        
        if modified_count > 0:
            st.success(f"✅ {modified_count} of {total_questions} questions have been reviewed and modified")
        else:
            st.info(f"📝 {total_questions} questions loaded - no modifications made yet")
        
        # Export options
        st.subheader("📤 Export Options")
        
        if st.button("📄 Export as JSON", key="export_json"):
            self.export_questions_json()
        
        # Next stage navigation
        st.divider()
        st.subheader("➡️ Next Stage")
        
        if st.button("🚀 Continue to Final Export", key="continue_to_export", type="primary"):
            st.session_state.current_stage = 3  # Move to stage 4
            st.rerun()
    
    def export_questions_json(self):
        """Export questions as JSON"""
        try:
            questions_data = st.session_state.get('questions_data', {})
            
            # Create export data
            export_data = {
                'questions': questions_data.get('questions', []),
                'metadata': {
                    'total_questions': len(questions_data.get('questions', [])),
                    'modified_questions': len(st.session_state.get('modified_questions', set())),
                    'export_timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'stage': 'Human Review & Editing'
                }
            }
            
            # Convert to JSON string
            json_string = json.dumps(export_data, indent=2)
            
            # Offer download
            st.download_button(
                label="💾 Download JSON File",
                data=json_string,
                file_name=f"questions_reviewed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.success("✅ JSON export ready for download")
            
        except Exception as e:
            st.error(f"❌ Error exporting JSON: {e}")
