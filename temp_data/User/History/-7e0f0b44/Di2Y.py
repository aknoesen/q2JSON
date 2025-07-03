# navigation/manager.py
import streamlit as st
import time

class NavigationManager:
    """Centralized navigation and stage management for the q2JSON Streamlit app."""

    STAGE_MIN = 0
    STAGE_MAX = 3
    STAGES = {
        0: "Prompt Builder",
        1: "AI Processing",
        2: "JSON Validation & Export",
        3: "Human Review & Editing"
    }
    REQUIRED_KEYS = [
        "current_stage",
        "navigation_timestamp",
        "generated_prompt",
        "raw_extracted_json"
    ]

    @staticmethod
    def can_advance_to_stage(target_stage):
        """
        Returns (bool, error_message) indicating if navigation to target_stage is allowed.
        Allows backward navigation and staying on the same stage unconditionally.
        Only applies requirements when moving forward.
        """
        current_stage = st.session_state.get("current_stage", 0)
        if target_stage < current_stage:
            return True, ""
        if target_stage == current_stage:
            return True, ""
        # Only apply requirements when moving forward
        if target_stage == 1:
            if not st.session_state.get("generated_prompt"):
                return False, "You must generate a prompt before proceeding to AI Processing."
        if target_stage == 2:
            if not st.session_state.get("raw_extracted_json"):
                return False, "You must process and extract JSON before proceeding to Validation."
        if not (NavigationManager.STAGE_MIN <= target_stage <= NavigationManager.STAGE_MAX):
            return False, f"Target stage {target_stage} is out of bounds."
        return True, ""

    @staticmethod
    def advance_stage(target_stage, source="selector"):
        """Advance to target stage with validation"""
        can_advance, error_msg = NavigationManager.can_advance_to_stage(target_stage)
        if not can_advance:
            st.error(error_msg)
            return
        
        st.session_state.current_stage = target_stage
        st.session_state.navigation_timestamp = time.time()
        st.session_state["navigation_source"] = source
        st.rerun()

    @staticmethod
    def create_navigation_selector(target_stage, label, disabled=False):
        """
        Navigation selector using a selectbox instead of a button.
        Returns True if navigation was triggered.
        """
        can_advance, error_msg = NavigationManager.can_advance_to_stage(target_stage)
        selector_key = f"nav_selector_to_{target_stage}"
        options = ["Stay Here", "Continue"]
        help_text = None

        if disabled or not can_advance:
            help_text = error_msg if not can_advance else "Navigation is disabled."
            st.warning(help_text)
            st.selectbox(
                label,
                options,
                index=0,
                key=selector_key,
                disabled=True,
                help=help_text
            )
            return False

        selection = st.selectbox(
            label,
            options,
            index=0,
            key=selector_key,
            help=help_text
        )

        if selection == "Continue":
            NavigationManager.advance_stage(target_stage, source="selector")
            return True
        return False

    @staticmethod
    def create_manual_navigation():
        """Create manual navigation in sidebar"""
        st.sidebar.markdown("### 🔧 Manual Navigation")
        current_stage = st.session_state.get("current_stage", 0)
        st.sidebar.write(f"Current: **{NavigationManager.STAGES.get(current_stage, 'Unknown')}**")
        
        stage_options = list(NavigationManager.STAGES.keys())
        def format_stage(x):
            return f"Stage {x+1}: {NavigationManager.STAGES[x]}"
        
        selected_stage = st.sidebar.selectbox(
            "Jump to stage:",
            stage_options,
            index=current_stage,
            format_func=format_stage,
            key="manual_nav_select"
        )
        
        if selected_stage != current_stage:
            if st.sidebar.button("🚀 Force Navigate", key=f"force_nav_btn_{current_stage}_to_{selected_stage}"):
                st.sidebar.warning(f"Forcing navigation to Stage {selected_stage+1}: {NavigationManager.STAGES[selected_stage]}")
                
                # Update navigation history
                nav_hist = st.session_state.get("navigation_history", [])
                nav_hist.append({
                    "from": current_stage,
                    "to": selected_stage,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state["navigation_history"] = nav_hist[-5:]
                st.session_state.current_stage = selected_stage
                st.session_state.navigation_timestamp = time.time()
                st.rerun()

    @staticmethod
    def create_debug_info():
        """Create debug information in sidebar"""
        debug = st.sidebar.checkbox("🔍 Debug Navigation")
        if debug:
            st.sidebar.markdown("### Navigation Debug Info")
            current_stage = st.session_state.get("current_stage", 0)
            navigation_timestamp = st.session_state.get("navigation_timestamp", None)
            navigation_source = st.session_state.get("navigation_source", "N/A")
            generated_prompt = st.session_state.get("generated_prompt", "")
            raw_extracted_json = st.session_state.get("raw_extracted_json", "")
            
            st.sidebar.write(f"**current_stage**: {current_stage}")
            st.sidebar.write(f"**navigation_timestamp**: {navigation_timestamp}")
            st.sidebar.write(f"**last_navigation_source**: {navigation_source}")
            st.sidebar.write(f"**has_generated_prompt**: {bool(str(generated_prompt).strip())}")
            st.sidebar.write(f"**has_raw_extracted_json**: {bool(str(raw_extracted_json).strip())}")

    @staticmethod
    def create_emergency_reset():
        """Create emergency reset functionality"""
        with st.sidebar.expander("🚨 Emergency Reset", expanded=False):
            st.warning("⚠️ This will clear all progress and start over")
            if st.sidebar.button("🔄 Reset All Progress", key=f"emergency_reset_{st.session_state.current_stage}"):
                st.session_state.current_stage = 0
                st.session_state.generated_prompt = None
                st.session_state.raw_extracted_json = None
                st.session_state.questions_data = None
                st.success("🔄 Reset complete!")
                st.rerun()