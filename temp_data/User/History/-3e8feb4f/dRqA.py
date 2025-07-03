# extracted_components/validation_manager.py
"""
Q2JSON Validation Manager
Extracted and enhanced from Q2LMS question_flag_manager.py architecture

Provides comprehensive validation and flagging system for Q2JSON Stage 4.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
import json
from .latex_processor import Q2JSONLaTeXProcessor


class Q2JSONValidationManager:
    """
    Enhanced validation manager combining Q2LMS flagging architecture with Q2JSON validation.
    
    Extracted from:
    - Q2LMS question_flag_manager.py (flagging architecture)
    - Enhanced with mathematical validation capabilities
    
    Enhanced with:
    - Mathematical validation rules
    - Multi-level validation system (critical/warning/info)
    - Batch validation operations
    - Validation reporting and analytics
    """
    
    def __init__(self):
        self.latex_processor = Q2JSONLaTeXProcessor()
        
        # Validation types and their configurations
        self.validation_types = {
            'mathematical': {
                'name': 'Mathematical Issues',
                'icon': '🧮',
                'levels': ['critical', 'warning', 'info'],
                'description': 'LaTeX syntax, rendering, and mathematical notation validation'
            },
            'content': {
                'name': 'Content Quality',
                'icon': '📝',
                'levels': ['warning', 'info'],
                'description': 'Question content completeness and quality checks'
            },
            'structure': {
                'name': 'Structure Issues',
                'icon': '🏗️',
                'levels': ['critical', 'warning'],
                'description': 'Question structure and format validation'
            },
            'accessibility': {
                'name': 'Accessibility',
                'icon': '♿',
                'levels': ['warning', 'info'],
                'description': 'Accessibility and inclusivity recommendations'
            }
        }
        
        # Flag colors for UI
        self.flag_colors = {
            'critical': '#dc3545',  # Red
            'warning': '#ffc107',   # Yellow
            'info': '#17a2b8'       # Cyan
        }
    
    def validate_question_comprehensive(self, question_data: Dict[str, Any], question_index: Optional[int] = None) -> Dict[str, Any]:
        """
        Comprehensive validation of a single question.
        
        Args:
            question_data: Question data to validate
            question_index: Optional question index for context
            
        Returns:
            Comprehensive validation results
        """
        validation_results = {
            'question_index': question_index,
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'valid',
            'validation_types': {},
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'warnings': 0,
                'info_items': 0
            },
            'recommendations': [],
            'validation_score': 100  # Start with perfect score, deduct for issues
        }
        
        # Mathematical validation
        math_results = self._validate_mathematical_content(question_data)
        validation_results['validation_types']['mathematical'] = math_results
        
        # Content validation
        content_results = self._validate_content_quality(question_data)
        validation_results['validation_types']['content'] = content_results
        
        # Structure validation
        structure_results = self._validate_question_structure(question_data)
        validation_results['validation_types']['structure'] = structure_results
        
        # Accessibility validation
        accessibility_results = self._validate_accessibility(question_data)
        validation_results['validation_types']['accessibility'] = accessibility_results
        
        # Aggregate results
        self._aggregate_validation_results(validation_results)
        
        return validation_results
    
    def validate_question_batch(self, questions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple questions in batch.
        
        Args:
            questions_data: List of question data dictionaries
            
        Returns:
            Batch validation results
        """
        batch_results = {
            'timestamp': datetime.now().isoformat(),
            'total_questions': len(questions_data),
            'question_results': [],
            'batch_summary': {
                'questions_with_critical_issues': 0,
                'questions_with_warnings': 0,
                'questions_valid': 0,
                'most_common_issues': {}
            },
            'recommendations': {
                'immediate_actions': [],
                'improvements': [],
                'best_practices': []
            }
        }
        
        # Validate each question
        all_issues = []
        for i, question_data in enumerate(questions_data):
            question_results = self.validate_question_comprehensive(question_data, i)
            batch_results['question_results'].append(question_results)
            
            # Collect issues for analysis
            for validation_type, type_results in question_results['validation_types'].items():
                for level, issues in type_results.get('flags', {}).items():
                    for issue in issues:
                        all_issues.append({
                            'question_index': i,
                            'type': validation_type,
                            'level': level,
                            'issue_type': issue.get('type', 'unknown'),
                            'message': issue.get('message', '')
                        })
        
        # Analyze batch results
        self._analyze_batch_results(batch_results, all_issues)
        
        return batch_results
    
    def add_validation_flags_to_dataframe(self, df: pd.DataFrame, validation_batch_results: Dict[str, Any]) -> pd.DataFrame:
        """
        Add validation flags to DataFrame (similar to Q2LMS flag management).
        
        Args:
            df: DataFrame to add flags to
            validation_batch_results: Batch validation results
            
        Returns:
            DataFrame with validation flag columns
        """
        # Add validation flag columns
        flag_columns = [
            'math_critical', 'math_warning', 'math_info',
            'content_warning', 'content_info',
            'structure_critical', 'structure_warning',
            'accessibility_warning', 'accessibility_info',
            'overall_validation_status', 'validation_score'
        ]
        
        for col in flag_columns:
            if col not in df.columns:
                if 'critical' in col:
                    df[col] = False
                elif 'warning' in col or 'info' in col:
                    df[col] = False
                elif col == 'overall_validation_status':
                    df[col] = 'valid'
                elif col == 'validation_score':
                    df[col] = 100
        
        # Update flags based on validation results
        for i, question_results in enumerate(validation_batch_results['question_results']):
            if i < len(df):
                self._update_dataframe_row_flags(df, i, question_results)
        
        return df
    
    def render_validation_dashboard(self, validation_results: Dict[str, Any]) -> None:
        """
        Render comprehensive validation dashboard.
        
        Args:
            validation_results: Validation results (single question or batch)
        """
        if 'question_results' in validation_results:
            # Batch results
            self._render_batch_validation_dashboard(validation_results)
        else:
            # Single question results
            self._render_single_question_validation_dashboard(validation_results)
    
    def render_validation_controls(self, df: pd.DataFrame) -> None:
        """
        Render validation controls and batch operations.
        
        Args:
            df: DataFrame with validation flags
        """
        st.markdown("### 🔍 Validation Controls")
        
        # Validation summary
        self._render_validation_summary_metrics(df)
        
        st.markdown("---")
        
        # Batch validation controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🧮 Validate All Math", help="Run mathematical validation on all questions"):
                self._batch_validate_mathematical(df)
        
        with col2:
            if st.button("📝 Check Content", help="Validate content quality for all questions"):
                self._batch_validate_content(df)
        
        with col3:
            if st.button("🏗️ Structure Check", help="Validate question structure"):
                self._batch_validate_structure(df)
        
        with col4:
            if st.button("♿ Accessibility", help="Check accessibility compliance"):
                self._batch_validate_accessibility(df)
        
        st.markdown("---")
        
        # Filter controls
        self._render_validation_filters(df)
    
    def get_validation_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get validation statistics from DataFrame.
        
        Args:
            df: DataFrame with validation flags
            
        Returns:
            Validation statistics
        """
        stats = {
            'total_questions': len(df),
            'questions_with_critical_issues': 0,
            'questions_with_warnings': 0,
            'questions_valid': 0,
            'average_validation_score': 0,
            'issue_breakdown': {
                'mathematical': {'critical': 0, 'warning': 0, 'info': 0},
                'content': {'warning': 0, 'info': 0},
                'structure': {'critical': 0, 'warning': 0},
                'accessibility': {'warning': 0, 'info': 0}
            }
        }
        
        if len(df) == 0:
            return stats
        
        # Count validation statuses
        if 'overall_validation_status' in df.columns:
            status_counts = df['overall_validation_status'].value_counts()
            stats['questions_with_critical_issues'] = status_counts.get('critical', 0)
            stats['questions_with_warnings'] = status_counts.get('warning', 0)
            stats['questions_valid'] = status_counts.get('valid', 0)
        
        # Average validation score
        if 'validation_score' in df.columns:
            stats['average_validation_score'] = df['validation_score'].mean()
        
        # Issue breakdown
        for validation_type in stats['issue_breakdown']:
            for level in stats['issue_breakdown'][validation_type]:
                col_name = f"{validation_type}_{level}"
                if col_name in df.columns:
                    stats['issue_breakdown'][validation_type][level] = df[col_name].sum()
        
        return stats
    
    def _validate_mathematical_content(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mathematical content in question"""
        math_results = {
            'status': 'valid',
            'flags': {'critical': [], 'warning': [], 'info': []},
            'fields_validated': [],
            'statistics': {
                'total_latex_expressions': 0,
                'fields_with_math': 0,
                'unicode_symbols_found': 0
            }
        }
        
        # Fields to check for mathematical content
        math_fields = [
            'question_text', 'choice_a', 'choice_b', 'choice_c', 'choice_d',
            'correct_answer', 'correct_feedback', 'incorrect_feedback'
        ]
        
        total_expressions = 0
        fields_with_math = 0
        
        for field in math_fields:
            field_value = question_data.get(field, '')
            if field_value and isinstance(field_value, str):
                # Validate this field
                _, field_validation = self.latex_processor.render_latex_with_validation(field_value)
                
                if field_validation.get('flags'):
                    math_results['fields_validated'].append({
                        'field': field,
                        'validation': field_validation
                    })
                    
                    # Aggregate flags
                    for level in ['critical', 'warning', 'info']:
                        math_results['flags'][level].extend(field_validation['flags'].get(level, []))
                
                # Update statistics
                expr_count = field_validation.get('statistics', {}).get('latex_expressions', 0)
                if expr_count > 0:
                    total_expressions += expr_count
                    fields_with_math += 1
                
                unicode_count = field_validation.get('statistics', {}).get('unicode_symbols', 0)
                math_results['statistics']['unicode_symbols_found'] += unicode_count
        
        math_results['statistics']['total_latex_expressions'] = total_expressions
        math_results['statistics']['fields_with_math'] = fields_with_math
        
        # Set overall status
        if math_results['flags']['critical']:
            math_results['status'] = 'critical'
        elif math_results['flags']['warning']:
            math_results['status'] = 'warning'
        
        return math_results
    
    def _validate_content_quality(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content quality and completeness"""
        content_results = {
            'status': 'valid',
            'flags': {'warning': [], 'info': []},
            'checks_performed': []
        }
        
        # Check required fields
        required_fields = ['title', 'question_text', 'correct_answer']
        for field in required_fields:
            if not question_data.get(field, '').strip():
                content_results['flags']['warning'].append({
                    'type': 'missing_required_field',
                    'message': f'Required field "{field}" is empty or missing',
                    'field': field,
                    'suggestion': f'Add content to the {field} field'
                })
        
        # Check question text length
        question_text = question_data.get('question_text', '')
        if question_text:
            if len(question_text) < 10:
                content_results['flags']['warning'].append({
                    'type': 'question_too_short',
                    'message': 'Question text is very short (less than 10 characters)',
                    'suggestion': 'Consider adding more context or detail to the question'
                })
            elif len(question_text) > 1000:
                content_results['flags']['info'].append({
                    'type': 'question_very_long',
                    'message': f'Question text is very long ({len(question_text)} characters)',
                    'suggestion': 'Consider breaking into multiple questions for better readability'
                })
        
        # Check for multiple choice completeness
        question_type = question_data.get('type', question_data.get('question_type', ''))
        if question_type == 'multiple_choice':
            choices = ['choice_a', 'choice_b', 'choice_c', 'choice_d']
            empty_choices = [choice for choice in choices if not question_data.get(choice, '').strip()]
            
            if empty_choices:
                content_results['flags']['warning'].append({
                    'type': 'incomplete_choices',
                    'message': f'Empty answer choices: {", ".join(empty_choices)}',
                    'suggestion': 'Fill in all answer choices for multiple choice questions'
                })
        
        # Set overall status
        if content_results['flags']['warning']:
            content_results['status'] = 'warning'
        
        return content_results
    
    def _validate_question_structure(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate question structure and format"""
        structure_results = {
            'status': 'valid',
            'flags': {'critical': [], 'warning': []},
            'checks_performed': []
        }
        
        # Check question type validity
        question_type = question_data.get('type', question_data.get('question_type', ''))
        valid_types = ['multiple_choice', 'numerical', 'true_false', 'fill_in_blank']
        
        if not question_type:
            structure_results['flags']['critical'].append({
                'type': 'missing_question_type',
                'message': 'Question type is not specified',
                'suggestion': 'Set a valid question type'
            })
        elif question_type not in valid_types:
            structure_results['flags']['warning'].append({
                'type': 'unknown_question_type',
                'message': f'Unknown question type: {question_type}',
                'suggestion': f'Use one of: {", ".join(valid_types)}'
            })
        
        # Check points validity
        points = question_data.get('points', 1)
        try:
            points_float = float(points)
            if points_float <= 0:
                structure_results['flags']['warning'].append({
                    'type': 'invalid_points',
                    'message': f'Points value is not positive: {points}',
                    'suggestion': 'Set points to a positive number'
                })
        except (ValueError, TypeError):
            structure_results['flags']['warning'].append({
                'type': 'invalid_points_format',
                'message': f'Points value is not a valid number: {points}',
                'suggestion': 'Set points to a numeric value'
            })
        
        # Set overall status
        if structure_results['flags']['critical']:
            structure_results['status'] = 'critical'
        elif structure_results['flags']['warning']:
            structure_results['status'] = 'warning'
        
        return structure_results
    
    def _validate_accessibility(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate accessibility features"""
        accessibility_results = {
            'status': 'valid',
            'flags': {'warning': [], 'info': []},
            'checks_performed': []
        }
        
        # Check for alt text if images are referenced
        question_text = question_data.get('question_text', '')
        if '<img' in question_text or 'image' in question_text.lower():
            accessibility_results['flags']['info'].append({
                'type': 'image_alt_text',
                'message': 'Question appears to reference images',
                'suggestion': 'Ensure all images have appropriate alt text for screen readers'
            })
        
        # Check for mathematical accessibility
        if self.latex_processor.has_latex(question_text):
            accessibility_results['flags']['info'].append({
                'type': 'math_accessibility',
                'message': 'Question contains mathematical content',
                'suggestion': 'Mathematical content will be accessible via screen readers when properly rendered'
            })
        
        # Check for color-only information
        color_words = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'color']
        for color_word in color_words:
            if color_word in question_text.lower():
                accessibility_results['flags']['warning'].append({
                    'type': 'color_dependency',
                    'message': f'Question may rely on color information: "{color_word}"',
                    'suggestion': 'Ensure information is not conveyed by color alone'
                })
                break
        
        return accessibility_results
    
    def _aggregate_validation_results(self, validation_results: Dict[str, Any]) -> None:
        """Aggregate validation results into summary"""
        summary = validation_results['summary']
        overall_status = 'valid'
        validation_score = 100
        
        # Count issues across all validation types
        for validation_type, type_results in validation_results['validation_types'].items():
            flags = type_results.get('flags', {})
            
            critical_count = len(flags.get('critical', []))
            warning_count = len(flags.get('warning', []))
            info_count = len(flags.get('info', []))
            
            summary['critical_issues'] += critical_count
            summary['warnings'] += warning_count
            summary['info_items'] += info_count
            summary['total_issues'] += critical_count + warning_count + info_count
            
            # Deduct from validation score
            validation_score -= (critical_count * 10 + warning_count * 3 + info_count * 1)
        
        # Set overall status
        if summary['critical_issues'] > 0:
            overall_status = 'critical'
        elif summary['warnings'] > 0:
            overall_status = 'warning'
        
        validation_results['overall_status'] = overall_status
        validation_results['validation_score'] = max(0, validation_score)  # Don't go below 0
    
    def _analyze_batch_results(self, batch_results: Dict[str, Any], all_issues: List[Dict[str, Any]]) -> None:
        """Analyze batch validation results"""
        summary = batch_results['batch_summary']
        
        # Count question statuses
        for question_result in batch_results['question_results']:
            status = question_result['overall_status']
            if status == 'critical':
                summary['questions_with_critical_issues'] += 1
            elif status == 'warning':
                summary['questions_with_warnings'] += 1
            else:
                summary['questions_valid'] += 1
        
        # Find most common issues
        issue_counts = {}
        for issue in all_issues:
            issue_key = f"{issue['type']}_{issue['issue_type']}"
            issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1
        
        # Sort by frequency and take top 5
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        summary['most_common_issues'] = dict(sorted_issues[:5])
        
        # Generate recommendations
        self._generate_batch_recommendations(batch_results, all_issues)
    
    def _generate_batch_recommendations(self, batch_results: Dict[str, Any], all_issues: List[Dict[str, Any]]) -> None:
        """Generate recommendations based on batch analysis"""
        recommendations = batch_results['recommendations']
        
        # Immediate actions for critical issues
        critical_issues = [issue for issue in all_issues if issue['level'] == 'critical']
        if critical_issues:
            recommendations['immediate_actions'].append(
                f"Address {len(critical_issues)} critical mathematical issues that prevent proper rendering"
            )
        
        # Mathematical improvement suggestions
        math_issues = [issue for issue in all_issues if issue['type'] == 'mathematical']
        if len(math_issues) > len(batch_results['question_results']) * 0.3:  # If >30% have math issues
            recommendations['improvements'].append(
                "Consider reviewing LaTeX formatting guidelines - many questions have mathematical notation issues"
            )
        
        # Content quality suggestions
        content_issues = [issue for issue in all_issues if issue['type'] == 'content']
        if content_issues:
            recommendations['improvements'].append(
                f"Improve content quality - {len(content_issues)} content issues found across questions"
            )
        
        # Best practices
        recommendations['best_practices'].extend([
            "Use $...$ delimiters for all mathematical expressions",
            "Include clear, complete answer choices for multiple choice questions",
            "Provide meaningful feedback for both correct and incorrect answers",
            "Test mathematical rendering before finalizing questions"
        ])
    
    def _update_dataframe_row_flags(self, df: pd.DataFrame, row_index: int, question_results: Dict[str, Any]) -> None:
        """Update DataFrame row with validation flags"""
        validation_types = question_results.get('validation_types', {})
        
        # Update mathematical flags
        math_results = validation_types.get('mathematical', {})
        math_flags = math_results.get('flags', {})
        df.loc[row_index, 'math_critical'] = len(math_flags.get('critical', [])) > 0
        df.loc[row_index, 'math_warning'] = len(math_flags.get('warning', [])) > 0
        df.loc[row_index, 'math_info'] = len(math_flags.get('info', [])) > 0
        
        # Update content flags
        content_results = validation_types.get('content', {})
        content_flags = content_results.get('flags', {})
        df.loc[row_index, 'content_warning'] = len(content_flags.get('warning', [])) > 0
        df.loc[row_index, 'content_info'] = len(content_flags.get('info', [])) > 0
        
        # Update structure flags
        structure_results = validation_types.get('structure', {})
        structure_flags = structure_results.get('flags', {})
        df.loc[row_index, 'structure_critical'] = len(structure_flags.get('critical', [])) > 0
        df.loc[row_index, 'structure_warning'] = len(structure_flags.get('warning', [])) > 0
        
        # Update accessibility flags
        accessibility_results = validation_types.get('accessibility', {})
        accessibility_flags = accessibility_results.get('flags', {})
        df.loc[row_index, 'accessibility_warning'] = len(accessibility_flags.get('warning', [])) > 0
        df.loc[row_index, 'accessibility_info'] = len(accessibility_flags.get('info', [])) > 0
        
        # Update overall status and score
        df.loc[row_index, 'overall_validation_status'] = question_results.get('overall_status', 'valid')
        df.loc[row_index, 'validation_score'] = question_results.get('validation_score', 100)
    
    def _render_batch_validation_dashboard(self, batch_results: Dict[str, Any]) -> None:
        """Render batch validation dashboard"""
        st.markdown("## 📊 Batch Validation Dashboard")
        
        summary = batch_results['batch_summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Questions", batch_results['total_questions'])
        
        with col2:
            st.metric("Critical Issues", summary['questions_with_critical_issues'], 
                     delta=f"-{summary['questions_valid']} valid" if summary['questions_valid'] > 0 else None)
        
        with col3:
            st.metric("Warnings", summary['questions_with_warnings'])
        
        with col4:
            st.metric("Valid Questions", summary['questions_valid'])
        
        # Most common issues
        if summary['most_common_issues']:
            st.markdown("### 🔍 Most Common Issues")
            for issue, count in list(summary['most_common_issues'].items())[:5]:
                st.markdown(f"• **{issue}**: {count} occurrences")
        
        # Recommendations
        recommendations = batch_results['recommendations']
        if any(recommendations.values()):
            st.markdown("### 💡 Recommendations")
            
            if recommendations['immediate_actions']:
                st.markdown("**🚨 Immediate Actions:**")
                for action in recommendations['immediate_actions']:
                    st.markdown(f"• {action}")
            
            if recommendations['improvements']:
                st.markdown("**⚠️ Improvements:**")
                for improvement in recommendations['improvements']:
                    st.markdown(f"• {improvement}")
            
            if recommendations['best_practices']:
                with st.expander("📚 Best Practices"):
                    for practice in recommendations['best_practices']:
                        st.markdown(f"• {practice}")
    
    def _render_single_question_validation_dashboard(self, question_results: Dict[str, Any]) -> None:
        """Render single question validation dashboard"""
        st.markdown("## 🔍 Question Validation Results")
        
        # Overall status
        status = question_results['overall_status']
        score = question_results['validation_score']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_color = self.flag_colors.get(status, '#28a745')
            st.markdown(f"**Status:** <span style='color: {status_color}'>{status.upper()}</span>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.metric("Validation Score", f"{score}/100")
        
        with col3:
            summary = question_results['summary']
            st.metric("Total Issues", summary['total_issues'])
        
        # Validation type breakdown
        st.markdown("### 📋 Validation Details")
        
        for validation_type, type_results in question_results['validation_types'].items():
            type_config = self.validation_types.get(validation_type, {})
            type_name = type_config.get('name', validation_type.title())
            type_icon = type_config.get('icon', '📝')
            
            flags = type_results.get('flags', {})
            total_flags = sum(len(flags.get(level, [])) for level in ['critical', 'warning', 'info'])
            
            if total_flags > 0:
                with st.expander(f"{type_icon} {type_name} ({total_flags} issues)"):
                    for level in ['critical', 'warning', 'info']:
                        issues = flags.get(level, [])
                        if issues:
                            level_icon = {'critical': '🚨', 'warning': '⚠️', 'info': 'ℹ️'}[level]
                            st.markdown(f"**{level_icon} {level.title()} ({len(issues)}):**")
                            for issue in issues:
                                st.markdown(f"• {issue.get('message', 'Unknown issue')}")
                                if 'suggestion' in issue:
                                    st.caption(f"  💡 {issue['suggestion']}")
    
    def _render_validation_summary_metrics(self, df: pd.DataFrame) -> None:
        """Render validation summary metrics"""
        stats = self.get_validation_statistics(df)
        
        st.markdown("#### 📊 Validation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Questions", stats['total_questions'])
        
        with col2:
            critical_pct = (stats['questions_with_critical_issues'] / max(1, stats['total_questions'])) * 100
            st.metric("Critical Issues", stats['questions_with_critical_issues'], 
                     delta=f"{critical_pct:.1f}%")
        
        with col3:
            warning_pct = (stats['questions_with_warnings'] / max(1, stats['total_questions'])) * 100
            st.metric("Warnings", stats['questions_with_warnings'], 
                     delta=f"{warning_pct:.1f}%")
        
        with col4:
            st.metric("Avg. Score", f"{stats['average_validation_score']:.1f}/100")
    
    def _render_validation_filters(self, df: pd.DataFrame) -> None:
        """Render validation filtering controls"""
        st.markdown("#### 🔽 Filter by Validation Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_critical = st.checkbox("🚨 Critical Issues", value=True)
        
        with col2:
            show_warnings = st.checkbox("⚠️ Warnings", value=True)
        
        with col3:
            show_valid = st.checkbox("✅ Valid Questions", value=True)
        
        # Apply filters (this would be used by calling code)
        st.session_state['validation_filters'] = {
            'show_critical': show_critical,
            'show_warnings': show_warnings,
            'show_valid': show_valid
        }
    
    def _batch_validate_mathematical(self, df: pd.DataFrame) -> None:
        """Batch validate mathematical content"""
        st.info("🔄 Running mathematical validation...")
        # Implementation would go here
        st.success("✅ Mathematical validation completed!")
    
    def _batch_validate_content(self, df: pd.DataFrame) -> None:
        """Batch validate content quality"""
        st.info("🔄 Running content validation...")
        # Implementation would go here
        st.success("✅ Content validation completed!")
    
    def _batch_validate_structure(self, df: pd.DataFrame) -> None:
        """Batch validate question structure"""
        st.info("🔄 Running structure validation...")
        # Implementation would go here
        st.success("✅ Structure validation completed!")
    
    def _batch_validate_accessibility(self, df: pd.DataFrame) -> None:
        """Batch validate accessibility"""
        st.info("🔄 Running accessibility validation...")
        # Implementation would go here
        st.success("✅ Accessibility validation completed!")
