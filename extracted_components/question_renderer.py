# Q2JSON Question Renderer Component
"""
Q2JSONQuestionRenderer - Multi-type question display with LaTeX support

Extracted and enhanced from Q2LMS codebase for Q2JSON Stage 4 integration.
Provides comprehensive question rendering with mathematical notation support,
validation integration, and flexible display options.
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
import html

try:
    from .latex_processor import Q2JSONLaTeXProcessor, MathValidationManager
except ImportError:
    from latex_processor import Q2JSONLaTeXProcessor, MathValidationManager


class Q2JSONQuestionRenderer:
    """
    Enhanced question renderer extracted from Q2LMS with mathematical validation.
    
    Features:
    - Multi-type question rendering (MCQ, TF, Essay, Numerical, etc.)
    - LaTeX/KaTeX mathematical notation support
    - Validation integration with flagging
    - Flexible styling and display options
    - Answer key and feedback rendering
    """
    
    def __init__(self, latex_processor: Optional[Q2JSONLaTeXProcessor] = None):
        """Initialize the question renderer."""
        self.latex_processor = latex_processor or Q2JSONLaTeXProcessor()
        self.math_validator = MathValidationManager()
        
        # Question type handlers
        self.type_handlers = {
            'multiple_choice': self._render_multiple_choice,
            'true_false': self._render_true_false,
            'essay': self._render_essay,
            'short_answer': self._render_short_answer,
            'numerical': self._render_numerical,
            'matching': self._render_matching,
            'fill_blank': self._render_fill_blank,
            'ordering': self._render_ordering
        }
        
        # CSS for question styling
        self.question_css = """
        <style>
        .q2json-question {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            background: #fafafa;
        }
        .q2json-question-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .q2json-question-text {
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .q2json-options {
            margin: 10px 0;
        }
        .q2json-option {
            margin: 8px 0;
            padding: 8px;
            border-radius: 4px;
            background: white;
            border: 1px solid #ddd;
        }
        .q2json-correct {
            background: #d4edda !important;
            border-color: #c3e6cb !important;
        }
        .q2json-incorrect {
            background: #f8d7da !important;
            border-color: #f5c6cb !important;
        }
        .q2json-validation-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            color: #856404;
        }
        .q2json-validation-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            color: #721c24;
        }
        .q2json-math-content {
            font-family: 'Times New Roman', serif;
            font-size: 1.1em;
        }
        </style>
        """
    
    def render_question(self, question: Dict[str, Any], 
                       show_answers: bool = False,
                       show_feedback: bool = False,
                       show_validation: bool = True,
                       question_number: Optional[int] = None) -> str:
        """
        Render a complete question with all components.
        
        Args:
            question: Question data dictionary
            show_answers: Whether to show correct answers
            show_feedback: Whether to show feedback
            show_validation: Whether to show validation warnings
            question_number: Optional question numbering
            
        Returns:
            HTML string of rendered question
        """
        try:
            # Validate question structure
            if not self._validate_question_structure(question):
                return self._render_error("Invalid question structure")
            
            # Process LaTeX content
            processed_question = self._process_latex_content(question)
            
            # Get question type and handler
            question_type = processed_question.get('type', 'multiple_choice').lower()
            handler = self.type_handlers.get(question_type, self._render_generic)
            
            # Build question HTML
            html_parts = []
            
            # Add CSS
            html_parts.append(self.question_css)
            
            # Question container start
            html_parts.append('<div class="q2json-question">')
            
            # Question title/number
            if question_number:
                title = f"Question {question_number}"
                if processed_question.get('title'):
                    title += f": {processed_question['title']}"
                html_parts.append(f'<div class="q2json-question-title">{title}</div>')
            elif processed_question.get('title'):
                html_parts.append(f'<div class="q2json-question-title">{processed_question["title"]}</div>')
            
            # Validation warnings
            if show_validation:
                validation_html = self._render_validation_warnings(processed_question)
                if validation_html:
                    html_parts.append(validation_html)
            
            # Question text
            question_text = processed_question.get('question_text', '')
            if question_text:
                processed_text = self.latex_processor.process_latex(question_text)
                html_parts.append(f'<div class="q2json-question-text q2json-math-content">{processed_text}</div>')
            
            # Question-specific content
            content_html = handler(processed_question, show_answers, show_feedback)
            html_parts.append(content_html)
            
            # Additional feedback
            if show_feedback and processed_question.get('general_feedback'):
                feedback_html = self._render_general_feedback(processed_question['general_feedback'])
                html_parts.append(feedback_html)
            
            # Question container end
            html_parts.append('</div>')
            
            return '\n'.join(html_parts)
            
        except Exception as e:
            return self._render_error(f"Rendering error: {str(e)}")
    
    def render_question_list(self, questions: List[Dict[str, Any]], 
                           **render_options) -> str:
        """Render a list of questions."""
        html_parts = []
        
        for i, question in enumerate(questions, 1):
            question_html = self.render_question(
                question, 
                question_number=i,
                **render_options
            )
            html_parts.append(question_html)
        
        return '\n'.join(html_parts)
    
    def _render_multiple_choice(self, question: Dict[str, Any], 
                              show_answers: bool, show_feedback: bool) -> str:
        """Render multiple choice question."""
        html_parts = []
        options = question.get('options', [])
        correct_answers = question.get('correct_answers', [])
        
        if not options:
            return self._render_error("No options provided for multiple choice question")
        
        html_parts.append('<div class="q2json-options">')
        
        for i, option in enumerate(options):
            option_id = f"option_{i}"
            option_text = self.latex_processor.process_latex(str(option))
            
            # Determine styling
            css_class = "q2json-option"
            if show_answers:
                if i in correct_answers or str(i) in correct_answers:
                    css_class += " q2json-correct"
                else:
                    css_class += " q2json-incorrect"
            
            # Option HTML
            option_html = f'''
            <div class="{css_class}">
                <label for="{option_id}">
                    <input type="{'checkbox' if len(correct_answers) > 1 else 'radio'}" 
                           id="{option_id}" name="question_options" value="{i}">
                    <span class="q2json-math-content">{option_text}</span>
                </label>
            </div>
            '''
            html_parts.append(option_html)
            
            # Option feedback
            if show_feedback and question.get('option_feedback'):
                feedback = question['option_feedback'].get(str(i))
                if feedback:
                    feedback_html = f'<div class="q2json-option-feedback">{self.latex_processor.process_latex(feedback)}</div>'
                    html_parts.append(feedback_html)
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _render_true_false(self, question: Dict[str, Any], 
                          show_answers: bool, show_feedback: bool) -> str:
        """Render true/false question."""
        html_parts = []
        correct_answer = question.get('correct_answer', True)
        
        html_parts.append('<div class="q2json-options">')
        
        for value, label in [(True, 'True'), (False, 'False')]:
            css_class = "q2json-option"
            if show_answers:
                if value == correct_answer:
                    css_class += " q2json-correct"
                else:
                    css_class += " q2json-incorrect"
            
            option_html = f'''
            <div class="{css_class}">
                <label>
                    <input type="radio" name="tf_option" value="{str(value).lower()}">
                    {label}
                </label>
            </div>
            '''
            html_parts.append(option_html)
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _render_essay(self, question: Dict[str, Any], 
                     show_answers: bool, show_feedback: bool) -> str:
        """Render essay question."""
        html_parts = []
        
        # Sample answer if available
        if show_answers and question.get('sample_answer'):
            sample_answer = self.latex_processor.process_latex(question['sample_answer'])
            html_parts.append(f'''
            <div class="q2json-sample-answer">
                <strong>Sample Answer:</strong>
                <div class="q2json-math-content">{sample_answer}</div>
            </div>
            ''')
        
        # Essay input area
        html_parts.append('''
        <div class="q2json-essay-input">
            <textarea placeholder="Enter your answer here..." 
                      rows="10" cols="80" 
                      style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
            </textarea>
        </div>
        ''')
        
        return '\n'.join(html_parts)
    
    def _render_short_answer(self, question: Dict[str, Any], 
                           show_answers: bool, show_feedback: bool) -> str:
        """Render short answer question."""
        html_parts = []
        
        # Correct answers if available
        if show_answers and question.get('correct_answers'):
            answers = question['correct_answers']
            if isinstance(answers, list):
                answer_text = ', '.join(str(ans) for ans in answers)
            else:
                answer_text = str(answers)
            
            processed_answers = self.latex_processor.process_latex(answer_text)
            html_parts.append(f'''
            <div class="q2json-correct-answers">
                <strong>Correct Answer(s):</strong>
                <span class="q2json-math-content">{processed_answers}</span>
            </div>
            ''')
        
        # Input field
        html_parts.append('''
        <div class="q2json-short-input">
            <input type="text" placeholder="Enter your answer..." 
                   style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        </div>
        ''')
        
        return '\n'.join(html_parts)
    
    def _render_numerical(self, question: Dict[str, Any], 
                         show_answers: bool, show_feedback: bool) -> str:
        """Render numerical question with unit support."""
        html_parts = []
        
        # Correct answer and tolerance
        if show_answers:
            correct_answer = question.get('correct_answer')
            tolerance = question.get('tolerance', 0)
            unit = question.get('unit', '')
            
            if correct_answer is not None:
                answer_display = f"{correct_answer}"
                if tolerance > 0:
                    answer_display += f" ± {tolerance}"
                if unit:
                    answer_display += f" {unit}"
                
                html_parts.append(f'''
                <div class="q2json-correct-answer">
                    <strong>Correct Answer:</strong>
                    <span class="q2json-math-content">{answer_display}</span>
                </div>
                ''')
        
        # Numerical input
        unit_display = question.get('unit', '')
        html_parts.append(f'''
        <div class="q2json-numerical-input">
            <input type="number" step="any" placeholder="Enter numerical value..." 
                   style="padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            {f'<span class="unit">{unit_display}</span>' if unit_display else ''}
        </div>
        ''')
        
        return '\n'.join(html_parts)
    
    def _render_matching(self, question: Dict[str, Any], 
                        show_answers: bool, show_feedback: bool) -> str:
        """Render matching question."""
        html_parts = []
        
        left_items = question.get('left_items', [])
        right_items = question.get('right_items', [])
        correct_matches = question.get('correct_matches', {})
        
        if not left_items or not right_items:
            return self._render_error("Matching question requires both left and right items")
        
        html_parts.append('<div class="q2json-matching">')
        html_parts.append('<table style="width: 100%; border-collapse: collapse;">')
        
        for i, left_item in enumerate(left_items):
            left_text = self.latex_processor.process_latex(str(left_item))
            
            html_parts.append('<tr>')
            html_parts.append(f'<td style="padding: 10px; border: 1px solid #ddd; width: 50%;">')
            html_parts.append(f'<span class="q2json-math-content">{left_text}</span>')
            html_parts.append('</td>')
            
            html_parts.append('<td style="padding: 10px; border: 1px solid #ddd;">')
            html_parts.append(f'<select name="match_{i}" style="width: 100%; padding: 5px;">')
            html_parts.append('<option value="">Select match...</option>')
            
            for j, right_item in enumerate(right_items):
                right_text = self.latex_processor.process_latex(str(right_item))
                selected = ""
                if show_answers and str(i) in correct_matches:
                    if correct_matches[str(i)] == j:
                        selected = "selected"
                
                html_parts.append(f'<option value="{j}" {selected}>{right_text}</option>')
            
            html_parts.append('</select>')
            html_parts.append('</td>')
            html_parts.append('</tr>')
        
        html_parts.append('</table>')
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _render_fill_blank(self, question: Dict[str, Any], 
                          show_answers: bool, show_feedback: bool) -> str:
        """Render fill-in-the-blank question."""
        question_text = question.get('question_text', '')
        blanks = question.get('blanks', [])
        
        # Replace blanks with input fields
        processed_text = question_text
        for i, blank in enumerate(blanks):
            blank_id = f"blank_{i}"
            
            # Show answer if requested
            value = ""
            if show_answers and blank.get('correct_answer'):
                value = f'value="{html.escape(str(blank["correct_answer"]))}"'
            
            input_html = f'<input type="text" id="{blank_id}" {value} style="border-bottom: 2px solid #333; background: transparent; padding: 2px;">'
            
            # Replace placeholder
            placeholder = blank.get('placeholder', f'_____')
            processed_text = processed_text.replace(placeholder, input_html, 1)
        
        processed_text = self.latex_processor.process_latex(processed_text)
        
        return f'<div class="q2json-fill-blank q2json-math-content">{processed_text}</div>'
    
    def _render_ordering(self, question: Dict[str, Any], 
                        show_answers: bool, show_feedback: bool) -> str:
        """Render ordering/sequencing question."""
        items = question.get('items', [])
        correct_order = question.get('correct_order', list(range(len(items))))
        
        if not items:
            return self._render_error("Ordering question requires items")
        
        html_parts = []
        html_parts.append('<div class="q2json-ordering">')
        html_parts.append('<div class="ordering-instructions">Drag and drop to reorder:</div>')
        
        # Display items in correct order if showing answers
        display_items = items[:]
        if show_answers and correct_order:
            display_items = [items[i] for i in correct_order]
        
        html_parts.append('<ul class="ordering-list" style="list-style: none; padding: 0;">')
        
        for i, item in enumerate(display_items):
            item_text = self.latex_processor.process_latex(str(item))
            html_parts.append(f'''
            <li class="ordering-item" draggable="true" 
                style="padding: 10px; margin: 5px 0; border: 1px solid #ddd; 
                       border-radius: 4px; background: white; cursor: move;">
                <span class="order-number">{i + 1}.</span>
                <span class="q2json-math-content">{item_text}</span>
            </li>
            ''')
        
        html_parts.append('</ul>')
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _render_generic(self, question: Dict[str, Any], 
                       show_answers: bool, show_feedback: bool) -> str:
        """Render generic/unknown question type."""
        return f'''
        <div class="q2json-generic">
            <p><em>Question type: {question.get('type', 'unknown')}</em></p>
            <pre>{json.dumps(question, indent=2)}</pre>
        </div>
        '''
    
    def _process_latex_content(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Process all LaTeX content in question."""
        processed = question.copy()
        
        # Fields that may contain LaTeX
        latex_fields = ['question_text', 'title', 'general_feedback', 'sample_answer']
        
        for field in latex_fields:
            if field in processed and processed[field]:
                processed[field] = self.latex_processor.process_latex(processed[field])
        
        # Process options
        if 'options' in processed:
            processed['options'] = [
                self.latex_processor.process_latex(str(opt)) 
                for opt in processed['options']
            ]
        
        # Process option feedback
        if 'option_feedback' in processed:
            processed['option_feedback'] = {
                k: self.latex_processor.process_latex(str(v))
                for k, v in processed['option_feedback'].items()
            }
        
        return processed
    
    def _render_validation_warnings(self, question: Dict[str, Any]) -> str:
        """Render validation warnings for question."""
        warnings = []
        errors = []
        
        # Check mathematical content
        text_content = question.get('question_text', '')
        if text_content:
            issues = self.math_validator.validate_math_content(text_content)
            for issue in issues:
                if issue['severity'] == 'error':
                    errors.append(issue['message'])
                else:
                    warnings.append(issue['message'])
        
        # Check options for math content
        if 'options' in question:
            for i, option in enumerate(question['options']):
                issues = self.math_validator.validate_math_content(str(option))
                for issue in issues:
                    msg = f"Option {i + 1}: {issue['message']}"
                    if issue['severity'] == 'error':
                        errors.append(msg)
                    else:
                        warnings.append(msg)
        
        html_parts = []
        
        if errors:
            error_list = '\n'.join(f'<li>{error}</li>' for error in errors)
            html_parts.append(f'''
            <div class="q2json-validation-error">
                <strong>⚠️ Validation Errors:</strong>
                <ul>{error_list}</ul>
            </div>
            ''')
        
        if warnings:
            warning_list = '\n'.join(f'<li>{warning}</li>' for warning in warnings)
            html_parts.append(f'''
            <div class="q2json-validation-warning">
                <strong>⚠️ Validation Warnings:</strong>
                <ul>{warning_list}</ul>
            </div>
            ''')
        
        return '\n'.join(html_parts)
    
    def _render_general_feedback(self, feedback: str) -> str:
        """Render general question feedback."""
        processed_feedback = self.latex_processor.process_latex(feedback)
        return f'''
        <div class="q2json-general-feedback" 
             style="background: #e8f4fd; border: 1px solid #bee5eb; 
                    border-radius: 4px; padding: 10px; margin: 10px 0;">
            <strong>Feedback:</strong>
            <div class="q2json-math-content">{processed_feedback}</div>
        </div>
        '''
    
    def _validate_question_structure(self, question: Dict[str, Any]) -> bool:
        """Validate basic question structure."""
        if not isinstance(question, dict):
            return False
        
        # Must have question text or title
        if not question.get('question_text') and not question.get('title'):
            return False
        
        # Type-specific validation
        question_type = question.get('type', 'multiple_choice').lower()
        
        if question_type == 'multiple_choice':
            return bool(question.get('options'))
        elif question_type == 'matching':
            return bool(question.get('left_items')) and bool(question.get('right_items'))
        elif question_type == 'fill_blank':
            return bool(question.get('blanks'))
        elif question_type == 'ordering':
            return bool(question.get('items'))
        
        return True
    
    def _render_error(self, message: str) -> str:
        """Render error message."""
        return f'''
        <div class="q2json-error" 
             style="background: #f8d7da; border: 1px solid #f5c6cb; 
                    border-radius: 4px; padding: 15px; margin: 10px 0; color: #721c24;">
            <strong>Rendering Error:</strong> {html.escape(message)}
        </div>
        '''


# Streamlit integration functions
def st_render_question(question: Dict[str, Any], 
                      renderer: Optional[Q2JSONQuestionRenderer] = None,
                      **options) -> None:
    """Streamlit helper to render a question."""
    if renderer is None:
        renderer = Q2JSONQuestionRenderer()
    
    question_html = renderer.render_question(question, **options)
    st.components.v1.html(question_html, height=600, scrolling=True)


def st_render_question_editor(question: Dict[str, Any],
                             renderer: Optional[Q2JSONQuestionRenderer] = None) -> Dict[str, Any]:
    """Streamlit helper for question editing with live preview."""
    if renderer is None:
        renderer = Q2JSONQuestionRenderer()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Edit Question")
        
        # Basic question editing
        question['title'] = st.text_input("Title", value=question.get('title', ''))
        question['question_text'] = st.text_area("Question Text", 
                                                value=question.get('question_text', ''),
                                                height=150)
        
        question_type = st.selectbox("Question Type",
                                   options=['multiple_choice', 'true_false', 'essay', 
                                          'short_answer', 'numerical', 'matching',
                                          'fill_blank', 'ordering'],
                                   index=0 if question.get('type') not in ['multiple_choice', 'true_false', 'essay', 
                                          'short_answer', 'numerical', 'matching',
                                          'fill_blank', 'ordering'] else 
                                         ['multiple_choice', 'true_false', 'essay', 
                                          'short_answer', 'numerical', 'matching',
                                          'fill_blank', 'ordering'].index(question.get('type', 'multiple_choice')))
        question['type'] = question_type
        
        # Type-specific editing
        if question_type == 'multiple_choice':
            num_options = st.number_input("Number of options", min_value=2, max_value=10, value=4)
            options = []
            correct_answers = []
            
            for i in range(num_options):
                option_text = st.text_input(f"Option {i+1}", 
                                          value=question.get('options', [''] * num_options)[i] if i < len(question.get('options', [])) else '')
                options.append(option_text)
                
                is_correct = st.checkbox(f"Option {i+1} is correct", 
                                       value=i in question.get('correct_answers', []))
                if is_correct:
                    correct_answers.append(i)
            
            question['options'] = options
            question['correct_answers'] = correct_answers
    
    with col2:
        st.subheader("Live Preview")
        
        # Render preview
        try:
            preview_html = renderer.render_question(question, 
                                                  show_answers=st.checkbox("Show answers", value=False),
                                                  show_feedback=st.checkbox("Show feedback", value=False),
                                                  show_validation=st.checkbox("Show validation", value=True))
            st.components.v1.html(preview_html, height=400, scrolling=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
    
    return question
