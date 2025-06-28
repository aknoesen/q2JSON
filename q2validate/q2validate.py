#!/usr/bin/env python3
"""
q2validate - JSON Validation Tool for Q2LMS
Main Streamlit application for validating q2prompt output
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import io

# Import our modules
from modules.q2lms_adapter import Q2LMSAdapter
from modules.unicode_converter import get_unicode_converter
from modules.schema_validator import JSONSchemaValidator

def init_session_state():
    """Initialize session state variables"""
    if 'questions_data' not in st.session_state:
        st.session_state.questions_data = None
    if 'processed_questions' not in st.session_state:
        st.session_state.processed_questions = None
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None

def validate_and_process_questions(questions: List[Dict[str, Any]], auto_fix_unicode: bool = True):
    """Validate and process questions"""
    
    # Initialize components
    validator = JSONSchemaValidator()
    converter = get_unicode_converter()
    
    results = {
        'total_questions': len(questions),
        'schema_valid': 0,
        'unicode_issues': 0,
        'auto_fixed': 0,
        'ready_for_q2lms': 0,
        'question_results': []
    }
    
    processed_questions = []
    
    for i, question in enumerate(questions):
        # Schema validation
        is_schema_valid, schema_errors = validator.validate_question_schema(question)
        
        # Unicode detection
        unicode_issues = converter.detect_issues(question)
        has_unicode = len(unicode_issues) > 0
        
        # Auto-fix Unicode if requested and available
        final_question = question.copy()
        conversion_report = {}
        
        if auto_fix_unicode and has_unicode and hasattr(converter, 'convert_question'):
            final_question, conversion_report = converter.convert_question(question)
            # Re-check after conversion
            remaining_unicode = converter.detect_issues(final_question)
            has_unicode_after = len(remaining_unicode) > 0
        else:
            has_unicode_after = has_unicode
            conversion_report = {'conversion_successful': not has_unicode}
        
        # Update counters
        if is_schema_valid:
            results['schema_valid'] += 1
        if has_unicode:
            results['unicode_issues'] += 1
        if auto_fix_unicode and conversion_report.get('conversion_successful', False):
            results['auto_fixed'] += 1
        if is_schema_valid and not has_unicode_after:
            results['ready_for_q2lms'] += 1
        
        # Store individual results
        question_result = {
            'index': i,
            'title': question.get('title', f'Question {i+1}'),
            'schema_valid': is_schema_valid,
            'schema_errors': schema_errors,
            'had_unicode': has_unicode,
            'has_unicode_after': has_unicode_after,
            'unicode_issues': unicode_issues,
            'conversion_report': conversion_report,
            'ready_for_q2lms': is_schema_valid and not has_unicode_after
        }
        
        results['question_results'].append(question_result)
        processed_questions.append(final_question)
    
    return processed_questions, results

def display_validation_dashboard(results: Dict[str, Any]):
    """Display validation results dashboard"""
    
    st.markdown("### 📊 Validation Results")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", results['total_questions'])
    
    with col2:
        st.metric(
            "Schema Valid", 
            results['schema_valid'],
            delta=f"{(results['schema_valid']/results['total_questions']*100):.0f}%" if results['total_questions'] > 0 else "0%"
        )
    
    with col3:
        st.metric(
            "Unicode Issues", 
            results['unicode_issues'],
            delta=f"-{results['auto_fixed']} fixed" if results['auto_fixed'] > 0 else None
        )
    
    with col4:
        st.metric(
            "Ready for Q2LMS", 
            results['ready_for_q2lms'],
            delta=f"{(results['ready_for_q2lms']/results['total_questions']*100):.0f}%" if results['total_questions'] > 0 else "0%"
        )
    
    # Status breakdown
    if results['ready_for_q2lms'] == results['total_questions']:
        st.success("🎉 All questions are valid and ready for Q2LMS!")
    elif results['ready_for_q2lms'] > 0:
        st.info(f"✅ {results['ready_for_q2lms']} questions ready, {results['total_questions'] - results['ready_for_q2lms']} need attention")
    else:
        st.warning("⚠️ No questions are ready for Q2LMS. Please review issues below.")

def display_question_details(questions: List[Dict[str, Any]], results: Dict[str, Any], q2lms_adapter: Q2LMSAdapter):
    """Display detailed question review"""
    
    st.markdown("### 🔍 Question Review")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_filter = st.selectbox(
            "Show:", 
            ["All Questions", "Ready for Q2LMS", "Has Issues", "Schema Errors", "Unicode Issues"]
        )
    
    with col2:
        questions_per_page = st.selectbox("Questions per page:", [5, 10, 20], index=1)
    
    with col3:
        show_preview = st.checkbox("Show Preview", value=True)
    
    # Filter questions based on selection
    filtered_indices = []
    for i, result in enumerate(results['question_results']):
        if show_filter == "All Questions":
            filtered_indices.append(i)
        elif show_filter == "Ready for Q2LMS" and result['ready_for_q2lms']:
            filtered_indices.append(i)
        elif show_filter == "Has Issues" and not result['ready_for_q2lms']:
            filtered_indices.append(i)
        elif show_filter == "Schema Errors" and not result['schema_valid']:
            filtered_indices.append(i)
        elif show_filter == "Unicode Issues" and (result['had_unicode'] or result['has_unicode_after']):
            filtered_indices.append(i)
    
    if not filtered_indices:
        st.info(f"No questions match the filter: {show_filter}")
        return
    
    # Pagination
    total_pages = (len(filtered_indices) - 1) // questions_per_page + 1
    
    if total_pages > 1:
        page = st.selectbox(f"Page (showing {len(filtered_indices)} questions):", range(1, total_pages + 1))
        start_idx = (page - 1) * questions_per_page
        end_idx = min(start_idx + questions_per_page, len(filtered_indices))
        page_indices = filtered_indices[start_idx:end_idx]
    else:
        page_indices = filtered_indices
    
    # Display questions
    for idx in page_indices:
        question = questions[idx]
        result = results['question_results'][idx]
        
        # Question header
        with st.expander(f"Question {idx + 1}: {result['title']}", expanded=False):
            
            # Status indicators
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if result['schema_valid']:
                    st.success("✅ Schema Valid")
                else:
                    st.error("❌ Schema Invalid")
            
            with col2:
                if not result['has_unicode_after']:
                    st.success("✅ No Unicode Issues")
                elif result['had_unicode'] and not result['has_unicode_after']:
                    st.success("🔧 Unicode Fixed")
                else:
                    st.warning("⚠️ Unicode Issues")
            
            with col3:
                if result['ready_for_q2lms']:
                    st.success("✅ Ready for Q2LMS")
                else:
                    st.error("❌ Needs Attention")
            
            # Show issues if any
            if result['schema_errors']:
                st.error("**Schema Errors:**")
                for error in result['schema_errors']:
                    st.write(f"• {error}")
            
            if result['unicode_issues']:
                st.warning("**Unicode Characters Found:**")
                for field, chars in result['unicode_issues'].items():
                    st.write(f"• **{field}**: {', '.join(chars)}")
            
            if result['conversion_report'].get('conversion_successful'):
                st.info("🔧 Unicode characters were automatically converted to LaTeX")
            
            # Show preview if requested
            if show_preview:
                st.markdown("**Preview:**")
                q2lms_adapter.preview_question(question)
            
            # Raw JSON option
            if st.checkbox(f"Show Raw JSON", key=f"raw_json_{idx}"):
                st.json(question)

def create_export_data(questions: List[Dict[str, Any]], results: Dict[str, Any]) -> Dict[str, Any]:
    """Create export data structure"""
    
    export_data = {
        'questions': questions,
        'metadata': {
            'processed_by': 'q2validate',
            'processing_date': datetime.now().isoformat(),
            'validation_results': {
                'total_questions': results['total_questions'],
                'schema_valid': results['schema_valid'],
                'unicode_issues_found': results['unicode_issues'],
                'unicode_issues_fixed': results['auto_fixed'],
                'ready_for_q2lms': results['ready_for_q2lms']
            },
            'format_version': '1.0'
        }
    }
    
    return export_data

def main():
    st.set_page_config(
        page_title="q2validate",
        page_icon="🔍",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🔍 q2validate - JSON Validation Tool")
    st.markdown("**Validate q2prompt output before Q2LMS import**")
    
    # Initialize components
    q2lms_adapter = Q2LMSAdapter()
    unicode_converter = get_unicode_converter()
    
    # Sidebar controls
    with st.sidebar:
        st.header("📁 Input Options")
        
        input_method = st.radio(
            "Choose input method:",
            ["Upload JSON File", "Paste JSON Text"]
        )
        
        st.header("🔧 Processing Options")
        auto_fix_unicode = st.checkbox("Auto-fix Unicode → LaTeX", value=True)
        
        st.header("📊 Component Status")
        st.success("✅ Q2LMS Adapter: Ready")
        
        if hasattr(unicode_converter, 'is_available') and unicode_converter.is_available():
            st.success("✅ Unicode Converter: Ready")
        else:
            st.warning("⚠️ Unicode Converter: Detection Only")
    
    # Main input area
    questions_data = None
    
    if input_method == "Upload JSON File":
        uploaded_file = st.file_uploader(
            "Choose JSON file from q2prompt",
            type=['json'],
            help="Upload the JSON file generated by q2prompt"
        )
        
        if uploaded_file is not None:
            try:
                questions_data = json.load(uploaded_file)
                st.success(f"✅ File loaded: {uploaded_file.name}")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
                return
    
    else:  # Paste JSON Text
        json_text = st.text_area(
            "Paste JSON from q2prompt:",
            height=200,
            placeholder='{"questions": [{"type": "multiple_choice", ...}]}',
            help="Paste the JSON output from q2prompt here"
        )
        
        if json_text.strip():
            try:
                questions_data = json.loads(json_text)
                st.success("✅ JSON parsed successfully")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
                return
    
    # Process questions if data loaded
    if questions_data is not None:
        # Handle different JSON structures
        if isinstance(questions_data, dict) and 'questions' in questions_data:
            questions = questions_data['questions']
        elif isinstance(questions_data, list):
            questions = questions_data
        else:
            st.error("❌ Unexpected JSON structure. Expected {'questions': [...]} or [...]")
            return
        
        if not questions:
            st.warning("⚠️ No questions found in JSON")
            return
        
        # Process questions
        with st.spinner("🔄 Validating questions..."):
            processed_questions, validation_results = validate_and_process_questions(
                questions, auto_fix_unicode
            )
        
        # Store in session state
        st.session_state.processed_questions = processed_questions
        st.session_state.validation_results = validation_results
        
        # Display results
        display_validation_dashboard(validation_results)
        
        st.markdown("---")
        
        # Question details
        display_question_details(processed_questions, validation_results, q2lms_adapter)
        
        # Export section
        st.markdown("---")
        st.markdown("### 📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export All Questions", type="primary"):
                export_data = create_export_data(processed_questions, validation_results)
                json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"q2validate_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📥 Export Ready Questions Only"):
                ready_questions = [
                    processed_questions[i] for i, result in enumerate(validation_results['question_results'])
                    if result['ready_for_q2lms']
                ]
                
                if ready_questions:
                    export_data = create_export_data(ready_questions, validation_results)
                    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="📥 Download Ready Questions",
                        data=json_str,
                        file_name=f"q2validate_ready_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No questions are ready for export")
        
        with col3:
            if st.button("📋 Copy JSON to Clipboard"):
                export_data = create_export_data(processed_questions, validation_results)
                json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                st.code(json_str, language='json')

if __name__ == "__main__":
    main()
