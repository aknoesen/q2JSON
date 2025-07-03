# Q2JSON Stage 4 Integration Example
"""
Example implementation showing how to integrate Q2LMS extracted components
into Q2JSON Stage 4 (Question Review & Edit) interface.

This example demonstrates:
1. Setting up the components
2. Rendering questions with validation
3. Side-by-side editing with mathematical validation
4. Batch validation operations
5. Validation dashboard and reporting
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import json

# Import the extracted Q2LMS components
from extracted_components import (
    Q2JSONLaTeXProcessor,
    MathValidationManager,
    Q2JSONQuestionRenderer,
    Q2JSONEditorFramework,
    Q2JSONValidationManager
)


class Q2JSONStage4Interface:
    """
    Q2JSON Stage 4 interface using extracted Q2LMS components.
    
    Provides question review and editing with mathematical validation.
    """
    
    def __init__(self):
        # Initialize all components
        self.latex_processor = Q2JSONLaTeXProcessor()
        self.question_renderer = Q2JSONQuestionRenderer()
        self.validation_manager = Q2JSONValidationManager()
        self.editor_framework = Q2JSONEditorFramework(save_callback=self.save_question)
        
        # Configure Streamlit page
        self._configure_page()
    
    def _configure_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Q2JSON Stage 4 - Question Review & Edit",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply MathJax configuration for LaTeX rendering
        st.markdown("""
        <script>
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                packages: {'[+]': ['ams', 'color', 'cancel']}
            },
            svg: {fontCache: 'global'},
            options: {
                renderActions: {
                    addMenu: [0, '', '']
                }
            }
        };
        </script>
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        """, unsafe_allow_html=True)
        
        # Custom CSS for validation indicators
        st.markdown("""
        <style>
        .validation-critical {
            border-left: 4px solid #dc3545;
            padding-left: 10px;
            background-color: #f8d7da;
        }
        .validation-warning {
            border-left: 4px solid #ffc107;
            padding-left: 10px;
            background-color: #fff3cd;
        }
        .validation-info {
            border-left: 4px solid #17a2b8;
            padding-left: 10px;
            background-color: #d1ecf1;
        }
        .math-expression {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application interface"""
        st.title("🔍 Q2JSON Stage 4 - Question Review & Edit")
        st.markdown("*Enhanced with Q2LMS mathematical validation capabilities*")
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown("## 🧭 Navigation")
            mode = st.radio(
                "Select Mode",
                ["📊 Validation Dashboard", "📝 Question Review", "✏️ Question Editor", "🔬 Batch Validation"],
                help="Choose the interface mode"
            )
            
            st.markdown("---")
            st.markdown("## 📁 Data")
            
            # Sample data or file upload
            if st.button("🎲 Load Sample Data"):
                self._load_sample_data()
            
            uploaded_file = st.file_uploader(
                "Upload Questions JSON",
                type=['json'],
                help="Upload a JSON file with question data"
            )
            
            if uploaded_file:
                self._load_uploaded_data(uploaded_file)
        
        # Main interface based on selected mode
        if mode == "📊 Validation Dashboard":
            self._render_validation_dashboard()
        elif mode == "📝 Question Review":
            self._render_question_review()
        elif mode == "✏️ Question Editor":
            self._render_question_editor()
        elif mode == "🔬 Batch Validation":
            self._render_batch_validation()
    
    def _render_validation_dashboard(self):
        """Render the validation dashboard"""
        st.header("📊 Validation Dashboard")
        
        if 'questions_data' not in st.session_state:
            st.info("👆 Load sample data or upload a file to begin validation analysis")
            return
        
        questions_data = st.session_state.questions_data
        
        # Run batch validation if not already done
        if 'batch_validation_results' not in st.session_state:
            with st.spinner("🔄 Running comprehensive validation..."):
                batch_results = self.validation_manager.validate_question_batch(questions_data)
                st.session_state.batch_validation_results = batch_results
        
        # Render validation dashboard
        batch_results = st.session_state.batch_validation_results
        self.validation_manager.render_validation_dashboard(batch_results)
        
        # Show DataFrame with validation flags
        st.markdown("---")
        st.markdown("### 📋 Questions with Validation Status")
        
        # Create DataFrame with validation flags
        df = pd.DataFrame(questions_data)
        df_with_flags = self.validation_manager.add_validation_flags_to_dataframe(df, batch_results)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_critical = st.checkbox("🚨 Critical Issues", value=True)
        with col2:
            show_warnings = st.checkbox("⚠️ Warnings", value=True)
        with col3:
            show_valid = st.checkbox("✅ Valid Questions", value=True)
        
        # Apply filters
        filtered_df = self._apply_validation_filters(df_with_flags, show_critical, show_warnings, show_valid)
        
        # Display filtered results
        if len(filtered_df) > 0:
            st.dataframe(
                filtered_df[['title', 'question_type', 'overall_validation_status', 'validation_score', 'math_critical', 'math_warning']],
                use_container_width=True
            )
        else:
            st.info("No questions match the selected filters")
    
    def _render_question_review(self):
        """Render question review interface"""
        st.header("📝 Question Review")
        
        if 'questions_data' not in st.session_state:
            st.info("👆 Load sample data or upload a file to begin reviewing questions")
            return
        
        questions_data = st.session_state.questions_data
        
        # Question selector
        question_options = [f"Question {i+1}: {q.get('title', 'Untitled')}" for i, q in enumerate(questions_data)]
        selected_idx = st.selectbox("Select Question", range(len(questions_data)), format_func=lambda x: question_options[x])
        
        if selected_idx is not None:
            selected_question = questions_data[selected_idx]
            
            # Validate selected question
            validation_results = self.validation_manager.validate_question_comprehensive(selected_question, selected_idx)
            
            # Render question with validation
            self.question_renderer.render_question_with_validation(
                selected_question, 
                validation_results, 
                show_validation_indicators=True
            )
            
            # Show detailed validation results
            st.markdown("---")
            self.validation_manager.render_validation_dashboard(validation_results)
    
    def _render_question_editor(self):
        """Render question editor interface"""
        st.header("✏️ Question Editor")
        
        if 'questions_data' not in st.session_state:
            st.info("👆 Load sample data or upload a file to begin editing questions")
            return
        
        questions_data = st.session_state.questions_data
        
        # Question selector
        question_options = [f"Question {i+1}: {q.get('title', 'Untitled')}" for i, q in enumerate(questions_data)]
        selected_idx = st.selectbox("Select Question to Edit", range(len(questions_data)), format_func=lambda x: question_options[x])
        
        if selected_idx is not None:
            selected_question = questions_data[selected_idx]
            
            # Render side-by-side editor
            editor_result = self.editor_framework.render_side_by_side_editor(
                selected_question,
                selected_idx,
                session_prefix="q2json_stage4",
                show_validation=True
            )
            
            # Handle save result
            if editor_result.get('saved'):
                st.success("✅ Question saved successfully!")
                # Update the questions data
                st.session_state.questions_data[selected_idx] = editor_result['question_data']
                st.rerun()
    
    def _render_batch_validation(self):
        """Render batch validation interface"""
        st.header("🔬 Batch Validation")
        
        if 'questions_data' not in st.session_state:
            st.info("👆 Load sample data or upload a file to begin batch validation")
            return
        
        questions_data = st.session_state.questions_data
        df = pd.DataFrame(questions_data)
        
        # Validation controls
        self.validation_manager.render_validation_controls(df)
        
        # Run comprehensive batch validation
        if st.button("🚀 Run Complete Validation Analysis", type="primary"):
            with st.spinner("🔄 Running comprehensive validation on all questions..."):
                batch_results = self.validation_manager.validate_question_batch(questions_data)
                st.session_state.batch_validation_results = batch_results
                
                # Show results
                self.validation_manager.render_validation_dashboard(batch_results)
                
                # Offer to download results
                results_json = json.dumps(batch_results, indent=2, default=str)
                st.download_button(
                    "📥 Download Validation Report",
                    data=results_json,
                    file_name=f"q2json_validation_report_{batch_results['timestamp'][:10]}.json",
                    mime="application/json"
                )
    
    def _load_sample_data(self):
        """Load sample question data"""
        sample_questions = [
            {
                "title": "Electrical Circuit Analysis",
                "question_text": "Calculate the total resistance when $R_1 = 10\\,\\Omega$ and $R_2 = 15\\,\\Omega$ are connected in series.",
                "question_type": "numerical",
                "correct_answer": "$25\\,\\Omega$",
                "points": 2,
                "difficulty": "Medium",
                "topic": "Electrical Engineering",
                "subtopic": "Circuit Analysis"
            },
            {
                "title": "Mathematical Expression",
                "question_text": "What is the result of $\\frac{\\pi}{2} \\times \\sin(30°)$?",
                "question_type": "multiple_choice",
                "choice_a": "$\\frac{\\pi}{4}$",
                "choice_b": "$\\frac{\\pi}{2}$",
                "choice_c": "$\\pi$",
                "choice_d": "$2\\pi$",
                "correct_answer": "A",
                "points": 1,
                "difficulty": "Easy",
                "topic": "Mathematics",
                "subtopic": "Trigonometry"
            },
            {
                "title": "Physics Problem - Missing LaTeX",
                "question_text": "If force F = 10 N and acceleration a = 2 m/s², what is the mass?",  # Note: missing LaTeX formatting
                "question_type": "numerical",
                "correct_answer": "5 kg",  # Note: missing LaTeX formatting
                "points": 2,
                "difficulty": "Medium",
                "topic": "Physics",
                "subtopic": "Mechanics"
            },
            {
                "title": "Chemistry - Unicode Issues",
                "question_text": "What is the molar mass of H₂SO₄?",  # Note: Unicode subscripts
                "question_type": "numerical",
                "correct_answer": "98 g/mol",
                "points": 1,
                "difficulty": "Easy",
                "topic": "Chemistry",
                "subtopic": "Stoichiometry"
            }
        ]
        
        st.session_state.questions_data = sample_questions
        st.success("✅ Sample data loaded! This includes questions with various mathematical formatting issues for demonstration.")
    
    def _load_uploaded_data(self, uploaded_file):
        """Load data from uploaded file"""
        try:
            data = json.load(uploaded_file)
            
            # Handle different JSON structures
            if isinstance(data, list):
                questions_data = data
            elif isinstance(data, dict) and 'questions' in data:
                questions_data = data['questions']
            else:
                st.error("❌ Invalid JSON structure. Expected a list of questions or an object with 'questions' key.")
                return
            
            st.session_state.questions_data = questions_data
            st.success(f"✅ Loaded {len(questions_data)} questions from uploaded file")
            
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON file: {e}")
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
    
    def _apply_validation_filters(self, df: pd.DataFrame, show_critical: bool, show_warnings: bool, show_valid: bool) -> pd.DataFrame:
        """Apply validation status filters to DataFrame"""
        mask = pd.Series([False] * len(df))
        
        if show_critical:
            mask |= (df['overall_validation_status'] == 'critical')
        if show_warnings:
            mask |= (df['overall_validation_status'] == 'warning')
        if show_valid:
            mask |= (df['overall_validation_status'] == 'valid')
        
        return df[mask]
    
    def save_question(self, question_index: int, question_data: Dict[str, Any]) -> bool:
        """Save callback for editor framework"""
        try:
            # Update the question in session state
            if 'questions_data' in st.session_state:
                st.session_state.questions_data[question_index] = question_data
            
            # Here you would typically save to a database or file
            st.info(f"💾 Saved question {question_index + 1}: {question_data.get('title', 'Untitled')}")
            return True
            
        except Exception as e:
            st.error(f"❌ Error saving question: {e}")
            return False


def main():
    """Main entry point"""
    app = Q2JSONStage4Interface()
    app.run()


if __name__ == "__main__":
    main()
