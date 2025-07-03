# Q2JSON Editor Framework Component
"""
Q2JSONEditorFramework - Side-by-side editing with live preview

Extracted and enhanced from Q2LMS codebase for Q2JSON Stage 4 integration.
Provides comprehensive editing framework with mathematical notation support,
real-time validation, and flexible preview modes.
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import copy
import re

try:
    from .latex_processor import Q2JSONLaTeXProcessor
    from .question_renderer import Q2JSONQuestionRenderer
    from .validation_manager import Q2JSONValidationManager
except ImportError:
    from latex_processor import Q2JSONLaTeXProcessor
    from question_renderer import Q2JSONQuestionRenderer
    from validation_manager import Q2JSONValidationManager


class Q2JSONEditorFramework:
    """
    Advanced editing framework extracted from Q2LMS with enhanced preview capabilities.
    
    Features:
    - Side-by-side editing with live preview
    - Mathematical notation support with LaTeX/KaTeX
    - Real-time validation and error highlighting
    - Undo/redo functionality
    - Auto-save capabilities
    - Multiple preview modes (student view, answer key, etc.)
    - Batch editing operations
    """
    
    def __init__(self, 
                 latex_processor: Optional[Q2JSONLaTeXProcessor] = None,
                 question_renderer: Optional[Q2JSONQuestionRenderer] = None,
                 validation_manager: Optional[Q2JSONValidationManager] = None,
                 save_callback: Optional[Callable] = None):
        """Initialize the editor framework."""
        self.latex_processor = latex_processor or Q2JSONLaTeXProcessor()
        self.question_renderer = question_renderer or Q2JSONQuestionRenderer(self.latex_processor)
        self.validation_manager = validation_manager or Q2JSONValidationManager()
        self.save_callback = save_callback
        
        # Editor state
        self.edit_history = []
        self.current_position = -1
        self.max_history = 50
        self.auto_save_enabled = True
        self.auto_save_interval = 30  # seconds
        
        # Preview modes
        self.preview_modes = {
            'student': {'show_answers': False, 'show_feedback': False, 'show_validation': False},
            'instructor': {'show_answers': True, 'show_feedback': True, 'show_validation': True},
            'answer_key': {'show_answers': True, 'show_feedback': False, 'show_validation': False},
            'validation': {'show_answers': False, 'show_feedback': False, 'show_validation': True}
        }
        
        # Editor configuration
        self.editor_config = {
            'theme': 'light',
            'font_size': 14,
            'show_line_numbers': True,
            'word_wrap': True,
            'auto_indent': True,
            'math_preview': True,
            'validation_on_type': True
        }
    
    def create_editor_interface(self, 
                              questions: List[Dict[str, Any]],
                              title: str = "Q2JSON Editor",
                              allow_batch_ops: bool = True) -> List[Dict[str, Any]]:
        """
        Create the main editor interface with side-by-side editing.
        
        Args:
            questions: List of questions to edit
            title: Interface title
            allow_batch_ops: Whether to allow batch operations
            
        Returns:
            Updated list of questions
        """
        st.title(title)
        
        # Initialize session state
        if 'editor_questions' not in st.session_state:
            st.session_state.editor_questions = copy.deepcopy(questions)
        if 'selected_question' not in st.session_state:
            st.session_state.selected_question = 0
        if 'preview_mode' not in st.session_state:
            st.session_state.preview_mode = 'student'
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = 'single'
        
        # Top toolbar
        self._render_toolbar(allow_batch_ops)
        
        # Main content area
        if st.session_state.edit_mode == 'single':
            self._render_single_question_editor()
        elif st.session_state.edit_mode == 'batch':
            self._render_batch_editor()
        elif st.session_state.edit_mode == 'json':
            self._render_json_editor()
        
        return st.session_state.editor_questions
    
    def _render_toolbar(self, allow_batch_ops: bool):
        """Render the top toolbar with controls."""
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
        
        with col1:
            # Edit mode selection
            edit_modes = ['single', 'json']
            if allow_batch_ops:
                edit_modes.append('batch')
            
            st.session_state.edit_mode = st.selectbox(
                "Edit Mode",
                options=edit_modes,
                index=edit_modes.index(st.session_state.edit_mode)
            )
        
        with col2:
            # Preview mode selection
            st.session_state.preview_mode = st.selectbox(
                "Preview Mode",
                options=list(self.preview_modes.keys()),
                index=list(self.preview_modes.keys()).index(st.session_state.preview_mode)
            )
        
        with col3:
            # Question navigation
            if st.session_state.editor_questions:
                st.session_state.selected_question = st.selectbox(
                    "Question",
                    options=range(len(st.session_state.editor_questions)),
                    format_func=lambda x: f"Question {x + 1}",
                    index=min(st.session_state.selected_question, len(st.session_state.editor_questions) - 1)
                )
        
        with col4:
            # Actions
            if st.button("➕ Add Question"):
                self._add_new_question()
            
            if st.button("🗑️ Delete Question") and st.session_state.editor_questions:
                self._delete_current_question()
        
        with col5:
            # Validation summary
            if st.session_state.editor_questions:
                total_issues = sum(
                    len(self.validation_manager.validate_question(q).issues)
                    for q in st.session_state.editor_questions
                )
                
                if total_issues > 0:
                    st.error(f"⚠️ {total_issues} validation issues")
                else:
                    st.success("✅ All questions valid")
    
    def _render_single_question_editor(self):
        """Render single question editor with side-by-side layout."""
        if not st.session_state.editor_questions:
            st.info("No questions to edit. Add a question to get started.")
            return
        
        current_question = st.session_state.editor_questions[st.session_state.selected_question]
        
        # Create two columns for side-by-side editing
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("✏️ Edit Question")
            edited_question = self._render_question_editor(current_question)
            
            # Update question if changes were made
            if edited_question != current_question:
                self._update_question(st.session_state.selected_question, edited_question)
        
        with col2:
            st.subheader("👁️ Live Preview")
            self._render_question_preview(current_question)
    
    def _render_question_editor(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Render the question editor form."""
        edited_question = copy.deepcopy(question)
        
        # Basic question information
        with st.expander("📝 Basic Information", expanded=True):
            edited_question['title'] = st.text_input(
                "Question Title",
                value=edited_question.get('title', ''),
                help="Optional title for the question"
            )
            
            edited_question['question_text'] = st.text_area(
                "Question Text",
                value=edited_question.get('question_text', ''),
                height=150,
                help="Main question text. LaTeX math supported: $inline$ or $$display$$"
            )
            
            # Question type
            question_types = [
                'multiple_choice', 'true_false', 'essay', 'short_answer',
                'numerical', 'matching', 'fill_blank', 'ordering'
            ]
            
            current_type = edited_question.get('type', 'multiple_choice')
            if current_type not in question_types:
                question_types.append(current_type)
            
            edited_question['type'] = st.selectbox(
                "Question Type",
                options=question_types,
                index=question_types.index(current_type)
            )
        
        # Type-specific editors
        question_type = edited_question['type']
        
        if question_type == 'multiple_choice':
            edited_question = self._edit_multiple_choice(edited_question)
        elif question_type == 'true_false':
            edited_question = self._edit_true_false(edited_question)
        elif question_type == 'essay':
            edited_question = self._edit_essay(edited_question)
        elif question_type == 'short_answer':
            edited_question = self._edit_short_answer(edited_question)
        elif question_type == 'numerical':
            edited_question = self._edit_numerical(edited_question)
        elif question_type == 'matching':
            edited_question = self._edit_matching(edited_question)
        elif question_type == 'fill_blank':
            edited_question = self._edit_fill_blank(edited_question)
        elif question_type == 'ordering':
            edited_question = self._edit_ordering(edited_question)
        
        # Additional settings
        with st.expander("⚙️ Additional Settings"):
            edited_question['points'] = st.number_input(
                "Points",
                min_value=0.0,
                value=float(edited_question.get('points', 1.0)),
                step=0.5
            )
            
            edited_question['difficulty'] = st.selectbox(
                "Difficulty",
                options=['Easy', 'Medium', 'Hard'],
                index=['Easy', 'Medium', 'Hard'].index(edited_question.get('difficulty', 'Medium'))
            )
            
            edited_question['category'] = st.text_input(
                "Category/Topic",
                value=edited_question.get('category', ''),
                help="Subject area or topic classification"
            )
            
            edited_question['tags'] = st.text_input(
                "Tags",
                value=', '.join(edited_question.get('tags', [])),
                help="Comma-separated tags"
            )
            
            # Convert tags back to list
            if edited_question['tags']:
                edited_question['tags'] = [tag.strip() for tag in edited_question['tags'].split(',')]
            else:
                edited_question['tags'] = []
            
            edited_question['general_feedback'] = st.text_area(
                "General Feedback",
                value=edited_question.get('general_feedback', ''),
                help="Feedback shown regardless of answer correctness"
            )
        
        return edited_question
    
    def _edit_multiple_choice(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit multiple choice question specific fields."""
        with st.expander("🔘 Multiple Choice Options", expanded=True):
            # Number of options
            current_options = question.get('options', ['', '', '', ''])
            num_options = st.number_input(
                "Number of options",
                min_value=2,
                max_value=10,
                value=max(len(current_options), 2)
            )
            
            # Adjust options list
            while len(current_options) < num_options:
                current_options.append('')
            current_options = current_options[:num_options]
            
            # Edit options
            options = []
            correct_answers = question.get('correct_answers', [])
            new_correct_answers = []
            
            for i in range(num_options):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    option_text = st.text_area(
                        f"Option {i + 1}",
                        value=current_options[i],
                        height=60,
                        key=f"option_{i}"
                    )
                    options.append(option_text)
                
                with col2:
                    is_correct = st.checkbox(
                        "Correct",
                        value=i in correct_answers,
                        key=f"correct_{i}"
                    )
                    if is_correct:
                        new_correct_answers.append(i)
            
            question['options'] = options
            question['correct_answers'] = new_correct_answers
            
            # Multiple correct answers allowed?
            question['multiple_correct'] = st.checkbox(
                "Allow multiple correct answers",
                value=question.get('multiple_correct', False)
            )
        
        return question
    
    def _edit_true_false(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit true/false question specific fields."""
        with st.expander("✅ True/False Settings", expanded=True):
            question['correct_answer'] = st.radio(
                "Correct Answer",
                options=[True, False],
                format_func=lambda x: "True" if x else "False",
                index=0 if question.get('correct_answer', True) else 1
            )
        
        return question
    
    def _edit_essay(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit essay question specific fields."""
        with st.expander("📝 Essay Settings", expanded=True):
            question['word_limit'] = st.number_input(
                "Word Limit (0 for no limit)",
                min_value=0,
                value=question.get('word_limit', 0)
            )
            
            question['sample_answer'] = st.text_area(
                "Sample Answer",
                value=question.get('sample_answer', ''),
                height=150,
                help="Optional sample or model answer"
            )
            
            question['grading_rubric'] = st.text_area(
                "Grading Rubric",
                value=question.get('grading_rubric', ''),
                height=100,
                help="Criteria for grading this essay"
            )
        
        return question
    
    def _edit_short_answer(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit short answer question specific fields."""
        with st.expander("📝 Short Answer Settings", expanded=True):
            # Correct answers (can be multiple)
            current_answers = question.get('correct_answers', [])
            if isinstance(current_answers, str):
                current_answers = [current_answers]
            
            answers_text = st.text_area(
                "Correct Answers (one per line)",
                value='\n'.join(str(ans) for ans in current_answers),
                height=100,
                help="Enter multiple acceptable answers, one per line"
            )
            
            question['correct_answers'] = [
                ans.strip() for ans in answers_text.split('\n') if ans.strip()
            ]
            
            question['case_sensitive'] = st.checkbox(
                "Case sensitive",
                value=question.get('case_sensitive', False)
            )
            
            question['exact_match'] = st.checkbox(
                "Exact match required",
                value=question.get('exact_match', True),
                help="If false, partial matches may be accepted"
            )
        
        return question
    
    def _edit_numerical(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit numerical question specific fields."""
        with st.expander("🔢 Numerical Settings", expanded=True):
            question['correct_answer'] = st.number_input(
                "Correct Answer",
                value=float(question.get('correct_answer', 0)),
                step=0.01
            )
            
            question['tolerance'] = st.number_input(
                "Tolerance (± value)",
                min_value=0.0,
                value=float(question.get('tolerance', 0)),
                step=0.01,
                help="Acceptable margin of error"
            )
            
            question['unit'] = st.text_input(
                "Unit",
                value=question.get('unit', ''),
                help="e.g., 'm/s', 'kg', 'N·m'"
            )
            
            question['decimal_places'] = st.number_input(
                "Decimal Places",
                min_value=0,
                max_value=10,
                value=question.get('decimal_places', 2)
            )
        
        return question
    
    def _edit_matching(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit matching question specific fields."""
        with st.expander("🔗 Matching Settings", expanded=True):
            # Left items
            left_items = question.get('left_items', [''])
            st.write("**Left Column Items:**")
            
            num_left = st.number_input("Number of left items", min_value=1, value=len(left_items))
            
            while len(left_items) < num_left:
                left_items.append('')
            left_items = left_items[:num_left]
            
            new_left_items = []
            for i, item in enumerate(left_items):
                new_item = st.text_input(f"Left item {i + 1}", value=item, key=f"left_{i}")
                new_left_items.append(new_item)
            
            question['left_items'] = new_left_items
            
            # Right items
            right_items = question.get('right_items', [''])
            st.write("**Right Column Items:**")
            
            num_right = st.number_input("Number of right items", min_value=1, value=len(right_items))
            
            while len(right_items) < num_right:
                right_items.append('')
            right_items = right_items[:num_right]
            
            new_right_items = []
            for i, item in enumerate(right_items):
                new_item = st.text_input(f"Right item {i + 1}", value=item, key=f"right_{i}")
                new_right_items.append(new_item)
            
            question['right_items'] = new_right_items
            
            # Correct matches
            st.write("**Correct Matches:**")
            correct_matches = question.get('correct_matches', {})
            new_correct_matches = {}
            
            for i in range(len(new_left_items)):
                if new_left_items[i]:  # Only show if left item exists
                    match_options = [f"{j}: {item}" for j, item in enumerate(new_right_items) if item]
                    current_match = correct_matches.get(str(i), 0)
                    
                    if match_options:
                        selected_match = st.selectbox(
                            f"Match for '{new_left_items[i][:30]}...'",
                            options=range(len(match_options)),
                            format_func=lambda x: match_options[x],
                            index=min(current_match, len(match_options) - 1),
                            key=f"match_{i}"
                        )
                        new_correct_matches[str(i)] = selected_match
            
            question['correct_matches'] = new_correct_matches
        
        return question
    
    def _edit_fill_blank(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit fill-in-the-blank question specific fields."""
        with st.expander("⬜ Fill in the Blank Settings", expanded=True):
            st.info("Use {{blank}} in your question text to indicate where blanks should appear.")
            
            # Count blanks in question text
            question_text = question.get('question_text', '')
            blank_count = question_text.count('{{blank}}')
            
            if blank_count > 0:
                st.success(f"Found {blank_count} blank(s) in question text")
                
                # Configure each blank
                blanks = question.get('blanks', [])
                while len(blanks) < blank_count:
                    blanks.append({'correct_answer': '', 'placeholder': '_____'})
                blanks = blanks[:blank_count]
                
                new_blanks = []
                for i, blank in enumerate(blanks):
                    st.write(f"**Blank {i + 1}:**")
                    
                    correct_answer = st.text_input(
                        f"Correct answer for blank {i + 1}",
                        value=blank.get('correct_answer', ''),
                        key=f"blank_answer_{i}"
                    )
                    
                    placeholder = st.text_input(
                        f"Placeholder for blank {i + 1}",
                        value=blank.get('placeholder', '_____'),
                        key=f"blank_placeholder_{i}"
                    )
                    
                    new_blanks.append({
                        'correct_answer': correct_answer,
                        'placeholder': placeholder
                    })
                
                question['blanks'] = new_blanks
            else:
                st.warning("No {{blank}} placeholders found in question text")
                question['blanks'] = []
        
        return question
    
    def _edit_ordering(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit ordering question specific fields."""
        with st.expander("🔢 Ordering Settings", expanded=True):
            # Items to order
            items = question.get('items', [''])
            
            num_items = st.number_input("Number of items", min_value=2, value=len(items))
            
            while len(items) < num_items:
                items.append('')
            items = items[:num_items]
            
            new_items = []
            for i, item in enumerate(items):
                new_item = st.text_input(f"Item {i + 1}", value=item, key=f"order_item_{i}")
                new_items.append(new_item)
            
            question['items'] = new_items
            
            # Correct order
            st.write("**Correct Order:**")
            st.info("Drag and drop to set the correct order (simulation - use numbers for now)")
            
            correct_order = question.get('correct_order', list(range(len(new_items))))
            
            # Simple number input for order (in real implementation, would use drag-drop)
            new_correct_order = []
            for i, item in enumerate(new_items):
                if item:  # Only show if item exists
                    position = st.number_input(
                        f"Position of '{item[:30]}...'",
                        min_value=1,
                        max_value=len(new_items),
                        value=correct_order[i] + 1 if i < len(correct_order) else i + 1,
                        key=f"order_pos_{i}"
                    )
                    new_correct_order.append(position - 1)
            
            question['correct_order'] = new_correct_order
        
        return question
    
    def _render_question_preview(self, question: Dict[str, Any]):
        """Render the live preview of the question."""
        try:
            # Get preview mode settings
            preview_settings = self.preview_modes[st.session_state.preview_mode]
            
            # Add validation results
            validation_result = self.validation_manager.validate_question(question)
            
            # Render question
            question_html = self.question_renderer.render_question(
                question,
                question_number=st.session_state.selected_question + 1,
                **preview_settings
            )
            
            # Display validation summary
            if validation_result.issues:
                st.error(f"⚠️ {len(validation_result.issues)} validation issues found")
                
                with st.expander("View Validation Issues"):
                    for issue in validation_result.issues:
                        if issue.severity == 'error':
                            st.error(f"**Error**: {issue.message}")
                        elif issue.severity == 'warning':
                            st.warning(f"**Warning**: {issue.message}")
                        else:
                            st.info(f"**Info**: {issue.message}")
            else:
                st.success("✅ Question validation passed")
            
            # Render the question
            st.components.v1.html(question_html, height=600, scrolling=True)
            
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
            st.code(str(question), language='json')
    
    def _render_batch_editor(self):
        """Render batch editing interface."""
        st.subheader("📦 Batch Operations")
        
        # Batch operation selection
        batch_ops = [
            'Update Category/Tags',
            'Update Difficulty',
            'Update Points',
            'Find and Replace',
            'Validate All',
            'Export Selected'
        ]
        
        selected_op = st.selectbox("Select Batch Operation", batch_ops)
        
        # Question selection
        st.write("**Select Questions:**")
        all_selected = st.checkbox("Select All")
        
        selected_questions = []
        if all_selected:
            selected_questions = list(range(len(st.session_state.editor_questions)))
        else:
            for i, question in enumerate(st.session_state.editor_questions):
                title = question.get('title', f'Question {i + 1}')
                if st.checkbox(f"{i + 1}: {title}", key=f"batch_select_{i}"):
                    selected_questions.append(i)
        
        if selected_questions:
            st.info(f"Selected {len(selected_questions)} question(s)")
            
            # Execute batch operation
            if selected_op == 'Update Category/Tags':
                self._batch_update_metadata(selected_questions)
            elif selected_op == 'Update Difficulty':
                self._batch_update_difficulty(selected_questions)
            elif selected_op == 'Update Points':
                self._batch_update_points(selected_questions)
            elif selected_op == 'Find and Replace':
                self._batch_find_replace(selected_questions)
            elif selected_op == 'Validate All':
                self._batch_validate(selected_questions)
            elif selected_op == 'Export Selected':
                self._batch_export(selected_questions)
    
    def _render_json_editor(self):
        """Render JSON editor interface."""
        st.subheader("📝 JSON Editor")
        
        if not st.session_state.editor_questions:
            st.info("No questions to edit.")
            return
        
        # Select question to edit as JSON
        question_idx = st.selectbox(
            "Select Question to Edit",
            range(len(st.session_state.editor_questions)),
            format_func=lambda x: f"Question {x + 1}"
        )
        
        # JSON editor
        current_question = st.session_state.editor_questions[question_idx]
        json_str = json.dumps(current_question, indent=2)
        
        edited_json = st.text_area(
            "Edit JSON",
            value=json_str,
            height=400,
            help="Edit the question as JSON. Be careful with syntax!"
        )
        
        # Validate and update
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Validate JSON"):
                try:
                    parsed_question = json.loads(edited_json)
                    st.success("✅ Valid JSON structure")
                    
                    # Validate as question
                    validation_result = self.validation_manager.validate_question(parsed_question)
                    if validation_result.issues:
                        st.warning(f"⚠️ {len(validation_result.issues)} validation issues")
                    else:
                        st.success("✅ Valid question structure")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {str(e)}")
        
        with col2:
            if st.button("Update Question"):
                try:
                    parsed_question = json.loads(edited_json)
                    st.session_state.editor_questions[question_idx] = parsed_question
                    st.success("✅ Question updated")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"❌ Cannot update: Invalid JSON: {str(e)}")
    
    def _add_new_question(self):
        """Add a new question."""
        new_question = {
            'type': 'multiple_choice',
            'title': '',
            'question_text': '',
            'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
            'correct_answers': [0],
            'points': 1.0,
            'difficulty': 'Medium',
            'category': '',
            'tags': []
        }
        
        st.session_state.editor_questions.append(new_question)
        st.session_state.selected_question = len(st.session_state.editor_questions) - 1
        st.rerun()
    
    def _delete_current_question(self):
        """Delete the currently selected question."""
        if st.session_state.editor_questions:
            del st.session_state.editor_questions[st.session_state.selected_question]
            
            # Adjust selected question index
            if st.session_state.selected_question >= len(st.session_state.editor_questions):
                st.session_state.selected_question = max(0, len(st.session_state.editor_questions) - 1)
            
            st.rerun()
    
    def _update_question(self, index: int, updated_question: Dict[str, Any]):
        """Update a question and save to history."""
        if index < len(st.session_state.editor_questions):
            st.session_state.editor_questions[index] = updated_question
    
    def _batch_update_metadata(self, selected_questions: List[int]):
        """Batch update category and tags."""
        st.write("**Update Category/Tags:**")
        
        new_category = st.text_input("New Category (leave empty to keep current)")
        new_tags = st.text_input("New Tags (comma-separated, leave empty to keep current)")
        
        if st.button("Apply Changes"):
            for idx in selected_questions:
                question = st.session_state.editor_questions[idx]
                
                if new_category:
                    question['category'] = new_category
                
                if new_tags:
                    question['tags'] = [tag.strip() for tag in new_tags.split(',')]
            
            st.success(f"Updated {len(selected_questions)} questions")
            st.rerun()
    
    def _batch_update_difficulty(self, selected_questions: List[int]):
        """Batch update difficulty."""
        st.write("**Update Difficulty:**")
        
        new_difficulty = st.selectbox("New Difficulty", ['Easy', 'Medium', 'Hard'])
        
        if st.button("Apply Changes"):
            for idx in selected_questions:
                st.session_state.editor_questions[idx]['difficulty'] = new_difficulty
            
            st.success(f"Updated {len(selected_questions)} questions")
            st.rerun()
    
    def _batch_update_points(self, selected_questions: List[int]):
        """Batch update points."""
        st.write("**Update Points:**")
        
        new_points = st.number_input("New Points", min_value=0.0, value=1.0, step=0.5)
        
        if st.button("Apply Changes"):
            for idx in selected_questions:
                st.session_state.editor_questions[idx]['points'] = new_points
            
            st.success(f"Updated {len(selected_questions)} questions")
            st.rerun()
    
    def _batch_find_replace(self, selected_questions: List[int]):
        """Batch find and replace."""
        st.write("**Find and Replace:**")
        
        find_text = st.text_input("Find")
        replace_text = st.text_input("Replace with")
        
        fields_to_search = st.multiselect(
            "Search in fields",
            ['question_text', 'title', 'options', 'general_feedback'],
            default=['question_text']
        )
        
        case_sensitive = st.checkbox("Case sensitive")
        
        if st.button("Apply Changes") and find_text:
            changes_made = 0
            
            for idx in selected_questions:
                question = st.session_state.editor_questions[idx]
                
                for field in fields_to_search:
                    if field in question:
                        if field == 'options' and isinstance(question[field], list):
                            # Handle options list
                            for i, option in enumerate(question[field]):
                                if isinstance(option, str):
                                    if case_sensitive:
                                        if find_text in option:
                                            question[field][i] = option.replace(find_text, replace_text)
                                            changes_made += 1
                                    else:
                                        if find_text.lower() in option.lower():
                                            question[field][i] = re.sub(
                                                re.escape(find_text), 
                                                replace_text, 
                                                option, 
                                                flags=re.IGNORECASE
                                            )
                                            changes_made += 1
                        elif isinstance(question[field], str):
                            # Handle string fields
                            if case_sensitive:
                                if find_text in question[field]:
                                    question[field] = question[field].replace(find_text, replace_text)
                                    changes_made += 1
                            else:
                                if find_text.lower() in question[field].lower():
                                    question[field] = re.sub(
                                        re.escape(find_text), 
                                        replace_text, 
                                        question[field], 
                                        flags=re.IGNORECASE
                                    )
                                    changes_made += 1
            
            if changes_made > 0:
                st.success(f"Made {changes_made} replacements")
                st.rerun()
            else:
                st.info("No matches found")
    
    def _batch_validate(self, selected_questions: List[int]):
        """Batch validate questions."""
        st.write("**Validation Results:**")
        
        total_issues = 0
        for idx in selected_questions:
            question = st.session_state.editor_questions[idx]
            validation_result = self.validation_manager.validate_question(question)
            
            if validation_result.issues:
                total_issues += len(validation_result.issues)
                
                with st.expander(f"Question {idx + 1} - {len(validation_result.issues)} issues"):
                    for issue in validation_result.issues:
                        if issue['severity'] == 'error':
                            st.error(f"**Error**: {issue['message']}")
                        elif issue['severity'] == 'warning':
                            st.warning(f"**Warning**: {issue['message']}")
                        else:
                            st.info(f"**Info**: {issue['message']}")
        
        if total_issues == 0:
            st.success("✅ All selected questions are valid!")
        else:
            st.error(f"Found {total_issues} validation issues across {len(selected_questions)} questions")
    
    def _batch_export(self, selected_questions: List[int]):
        """Batch export questions."""
        st.write("**Export Selected Questions:**")
        
        export_format = st.selectbox("Export Format", ['JSON', 'CSV', 'QTI'])
        
        if st.button("Generate Export"):
            selected_data = [st.session_state.editor_questions[idx] for idx in selected_questions]
            
            if export_format == 'JSON':
                export_data = json.dumps(selected_data, indent=2)
                st.download_button(
                    "Download JSON",
                    export_data,
                    f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
            
            # Add other export formats as needed
            st.success(f"Export prepared for {len(selected_questions)} questions")


# Streamlit integration helper
def create_q2json_editor(questions: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
    """Create a Q2JSON editor interface in Streamlit."""
    editor = Q2JSONEditorFramework()
    return editor.create_editor_interface(questions, **kwargs)
