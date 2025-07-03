# Q2JSON Stage 4 Complete Interface Example
"""
Q2JSON Stage 4 Integration Example - Complete Streamlit Application

This demonstrates how to use the extracted Q2JSON components together
to create a comprehensive question authoring and editing interface.

Features:
- Question import/export
- Side-by-side editing with live preview
- Mathematical notation support
- Comprehensive validation
- Multiple preview modes
- Batch operations
"""

import streamlit as st
import json
import io
import zipfile
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64

# Import the extracted Q2JSON components
try:
    from .latex_processor import Q2JSONLaTeXProcessor
    from .question_renderer import Q2JSONQuestionRenderer
    from .editor_framework import Q2JSONEditorFramework
    from .validation_manager import Q2JSONValidationManager
except ImportError:
    from latex_processor import Q2JSONLaTeXProcessor
    from question_renderer import Q2JSONQuestionRenderer
    from editor_framework import Q2JSONEditorFramework
    from validation_manager import Q2JSONValidationManager


class Q2JSONStage4Application:
    """
    Complete Q2JSON Stage 4 application using extracted components.
    
    This class demonstrates the integration of all Q2JSON components
    to create a full-featured question authoring environment.
    """
    
    def __init__(self):
        """Initialize the application with all components."""
        self.latex_processor = Q2JSONLaTeXProcessor()
        self.question_renderer = Q2JSONQuestionRenderer(self.latex_processor)
        self.editor_framework = Q2JSONEditorFramework(
            self.latex_processor,
            self.question_renderer,
            Q2JSONValidationManager(self.latex_processor)
        )
        self.validation_manager = Q2JSONValidationManager(self.latex_processor)
        
        # Application state
        self.current_questions = []
        self.app_mode = 'editor'
    
    def run(self):
        """Run the complete Q2JSON Stage 4 application."""
        self._setup_page_config()
        self._render_header()
        self._render_sidebar()
        
        # Main content based on selected mode
        if self.app_mode == 'editor':
            self._render_editor_mode()
        elif self.app_mode == 'import':
            self._render_import_mode()
        elif self.app_mode == 'validation':
            self._render_validation_mode()
        elif self.app_mode == 'preview':
            self._render_preview_mode()
        elif self.app_mode == 'export':
            self._render_export_mode()
        elif self.app_mode == 'demo':
            self._render_demo_mode()
    
    def _setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Q2JSON Stage 4 - Question Authoring Suite",
            page_icon="📝",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
        }
        .q2json-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        .q2json-stats {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render the application header."""
        st.markdown("""
        <div class="q2json-header">
            <h1>🎓 Q2JSON Stage 4 - Question Authoring Suite</h1>
            <p>Complete question authoring environment with LaTeX support, validation, and QTI compliance</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Render the sidebar navigation."""
        with st.sidebar:
            st.title("🧭 Navigation")
            
            # Mode selection
            modes = {
                'editor': '✏️ Question Editor',
                'import': '📥 Import Questions',
                'validation': '✅ Validation Center',
                'preview': '👁️ Preview Mode',
                'export': '📤 Export Questions',
                'demo': '🎯 Demo & Examples'
            }
            
            self.app_mode = st.selectbox(
                "Select Mode",
                options=list(modes.keys()),
                format_func=lambda x: modes[x],
                index=0
            )
            
            st.divider()
            
            # Application statistics
            self._render_sidebar_stats()
            
            st.divider()
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            
            if st.button("📂 Load Sample Questions"):
                self._load_sample_questions()
            
            if st.button("🧹 Clear All Questions"):
                if st.session_state.get('confirm_clear', False):
                    self._clear_all_questions()
                    st.session_state.confirm_clear = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm clearing all questions")
            
            if st.button("💾 Save Session"):
                self._save_session()
            
            st.divider()
            
            # Component information
            self._render_component_info()
    
    def _render_sidebar_stats(self):
        """Render statistics in sidebar."""
        questions = self._get_current_questions()
        
        st.markdown("### 📊 Current Session")
        st.metric("Total Questions", len(questions))
        
        if questions:
            # Validation stats
            valid_count = 0
            total_issues = 0
            
            for question in questions:
                result = self.validation_manager.validate_question(question)
                if result.is_valid:
                    valid_count += 1
                total_issues += len(result.issues)
            
            st.metric("Valid Questions", valid_count)
            st.metric("Total Issues", total_issues)
            
            # Question types
            type_counts = {}
            for question in questions:
                q_type = question.get('type', 'unknown')
                type_counts[q_type] = type_counts.get(q_type, 0) + 1
            
            if type_counts:
                st.markdown("**Question Types:**")
                for q_type, count in type_counts.items():
                    st.write(f"- {q_type}: {count}")
    
    def _render_component_info(self):
        """Render component information."""
        st.markdown("### 🔧 Components")
        
        with st.expander("Component Status"):
            components = [
                ("LaTeX Processor", "✅ Active"),
                ("Question Renderer", "✅ Active"),
                ("Editor Framework", "✅ Active"),
                ("Validation Manager", "✅ Active")
            ]
            
            for component, status in components:
                st.write(f"**{component}**: {status}")
    
    def _render_editor_mode(self):
        """Render the main editor interface."""
        st.header("✏️ Question Editor")
        
        questions = self._get_current_questions()
        
        if not questions:
            st.info("No questions loaded. Import questions or create new ones to get started.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Create New Question"):
                    self._create_new_question()
            
            with col2:
                if st.button("📂 Load Sample Questions"):
                    self._load_sample_questions()
        
        else:
            # Use the editor framework
            updated_questions = self.editor_framework.create_editor_interface(
                questions,
                title="",  # Header already rendered
                allow_batch_ops=True
            )
            
            # Update session state
            self._update_current_questions(updated_questions)
    
    def _render_import_mode(self):
        """Render the import interface."""
        st.header("📥 Import Questions")
        
        import_method = st.selectbox(
            "Import Method",
            ["Upload JSON File", "Paste JSON Text", "Import from URL", "Convert from Other Formats"]
        )
        
        if import_method == "Upload JSON File":
            self._render_file_upload()
        elif import_method == "Paste JSON Text":
            self._render_text_import()
        elif import_method == "Import from URL":
            self._render_url_import()
        elif import_method == "Convert from Other Formats":
            self._render_format_conversion()
    
    def _render_validation_mode(self):
        """Render the validation center."""
        st.header("✅ Validation Center")
        
        questions = self._get_current_questions()
        
        if not questions:
            st.info("No questions to validate. Import or create questions first.")
            return
        
        # Validation options
        col1, col2 = st.columns(2)
        
        with col1:
            validation_scope = st.selectbox(
                "Validation Scope",
                ["All Questions", "Selected Questions", "Current Question"]
            )
        
        with col2:
            validation_level = st.selectbox(
                "Validation Level",
                ["Standard", "Strict", "QTI Compliance Only", "Custom"]
            )
        
        # Run validation
        if st.button("🔍 Run Validation"):
            with st.spinner("Validating questions..."):
                if validation_scope == "All Questions":
                    results = self.validation_manager.validate_question_set(questions)
                    self._display_validation_results(results)
                else:
                    st.info("Individual validation not implemented in this demo")
        
        # Auto-fix suggestions
        st.subheader("🔧 Auto-Fix Suggestions")
        
        if questions:
            question_to_fix = st.selectbox(
                "Select Question to Fix",
                range(len(questions)),
                format_func=lambda x: f"Question {x + 1}"
            )
            
            suggestions = self.validation_manager.get_auto_fix_suggestions(questions[question_to_fix])
            
            if suggestions:
                st.write("**Available Auto-Fixes:**")
                for suggestion in suggestions:
                    st.write(f"- **{suggestion['field']}**: {suggestion['suggestion']}")
                
                if st.button("Apply Auto-Fixes"):
                    fixed_question = self.validation_manager.apply_auto_fixes(questions[question_to_fix])
                    questions[question_to_fix] = fixed_question
                    self._update_current_questions(questions)
                    st.success("Auto-fixes applied!")
                    st.rerun()
            else:
                st.info("No auto-fixes available for this question")
    
    def _render_preview_mode(self):
        """Render the preview interface."""
        st.header("👁️ Preview Mode")
        
        questions = self._get_current_questions()
        
        if not questions:
            st.info("No questions to preview. Import or create questions first.")
            return
        
        # Preview options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            preview_mode = st.selectbox(
                "Preview Mode",
                ["Student View", "Instructor View", "Answer Key", "Validation Mode"]
            )
        
        with col2:
            question_to_preview = st.selectbox(
                "Question",
                range(len(questions)),
                format_func=lambda x: f"Question {x + 1}"
            )
        
        with col3:
            render_all = st.checkbox("Show All Questions", value=False)
        
        # Render preview
        mode_settings = {
            "Student View": {'show_answers': False, 'show_feedback': False, 'show_validation': False},
            "Instructor View": {'show_answers': True, 'show_feedback': True, 'show_validation': True},
            "Answer Key": {'show_answers': True, 'show_feedback': False, 'show_validation': False},
            "Validation Mode": {'show_answers': False, 'show_feedback': False, 'show_validation': True}
        }
        
        settings = mode_settings[preview_mode]
        
        if render_all:
            # Render all questions
            for i, question in enumerate(questions):
                with st.expander(f"Question {i + 1}", expanded=i == 0):
                    html_content = self.question_renderer.render_question(
                        question,
                        question_number=i + 1,
                        **settings
                    )
                    st.components.v1.html(html_content, height=400, scrolling=True)
        else:
            # Render single question
            question = questions[question_to_preview]
            html_content = self.question_renderer.render_question(
                question,
                question_number=question_to_preview + 1,
                **settings
            )
            st.components.v1.html(html_content, height=600, scrolling=True)
    
    def _render_export_mode(self):
        """Render the export interface."""
        st.header("📤 Export Questions")
        
        questions = self._get_current_questions()
        
        if not questions:
            st.info("No questions to export. Import or create questions first.")
            return
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Export Format",
                ["JSON", "QTI 2.1", "CSV", "GIFT", "Moodle XML"]
            )
        
        with col2:
            include_validation = st.checkbox("Include Validation Report", value=True)
        
        # Question selection
        st.subheader("Select Questions to Export")
        
        export_all = st.checkbox("Export All Questions", value=True)
        
        if not export_all:
            selected_questions = []
            for i, question in enumerate(questions):
                title = question.get('title', f'Question {i + 1}')
                if st.checkbox(f"{i + 1}: {title}", key=f"export_{i}"):
                    selected_questions.append(i)
        else:
            selected_questions = list(range(len(questions)))
        
        # Export preview
        if selected_questions:
            st.info(f"Selected {len(selected_questions)} question(s) for export")
            
            if st.button("📥 Generate Export"):
                export_data = self._generate_export(
                    [questions[i] for i in selected_questions],
                    export_format,
                    include_validation
                )
                
                # Provide download
                if export_format == "JSON":
                    st.download_button(
                        "Download JSON",
                        export_data,
                        f"q2json_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json"
                    )
                else:
                    st.download_button(
                        f"Download {export_format}",
                        export_data,
                        f"q2json_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        "text/plain"
                    )
    
    def _render_demo_mode(self):
        """Render demo and examples."""
        st.header("🎯 Demo & Examples")
        
        demo_tabs = st.tabs([
            "🎓 Getting Started",
            "📚 Sample Questions",
            "🧮 LaTeX Examples",
            "🔧 Component Demo",
            "📋 Templates"
        ])
        
        with demo_tabs[0]:
            self._render_getting_started()
        
        with demo_tabs[1]:
            self._render_sample_questions()
        
        with demo_tabs[2]:
            self._render_latex_examples()
        
        with demo_tabs[3]:
            self._render_component_demo()
        
        with demo_tabs[4]:
            self._render_templates()
    
    def _render_getting_started(self):
        """Render getting started guide."""
        st.markdown("""
        ## Welcome to Q2JSON Stage 4! 🎉
        
        This application demonstrates the complete integration of Q2JSON components
        extracted and enhanced from the Q2LMS codebase.
        
        ### Features:
        
        - **✏️ Question Editor**: Full-featured editor with side-by-side preview
        - **🧮 LaTeX Support**: Complete mathematical notation support
        - **✅ Validation**: Comprehensive validation with auto-fix suggestions
        - **📤 Export**: Multiple export formats including QTI compliance
        - **🎨 Rich Rendering**: Beautiful question rendering with multiple view modes
        
        ### Quick Start:
        
        1. **Create Questions**: Use the Question Editor to create new questions
        2. **Import Data**: Upload existing JSON files or paste content
        3. **Validate**: Check question quality and compliance
        4. **Preview**: View questions as students or instructors would see them
        5. **Export**: Generate files for use in LMS platforms
        
        ### Components:
        
        - **LaTeX Processor**: Handles mathematical notation and formula rendering
        - **Question Renderer**: Displays questions with proper formatting
        - **Editor Framework**: Provides the editing interface
        - **Validation Manager**: Ensures question quality and compliance
        """)
        
        if st.button("🚀 Load Sample Questions to Get Started"):
            self._load_sample_questions()
            st.success("Sample questions loaded! Switch to Editor mode to see them.")
    
    def _render_sample_questions(self):
        """Render sample questions showcase."""
        st.subheader("📚 Sample Questions")
        
        sample_questions = self._get_sample_questions()
        
        for i, question in enumerate(sample_questions):
            with st.expander(f"Sample {i + 1}: {question.get('title', 'Untitled')}", expanded=i == 0):
                # Show question data
                st.code(json.dumps(question, indent=2), language='json')
                
                # Show rendered preview
                st.subheader("Preview:")
                html_content = self.question_renderer.render_question(
                    question,
                    show_answers=True,
                    show_feedback=True,
                    show_validation=True
                )
                st.components.v1.html(html_content, height=400, scrolling=True)
    
    def _render_latex_examples(self):
        """Render LaTeX examples."""
        st.subheader("🧮 LaTeX Examples")
        
        latex_examples = [
            ("Inline Math", r"The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$."),
            ("Display Math", r"$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$"),
            ("Matrix", r"$$A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$$"),
            ("Fractions", r"$$\frac{d}{dx}\left(\frac{u}{v}\right) = \frac{v\frac{du}{dx} - u\frac{dv}{dx}}{v^2}$$"),
            ("Greek Letters", r"$$\alpha + \beta = \gamma, \quad \sum_{i=1}^n x_i = \mu$$"),
            ("Chemical Formula", r"The reaction is: $\text{H}_2\text{SO}_4 + 2\text{NaOH} \rightarrow \text{Na}_2\text{SO}_4 + 2\text{H}_2\text{O}$")
        ]
        
        for title, latex_code in latex_examples:
            with st.expander(f"{title}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**LaTeX Code:**")
                    st.code(latex_code, language='latex')
                
                with col2:
                    st.write("**Rendered Output:**")
                    processed = self.latex_processor.process_latex(latex_code)
                    st.markdown(f'<div style="font-size:18px;">{processed}</div>', 
                              unsafe_allow_html=True)
    
    def _render_component_demo(self):
        """Render component demonstrations."""
        st.subheader("🔧 Component Demo")
        
        demo_type = st.selectbox(
            "Select Component Demo",
            ["LaTeX Processor", "Question Renderer", "Validation Manager"]
        )
        
        if demo_type == "LaTeX Processor":
            self._demo_latex_processor()
        elif demo_type == "Question Renderer":
            self._demo_question_renderer()
        elif demo_type == "Validation Manager":
            self._demo_validation_manager()
    
    def _demo_latex_processor(self):
        """Demo the LaTeX processor."""
        st.write("**LaTeX Processor Demo**")
        
        latex_input = st.text_area(
            "Enter LaTeX content:",
            value=r"The integral $\int_0^1 x^2 dx = \frac{1}{3}$ and the sum $\sum_{i=1}^n i = \frac{n(n+1)}{2}$.",
            height=100
        )
        
        if st.button("Process LaTeX"):
            try:
                processed = self.latex_processor.process_latex(latex_input)
                st.write("**Processed Output:**")
                st.markdown(processed, unsafe_allow_html=True)
                
                # Show validation
                validation_result = self.latex_processor.math_validator.validate_math_content(latex_input)
                if validation_result:
                    st.write("**Validation Issues:**")
                    for issue in validation_result:
                        if issue['severity'] == 'error':
                            st.error(issue['message'])
                        elif issue['severity'] == 'warning':
                            st.warning(issue['message'])
                        else:
                            st.info(issue['message'])
                else:
                    st.success("No validation issues found!")
                    
            except Exception as e:
                st.error(f"Processing error: {str(e)}")
    
    def _demo_question_renderer(self):
        """Demo the question renderer."""
        st.write("**Question Renderer Demo**")
        
        # Sample question for demo
        sample_question = {
            "type": "multiple_choice",
            "title": "Sample Math Question",
            "question_text": "What is the value of $x$ in the equation $2x + 5 = 13$?",
            "options": [
                "$x = 3$",
                "$x = 4$",
                "$x = 5$",
                "$x = 6$"
            ],
            "correct_answers": [1],
            "general_feedback": "To solve: $2x + 5 = 13 \\Rightarrow 2x = 8 \\Rightarrow x = 4$"
        }
        
        # Render with different modes
        modes = ["Student View", "Answer Key", "Full Preview"]
        selected_mode = st.selectbox("Render Mode", modes)
        
        mode_settings = {
            "Student View": {'show_answers': False, 'show_feedback': False},
            "Answer Key": {'show_answers': True, 'show_feedback': False},
            "Full Preview": {'show_answers': True, 'show_feedback': True}
        }
        
        settings = mode_settings[selected_mode]
        html_content = self.question_renderer.render_question(sample_question, **settings)
        st.components.v1.html(html_content, height=400, scrolling=True)
    
    def _demo_validation_manager(self):
        """Demo the validation manager."""
        st.write("**Validation Manager Demo**")
        
        # Create a question with various issues for demo
        problematic_question = {
            "type": "multiple_choice",
            "question_text": "What is $\\frac{1{0}$?",  # Intentional LaTeX error
            "options": ["Option 1", ""],  # Empty option
            "correct_answers": [5],  # Invalid index
            # Missing required fields
        }
        
        st.write("**Sample Question with Issues:**")
        st.code(json.dumps(problematic_question, indent=2), language='json')
        
        if st.button("Validate Question"):
            result = self.validation_manager.validate_question(problematic_question)
            
            st.write(f"**Validation Result:** {'✅ Valid' if result.is_valid else '❌ Invalid'}")
            st.write(f"**Quality Score:** {result.score:.1f}/100")
            
            if result.flags:
                st.write(f"**Flags:** {', '.join(result.flags)}")
            
            if result.issues:
                st.write("**Issues Found:**")
                for issue in result.issues:
                    if issue.severity == 'error':
                        st.error(f"**{issue.field or 'General'}**: {issue.message}")
                    elif issue.severity == 'warning':
                        st.warning(f"**{issue.field or 'General'}**: {issue.message}")
                    else:
                        st.info(f"**{issue.field or 'General'}**: {issue.message}")
                    
                    if issue.suggestion:
                        st.caption(f"💡 {issue.suggestion}")
    
    def _render_templates(self):
        """Render question templates."""
        st.subheader("📋 Question Templates")
        
        templates = {
            "Multiple Choice": {
                "type": "multiple_choice",
                "title": "Sample Multiple Choice Question",
                "question_text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answers": [1],
                "points": 1.0,
                "difficulty": "Easy"
            },
            "True/False": {
                "type": "true_false",
                "title": "Sample True/False Question",
                "question_text": "The earth is round.",
                "correct_answer": True,
                "points": 1.0,
                "difficulty": "Easy"
            },
            "Numerical": {
                "type": "numerical",
                "title": "Sample Numerical Question",
                "question_text": "What is the value of $\\pi$ to 2 decimal places?",
                "correct_answer": 3.14,
                "tolerance": 0.01,
                "points": 2.0,
                "difficulty": "Medium"
            },
            "Essay": {
                "type": "essay",
                "title": "Sample Essay Question",
                "question_text": "Discuss the impact of technology on education.",
                "word_limit": 500,
                "points": 10.0,
                "difficulty": "Medium"
            }
        }
        
        selected_template = st.selectbox("Select Template", list(templates.keys()))
        
        template_data = templates[selected_template]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Template JSON:**")
            st.code(json.dumps(template_data, indent=2), language='json')
            
            if st.button("Use This Template"):
                # Add to current questions
                questions = self._get_current_questions()
                questions.append(template_data.copy())
                self._update_current_questions(questions)
                st.success("Template added to questions! Switch to Editor mode to modify it.")
        
        with col2:
            st.write("**Template Preview:**")
            html_content = self.question_renderer.render_question(
                template_data,
                show_answers=True,
                show_feedback=True
            )
            st.components.v1.html(html_content, height=300, scrolling=True)
    
    def _render_file_upload(self):
        """Render file upload interface."""
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=['json'],
            help="Upload a JSON file containing questions"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                data = json.loads(content)
                
                # Handle different formats
                if isinstance(data, list):
                    questions = data
                elif isinstance(data, dict) and 'questions' in data:
                    questions = data['questions']
                else:
                    questions = [data]
                
                st.success(f"Successfully loaded {len(questions)} question(s)")
                
                # Preview
                if st.checkbox("Preview Questions"):
                    for i, question in enumerate(questions[:3]):  # Show first 3
                        with st.expander(f"Question {i + 1}"):
                            st.code(json.dumps(question, indent=2), language='json')
                    
                    if len(questions) > 3:
                        st.info(f"... and {len(questions) - 3} more questions")
                
                if st.button("Import Questions"):
                    current_questions = self._get_current_questions()
                    current_questions.extend(questions)
                    self._update_current_questions(current_questions)
                    st.success(f"Imported {len(questions)} questions!")
                    
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON file: {str(e)}")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    def _render_text_import(self):
        """Render text import interface."""
        json_text = st.text_area(
            "Paste JSON content:",
            height=300,
            placeholder='[{"type": "multiple_choice", "question_text": "..."}]'
        )
        
        if st.button("Import from Text"):
            if json_text.strip():
                try:
                    data = json.loads(json_text)
                    
                    # Handle different formats
                    if isinstance(data, list):
                        questions = data
                    elif isinstance(data, dict) and 'questions' in data:
                        questions = data['questions']
                    else:
                        questions = [data]
                    
                    current_questions = self._get_current_questions()
                    current_questions.extend(questions)
                    self._update_current_questions(current_questions)
                    st.success(f"Imported {len(questions)} questions!")
                    
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")
            else:
                st.warning("Please paste JSON content")
    
    def _render_url_import(self):
        """Render URL import interface."""
        url = st.text_input(
            "Enter URL to JSON file:",
            placeholder="https://example.com/questions.json"
        )
        
        if st.button("Import from URL"):
            if url:
                try:
                    import requests
                    response = requests.get(url)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Handle different formats
                    if isinstance(data, list):
                        questions = data
                    elif isinstance(data, dict) and 'questions' in data:
                        questions = data['questions']
                    else:
                        questions = [data]
                    
                    current_questions = self._get_current_questions()
                    current_questions.extend(questions)
                    self._update_current_questions(current_questions)
                    st.success(f"Imported {len(questions)} questions from URL!")
                    
                except Exception as e:
                    st.error(f"Error importing from URL: {str(e)}")
            else:
                st.warning("Please enter a URL")
    
    def _render_format_conversion(self):
        """Render format conversion interface."""
        st.info("Format conversion is not implemented in this demo version.")
        st.write("Supported formats for future implementation:")
        st.write("- GIFT format")
        st.write("- Moodle XML")
        st.write("- CSV format")
        st.write("- QTI 2.1")
    
    def _display_validation_results(self, results: Dict[str, Any]):
        """Display validation results."""
        summary = results['summary']
        
        st.subheader("📊 Validation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Questions", summary['total_questions'])
        with col2:
            st.metric("Valid Questions", summary['valid_questions'])
        with col3:
            st.metric("Invalid Questions", summary['invalid_questions'])
        with col4:
            st.metric("Total Issues", summary['total_issues'])
        
        # Detailed results
        with st.expander("Detailed Results"):
            for result in results['individual_results']:
                idx = result['question_index']
                question_result = result['result']
                
                if question_result['is_valid']:
                    st.success(f"Question {idx + 1}: Valid (Score: {question_result['score']:.1f})")
                else:
                    st.error(f"Question {idx + 1}: {len(question_result['issues'])} issues")
                    
                    for issue in question_result['issues']:
                        severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
                        st.write(f"{severity_icon.get(issue['severity'], '•')} {issue['message']}")
    
    def _generate_export(self, questions: List[Dict[str, Any]], 
                        format_type: str, include_validation: bool) -> str:
        """Generate export data."""
        if format_type == "JSON":
            export_data = {
                "questions": questions,
                "export_info": {
                    "format": "Q2JSON",
                    "version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "total_questions": len(questions)
                }
            }
            
            if include_validation:
                validation_results = self.validation_manager.validate_question_set(questions)
                export_data["validation"] = validation_results
            
            return json.dumps(export_data, indent=2)
        
        else:
            # For other formats, return a placeholder
            return f"Export format '{format_type}' is not fully implemented in this demo.\n\nQuestions to export:\n{json.dumps(questions, indent=2)}"
    
    def _get_current_questions(self) -> List[Dict[str, Any]]:
        """Get current questions from session state."""
        if 'q2json_questions' not in st.session_state:
            st.session_state.q2json_questions = []
        return st.session_state.q2json_questions
    
    def _update_current_questions(self, questions: List[Dict[str, Any]]):
        """Update current questions in session state."""
        st.session_state.q2json_questions = questions
    
    def _create_new_question(self):
        """Create a new question."""
        new_question = {
            "type": "multiple_choice",
            "title": "",
            "question_text": "",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correct_answers": [0],
            "points": 1.0,
            "difficulty": "Medium"
        }
        
        questions = self._get_current_questions()
        questions.append(new_question)
        self._update_current_questions(questions)
        
        st.success("New question created! Switch to Editor mode to customize it.")
        st.rerun()
    
    def _load_sample_questions(self):
        """Load sample questions."""
        sample_questions = self._get_sample_questions()
        self._update_current_questions(sample_questions)
        st.success(f"Loaded {len(sample_questions)} sample questions!")
        st.rerun()
    
    def _clear_all_questions(self):
        """Clear all current questions."""
        self._update_current_questions([])
        st.success("All questions cleared!")
    
    def _save_session(self):
        """Save current session."""
        questions = self._get_current_questions()
        if questions:
            session_data = {
                "questions": questions,
                "timestamp": datetime.now().isoformat(),
                "session_info": {
                    "total_questions": len(questions),
                    "app_version": "Q2JSON Stage 4 Demo"
                }
            }
            
            st.download_button(
                "💾 Download Session",
                json.dumps(session_data, indent=2),
                f"q2json_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
        else:
            st.warning("No questions to save!")
    
    def _get_sample_questions(self) -> List[Dict[str, Any]]:
        """Get sample questions for demonstration."""
        return [
            {
                "type": "multiple_choice",
                "title": "Basic Algebra",
                "question_text": "Solve for $x$: $2x + 5 = 13$",
                "options": [
                    "$x = 3$",
                    "$x = 4$",
                    "$x = 5$",
                    "$x = 6$"
                ],
                "correct_answers": [1],
                "points": 2.0,
                "difficulty": "Easy",
                "category": "Mathematics",
                "tags": ["algebra", "equations"],
                "general_feedback": "To solve: $2x + 5 = 13 \\Rightarrow 2x = 8 \\Rightarrow x = 4$"
            },
            {
                "type": "true_false",
                "title": "Physics Concept",
                "question_text": "The speed of light in vacuum is approximately $3 \\times 10^8$ m/s.",
                "correct_answer": True,
                "points": 1.0,
                "difficulty": "Easy",
                "category": "Physics",
                "tags": ["constants", "light"],
                "general_feedback": "Yes, the speed of light in vacuum is exactly 299,792,458 m/s, which is approximately $3 \\times 10^8$ m/s."
            },
            {
                "type": "numerical",
                "title": "Calculus Integration",
                "question_text": "Evaluate the definite integral: $\\int_0^2 x^2 dx$",
                "correct_answer": 2.667,
                "tolerance": 0.01,
                "unit": "",
                "points": 3.0,
                "difficulty": "Medium",
                "category": "Mathematics",
                "tags": ["calculus", "integration"],
                "general_feedback": "Using the power rule: $\\int_0^2 x^2 dx = \\left[\\frac{x^3}{3}\\right]_0^2 = \\frac{8}{3} - 0 = \\frac{8}{3} \\approx 2.667$"
            },
            {
                "type": "essay",
                "title": "Scientific Method",
                "question_text": "Explain the steps of the scientific method and provide an example of how it might be applied to investigate a hypothesis.",
                "word_limit": 300,
                "points": 10.0,
                "difficulty": "Medium",
                "category": "Science",
                "tags": ["scientific method", "research"],
                "sample_answer": "The scientific method includes: 1) Observation, 2) Question formulation, 3) Hypothesis development, 4) Experimental design, 5) Data collection, 6) Analysis, 7) Conclusion. For example, investigating whether plants grow taller with music exposure.",
                "grading_rubric": "Award points for: clear explanation of steps (6 pts), relevant example (3 pts), proper scientific terminology (1 pt)."
            }
        ]


def main():
    """Main function to run the Q2JSON Stage 4 application."""
    app = Q2JSONStage4Application()
    app.run()


if __name__ == "__main__":
    main()
