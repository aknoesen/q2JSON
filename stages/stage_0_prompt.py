# stages/stage_0_prompt.py
import streamlit as st
from pathlib import Path
from navigation.manager import NavigationManager
from utils.question_type_filter import QuestionTypeFilter
from utils.ui_helpers import show_stage_banner

def render_prompt_builder():
    """Render the complete Prompt Builder stage"""
    
    # Progress indicator
    progress = (st.session_state.current_stage + 1) / 4
    st.progress(progress)
    st.markdown(f"**Stage {st.session_state.current_stage + 1} of 4**: Prompt Builder")

    st.header("🎯 Build Your AI Prompt")
    
    # Stage description
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Create optimized prompts for AI question generation")
    with col2:
        st.metric("Stage", "1 of 4")
    
    # Compatible AI Providers
    render_ai_providers_info()
    
    # Educational Context Section
    educational_context = render_educational_context()
    
    # Enhanced Question Configuration using filter system
    question_filter = QuestionTypeFilter()
    question_config = question_filter.render_complete_question_configuration()
    
    # Advanced Options
    difficulty_level, include_explanations, custom_instructions = render_advanced_options()
    
    # Generate Prompt (only if valid selection)
    if question_config['valid_selection']:
        if st.button("🎯 Generate Complete Prompt", type="primary", use_container_width=True):
            generate_complete_prompt_enhanced(
                educational_context, 
                question_config, 
                difficulty_level, 
                include_explanations, 
                custom_instructions
            )
    else:
        st.button("🎯 Generate Complete Prompt", type="primary", use_container_width=True, disabled=True)
        st.warning("⚠️ Please select at least one question type before generating the prompt")
    
    # Display Generated Prompt
    display_generated_prompt()

    show_stage_banner(st.session_state.current_stage, total_stages=4)


def render_ai_providers_info():
    """Display compatible AI providers information"""
    st.subheader("🤖 Compatible AI Providers")
    st.info("✨ This prompt works with: **ChatGPT, Claude, Copilot, Gemini**, and other LLMs")
    st.markdown("*No configuration needed - the same prompt works universally across all AI providers*")


def render_educational_context():
    """Render educational context input section"""
    st.subheader("📚 Educational Context")
    
    context_option = st.radio(
        "Choose how to input your educational context:",
        ["🎯 Use Example", "📝 Use Template", "✍️ Write Custom"],
        horizontal=True
    )
    
    if context_option == "🎯 Use Example":
        educational_context = st.text_area(
            "Educational Context:",
            value="You are an expert in antennas, and teaching a lecture. The topic is patch antennas and implementation on PCB, polarization characteristics are of particular interest.",
            height=120,
            help="This is a working example from antenna theory"
        )
    elif context_option == "📝 Use Template":
        educational_context = st.text_area(
            "Educational Context:",
            value="You are an expert in [SUBJECT], and teaching a lecture. The topic is [TOPIC], [SPECIFIC_FOCUS] are of particular interest.",
            height=120,
            help="Fill in the brackets with your specific subject matter"
        )
    else:  # Write Custom
        educational_context = st.text_area(
            "Educational Context:",
            placeholder="Enter your educational context here...\n\nExample: You are an expert in calculus, teaching derivatives. Focus on practical applications and common student misconceptions.",
            height=120,
            help="Describe your subject area, teaching context, and specific focus"
        )
    
    return educational_context


def render_question_configuration():
    """Legacy function - now replaced by QuestionTypeFilter"""
    # This function is kept for compatibility but is no longer used
    # The new enhanced system is in QuestionTypeFilter.render_complete_question_configuration()
    pass


def generate_complete_prompt_enhanced(educational_context, question_config, 
                                    difficulty_level, include_explanations, custom_instructions):
    """Enhanced prompt generation using the new question type system"""
    if educational_context.strip():
        with st.spinner("Generating optimized prompt..."):
            # Load templates
            preamble, postamble, template_source = load_template_files()
            
            # Build complete prompt
            prompt_parts = []
            prompt_parts.append(preamble)
            prompt_parts.append(f"\n\n{educational_context}")
            
            # Use the enhanced type instructions
            prompt_parts.append(f"\n\n{question_config['type_instructions']}")
            
            if difficulty_level != "Mixed":
                prompt_parts.append(f"\nDifficulty level: {difficulty_level}")
            
            if include_explanations:
                prompt_parts.append("\nInclude detailed explanations for both correct and incorrect answers")
            
            if custom_instructions.strip():
                prompt_parts.append(f"\nAdditional requirements: {custom_instructions}")
            
            prompt_parts.append(f"\n\n{postamble}")
            
            complete_prompt = "".join(prompt_parts)
            
            # Store enhanced config in session state
            st.session_state.generated_prompt = complete_prompt
            st.session_state.prompt_config = {
                'question_count': question_config['question_count'],
                'selected_types': [q_type['name'] for q_type in question_config['selected_types']],
                'distribution_mode': question_config['distribution_mode'],
                'difficulty': difficulty_level,
                'explanations': include_explanations,
                'type_instructions': question_config['type_instructions']
            }
            
        st.success("✅ Enhanced prompt generated successfully!")
        st.info(template_source)
        
        # Show summary of configuration
        with st.expander("📋 Prompt Configuration Summary"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Question Types:**")
                for q_type in question_config['selected_types']:
                    st.markdown(f"- {q_type['emoji']} {q_type['name']}")
            with col2:
                st.markdown("**Settings:**")
                st.markdown(f"- **Count:** {question_config['question_count']}")
                st.markdown(f"- **Distribution:** {question_config['distribution_mode']}")
                st.markdown(f"- **Difficulty:** {difficulty_level}")
                st.markdown(f"- **Explanations:** {'Yes' if include_explanations else 'No'}")
    else:
        st.error("❌ Please provide educational context before generating prompt")


def render_advanced_options():
    """Render advanced options section"""
    with st.expander("🔧 Advanced Options"):
        difficulty_level = st.select_slider(
            "Difficulty Level:",
            options=["Beginner", "Intermediate", "Advanced", "Mixed"],
            value="Intermediate"
        )
        
        include_explanations = st.checkbox(
            "Include explanations for correct answers",
            value=True,
            help="Add detailed explanations to help students understand"
        )
        
        custom_instructions = st.text_area(
            "Additional Instructions (Optional):",
            placeholder="Any specific requirements or constraints...",
            height=80
        )
    
    return difficulty_level, include_explanations, custom_instructions


def generate_complete_prompt(educational_context, question_count, question_type, 
                           difficulty_level, include_explanations, custom_instructions):
    """Generate the complete AI prompt"""
    if educational_context.strip():
        with st.spinner("Generating optimized prompt..."):
            # Load templates
            preamble, postamble, template_source = load_template_files()
            
            # Build complete prompt
            prompt_parts = []
            prompt_parts.append(preamble)
            prompt_parts.append(f"\n\n{educational_context}")
            prompt_parts.append(f"\n\nGenerate {question_count} questions of type: {question_type.lower()}")
            
            if difficulty_level != "Mixed":
                prompt_parts.append(f"\nDifficulty level: {difficulty_level}")
            
            if include_explanations:
                prompt_parts.append("\nInclude detailed explanations for both correct and incorrect answers")
            
            if custom_instructions.strip():
                prompt_parts.append(f"\nAdditional requirements: {custom_instructions}")
            
            prompt_parts.append(f"\n\n{postamble}")
            
            complete_prompt = "".join(prompt_parts)
            
            # Store in session state
            st.session_state.generated_prompt = complete_prompt
            st.session_state.prompt_config = {
                'question_count': question_count,
                'question_type': question_type,
                'difficulty': difficulty_level,
                'explanations': include_explanations
            }
            
        st.success("✅ Prompt generated successfully!")
        st.info(template_source)
    else:
        st.error("❌ Please provide educational context before generating prompt")


def display_generated_prompt():
    """Display the generated prompt and next steps with enhanced configuration support"""
    if 'generated_prompt' in st.session_state and st.session_state.generated_prompt:
        st.subheader("📋 Generated Prompt")
        
        # Show prompt configuration (support both old and new format)
        if 'prompt_config' in st.session_state:
            config = st.session_state.prompt_config
            
            # Handle enhanced configuration format
            if 'selected_types' in config:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Questions", config['question_count'])
                with col2:
                    type_display = f"{len(config['selected_types'])} types" if len(config['selected_types']) > 1 else config['selected_types'][0]
                    st.metric("Types", type_display)
                with col3:
                    st.metric("Difficulty", config['difficulty'])
                
                # Show selected types in detail
                with st.expander("📊 Question Type Breakdown"):
                    st.markdown("**Selected Types:**")
                    for q_type in config['selected_types']:
                        st.markdown(f"- {q_type}")
                    st.markdown(f"**Distribution:** {config['distribution_mode']}")
            else:
                # Handle legacy configuration format
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Questions", config['question_count'])
                with col2:
                    st.metric("Type", config['question_type'])
                with col3:
                    st.metric("Difficulty", config['difficulty'])
        
        # Display the prompt
        st.text_area(
            "Complete Prompt (Ready for AI):",
            st.session_state.generated_prompt,
            height=250,
            help="Copy this entire prompt and paste it into your chosen AI"
        )

        # Next steps
        render_next_steps()


def render_next_steps():
    """Render next steps instructions"""
    st.subheader("📋 Your Next Steps")

    # Step 1: Get the prompt
    st.markdown("### Step 1: Get Your Prompt")
    
    prompt_method = st.radio(
        "How would you like to get your prompt?",
        ["💾 Download as file", "📋 Copy to clipboard"],
        horizontal=True,
        key="prompt_method"
    )

    if prompt_method == "💾 Download as file":
        render_download_option()
    elif prompt_method == "📋 Copy to clipboard":
        render_copy_option()

    # Step 2: Use with AI
    st.markdown("### Step 2: Use Prompt with Your AI")
    st.info("""
🚀 **IMPORTANT**: Take the prompt above to your chosen AI:
- 🌐 **ChatGPT**: Open ChatGPT and paste the prompt
- 🤖 **Copilot**: Open Microsoft Copilot and paste the prompt  
- 🧠 **Claude**: Open Claude and paste the prompt
- ✨ **Gemini**: Open Google Gemini and paste the prompt

⏳ **Wait for the AI to generate your questions**, then copy the complete response.
""")

    # Step 3: Continue to next stage
    st.markdown("### Step 3: Return with AI Response")
    if st.session_state.get("generated_prompt"):
        NavigationManager.create_navigation_selector(
            target_stage=1,
            label="✅ I Have AI Response - Continue"
        )
    st.markdown("---")
    st.warning("⚠️ **Don't skip Step 2!** Use the prompt with AI first.")


def render_download_option():
    """Render download file option"""
    file_name = st.text_input(
        "Prompt filename:",
        value="my_prompt",
        help="Enter filename (we'll add .txt automatically)",
        key="prompt_filename"
    )
    
    if file_name.strip():
        clean_name = file_name.strip().replace(" ", "_")
        clean_name = "".join(c for c in clean_name if c.isalnum() or c in ('_', '-'))
        if not clean_name:
            clean_name = "prompt"
        
        final_prompt_filename = f"{clean_name}.txt"
        st.info(f"📁 Will save as: **{final_prompt_filename}**")
        
        st.download_button(
            "💾 Download Prompt File",
            st.session_state.generated_prompt,
            file_name=final_prompt_filename,
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )
    else:
        st.warning("⚠️ Enter a filename above")


def render_copy_option():
    """Render copy to clipboard option"""
    st.text_area(
        "Select all and copy (Ctrl+A, then Ctrl+C):",
        st.session_state.generated_prompt,
        height=150,
        key="prompt_copy_area"
    )
    
    if st.button("✅ I Copied the Text", use_container_width=True, type="primary"):
        st.success("🎉 Great! Now paste it into your AI")


def load_template_files():
    """Load preamble and postamble template files"""
    try:
        preamble_path = Path('templates/preamble_default.txt')
        postamble_path = Path('templates/postamble_default.txt')
        
        if preamble_path.exists() and postamble_path.exists():
            with open(preamble_path, 'r', encoding='utf-8') as f:
                preamble = f.read()
            with open(postamble_path, 'r', encoding='utf-8') as f:
                postamble = f.read()
            return preamble, postamble, "✅ Using your actual template files"
        else:
            return get_fallback_templates()
    except Exception as e:
        return get_fallback_templates()


def get_fallback_templates():
    """Fallback templates if files are not found"""
    preamble = """You are an expert educator and question writer. Your task is to create high-quality educational questions based on the context provided below.

Please follow these guidelines:
1. Create questions that test understanding, not just memorization
2. Use clear, unambiguous language appropriate for the educational level
3. Include realistic and plausible distractors for multiple choice questions
4. Ensure questions are directly related to the learning objectives
5. Vary question difficulty from basic recall to higher-order thinking
6. Format your response as valid JSON only (no additional text)

Educational Context and Requirements:"""
    
    postamble = """

IMPORTANT: Format your response as a JSON object with this EXACT structure:

{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Descriptive Title for Question",
      "question_text": "The complete question text goes here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "points": 2,
      "feedback_correct": "Explanation for correct answer",
      "feedback_incorrect": "General feedback for incorrect answers"
    }
  ]
}

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON (no markdown, no explanations)
- Use exact field names as shown above
- Ensure all questions are complete and properly formatted
- Double-check JSON syntax is correct"""
    
    return preamble, postamble, "⚠️ Using fallback templates (templates/ directory not found)"