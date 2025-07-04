#!/usr/bin/env python3
"""
Test Streamlit components for Stage 4 UI issue
"""

import json
import sys
import os
import streamlit as st

# Add paths for imports
sys.path.append('.')
sys.path.append('modules')

def test_streamlit_components():
    """Test Streamlit components directly"""
    
    # Load test data
    test_file = r"c:\Users\aknoesen\Documents\Knoesen\Database for EEC1\Debug Problem Cases\MosfetQQDebug.json"
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    st.title("Stage 4 UI Diagnostic - Streamlit Components")
    
    # Test 1: Raw data display
    st.header("Test 1: Raw JSON Data")
    questions = test_data.get('questions', [])
    
    if questions:
        first_question = questions[0]
        st.write(f"**Question Title:** {first_question.get('title', 'No title')}")
        st.write(f"**Question Type:** {first_question.get('type', 'No type')}")
        
        choices = first_question.get('choices', [])
        st.write(f"**Choices Count:** {len(choices)}")
        
        if choices:
            st.write("**Choices:**")
            for i, choice in enumerate(choices):
                st.write(f"  {i+1}. {choice}")
        else:
            st.error("No choices found!")
        
        st.json(first_question)
    
    # Test 2: Session state simulation
    st.header("Test 2: Session State Simulation")
    
    # Initialize session state
    if 'test_questions' not in st.session_state:
        st.session_state.test_questions = questions
    
    stored_questions = st.session_state.test_questions
    st.write(f"Questions in session state: {len(stored_questions)}")
    
    if stored_questions:
        first_stored = stored_questions[0]
        stored_choices = first_stored.get('choices', [])
        st.write(f"Choices in session state: {len(stored_choices)}")
        
        if stored_choices:
            st.success("✅ Choices preserved in session state")
        else:
            st.error("❌ Choices lost in session state!")
    
    # Test 3: Component rendering
    st.header("Test 3: Component Rendering")
    
    try:
        # Test question selector
        if stored_questions:
            question_idx = st.selectbox(
                "Select Question",
                range(len(stored_questions)),
                format_func=lambda x: f"Question {x + 1}: {stored_questions[x].get('title', 'Untitled')[:50]}..."
            )
            
            selected_question = stored_questions[question_idx]
            
            st.write("**Selected Question:**")
            st.write(f"Title: {selected_question.get('title', 'No title')}")
            st.write(f"Type: {selected_question.get('type', 'No type')}")
            
            # Display choices
            selected_choices = selected_question.get('choices', [])
            st.write(f"**Choices ({len(selected_choices)}):**")
            
            if selected_choices:
                for i, choice in enumerate(selected_choices):
                    st.write(f"  {i+1}. {choice}")
                st.success("✅ Choices displayed successfully")
            else:
                st.error("❌ No choices to display")
                
            # Show raw JSON
            st.subheader("Raw Question Data")
            st.json(selected_question)
        
    except Exception as e:
        st.error(f"Error in component rendering: {e}")
        st.exception(e)
    
    # Test 4: Q2JSON components
    st.header("Test 4: Q2JSON Components")
    
    try:
        from modules.latex_processor import Q2JSONLaTeXProcessor
        from modules.question_renderer import Q2JSONQuestionRenderer
        
        latex_processor = Q2JSONLaTeXProcessor()
        question_renderer = Q2JSONQuestionRenderer(latex_processor)
        
        st.success("✅ Q2JSON components imported successfully")
        
        if stored_questions:
            first_question = stored_questions[0]
            try:
                rendered = question_renderer.render_question(first_question)
                st.success("✅ Question rendered successfully")
                st.write(f"Rendered type: {type(rendered)}")
                
                # Try to display rendered content
                if hasattr(rendered, 'choices'):
                    st.write("Choices in rendered object:")
                    st.write(rendered.choices)
                else:
                    st.write("Rendered content:")
                    st.write(str(rendered)[:500] + "...")
                    
            except Exception as e:
                st.error(f"Error rendering question: {e}")
                st.exception(e)
        
    except ImportError as e:
        st.error(f"Could not import Q2JSON components: {e}")
    except Exception as e:
        st.error(f"Error with Q2JSON components: {e}")
        st.exception(e)

if __name__ == "__main__":
    test_streamlit_components()