# utils/question_type_filter.py
import streamlit as st

class QuestionTypeFilter:
    """Robust question type selection system using multi-filter pattern"""
    
    def __init__(self):
        self.available_types = [
            {"name": "Multiple Choice", "code": "multiple_choice", "emoji": "🔘", "desc": "Single correct answer from options"},
            {"name": "True/False", "code": "true_false", "emoji": "✅", "desc": "Binary true or false questions"},
            {"name": "Numerical", "code": "numerical", "emoji": "🔢", "desc": "Exact numerical answers"},
            {"name": "Short Answer", "code": "short_answer", "emoji": "✍️", "desc": "Brief text responses"},
            {"name": "Essay", "code": "essay", "emoji": "📝", "desc": "Extended written responses"},
            {"name": "Fill in the Blank", "code": "fill_blank", "emoji": "⬜", "desc": "Complete missing text"}
        ]
    
    def render_question_type_selector(self):
        """Enhanced question type selection using robust filter pattern"""
        
        st.subheader("🎯 Question Type Selection")
        
        # Instructions
        st.markdown("""
        **Instructions:**
        - ✅ **Selected types** will be included in your prompt
        - ❌ **Uncheck types** to exclude them  
        - 🔍 **Use this to focus** on specific question formats
        """)
        
        # Reset handling (BEFORE widget creation)
        reset_key = "reset_question_types_requested"
        if st.session_state.get(reset_key, False):
            # Clear widget session state
            for key in list(st.session_state.keys()):
                if key == "enhanced_question_types_multiselect":
                    del st.session_state[key]
            st.session_state[reset_key] = False
            st.rerun()
        
        # Dynamic widget with counter-based key
        counter_key = "question_types_reset_counter"
        reset_counter = st.session_state.get(counter_key, 0)
        widget_key = f"enhanced_question_types_multiselect_{reset_counter}"
        
        # Prepare options for multiselect
        type_options = [f"{q_type['emoji']} {q_type['name']}" for q_type in self.available_types]
        type_descriptions = {f"{q_type['emoji']} {q_type['name']}": q_type['desc'] for q_type in self.available_types}
        
        # Default selection (first 3 most common types)
        default_selection = type_options[:3]  # Multiple Choice, True/False, Numerical
        
        selected_types = st.multiselect(
            "Choose question types to include:",
            options=type_options,
            default=default_selection,
            key=widget_key,
            help="💡 Tip: Select multiple types for variety, or focus on specific types"
        )
        
        # Show descriptions for selected types
        if selected_types:
            st.markdown("**Selected Question Types:**")
            for selected in selected_types:
                desc = type_descriptions.get(selected, "")
                st.markdown(f"- {selected}: *{desc}*")
        
        # Reset button (AFTER widget)
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Reset Types", key="reset_question_types_btn"):
                st.session_state[counter_key] = reset_counter + 1
                st.session_state[reset_key] = True
                st.rerun()
        
        # Status feedback
        if selected_types:
            excluded_count = len(type_options) - len(selected_types)
            if excluded_count > 0:
                st.info(f"✅ {len(selected_types)} question types selected\n📋 {excluded_count} types excluded")
            else:
                st.success(f"✅ All {len(type_options)} question types selected")
        else:
            st.warning("⚠️ No question types selected - please choose at least one")
        
        return self._process_selected_types(selected_types)
    
    def _process_selected_types(self, selected_display_names):
        """Convert display names back to structured data"""
        if not selected_display_names:
            return []
        
        selected_types = []
        for display_name in selected_display_names:
            # Extract the name part (remove emoji)
            clean_name = display_name.split(' ', 1)[1] if ' ' in display_name else display_name
            
            # Find matching type data
            for q_type in self.available_types:
                if q_type['name'] == clean_name:
                    selected_types.append(q_type)
                    break
        
        return selected_types
    
    def render_question_count_selector(self):
        """Enhanced question count selection"""
        
        st.subheader("📊 Question Quantity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            question_count = st.selectbox(
                "Total Number of Questions:",
                [5, 10, 15, 20, 25, 30],
                index=1,  # Default to 10
                help="How many questions should the AI generate in total?"
            )
        
        with col2:
            distribution_mode = st.selectbox(
                "Type Distribution:",
                ["Even distribution", "Weighted by complexity", "Custom ratios"],
                index=0,
                help="How should questions be distributed across selected types?"
            )
        
        return question_count, distribution_mode
    
    def generate_type_instructions(self, selected_types, question_count, distribution_mode):
        """Generate AI instructions based on selected types and distribution"""
        
        if not selected_types:
            return "Generate mixed question types"
        
        if len(selected_types) == 1:
            # Single type selected
            type_name = selected_types[0]['name']
            return f"Generate {question_count} {type_name.lower()} questions"
        
        # Multiple types selected
        type_names = [q_type['name'] for q_type in selected_types]
        
        if distribution_mode == "Even distribution":
            count_per_type = question_count // len(selected_types)
            remainder = question_count % len(selected_types)
            
            instructions = f"Generate {question_count} questions distributed as follows:\n"
            for i, q_type in enumerate(selected_types):
                count = count_per_type + (1 if i < remainder else 0)
                instructions += f"- {count} {q_type['name'].lower()} questions\n"
            
            return instructions.strip()
        
        elif distribution_mode == "Weighted by complexity":
            return f"Generate {question_count} questions using these types with more complex types having fewer questions: {', '.join(type_names)}"
        
        else:  # Custom ratios
            return f"Generate {question_count} questions using a mix of: {', '.join(type_names)}"
    
    def render_complete_question_configuration(self):
        """Complete question configuration section using the filter pattern"""
        
        # Question type selection
        selected_types = self.render_question_type_selector()
        
        st.markdown("---")
        
        # Question count and distribution
        question_count, distribution_mode = self.render_question_count_selector()
        
        # Generate instructions
        type_instructions = self.generate_type_instructions(selected_types, question_count, distribution_mode)
        
        # Show preview of what will be generated
        if selected_types:
            with st.expander("📋 Preview Generated Instructions"):
                st.code(type_instructions)
                st.markdown("*This is what will be included in your AI prompt*")
        
        return {
            'selected_types': selected_types,
            'question_count': question_count,
            'distribution_mode': distribution_mode,
            'type_instructions': type_instructions,
            'valid_selection': len(selected_types) > 0
        }
