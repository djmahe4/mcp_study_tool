import streamlit as st
import mcp_study
import pathlib
import subprocess

def main():
    st.set_page_config(page_title="Dynamic AI Study Companion", layout="wide")

    if 'subject_structure' not in st.session_state:
        st.session_state.subject_structure = mcp_study.load_subject_structure()

    if not st.session_state.subject_structure:
        display_setup_wizard()
    else:
        display_study_hub()

def display_setup_wizard():
    st.title("📚 Setup Your First Study Module")
    with st.form("setup_form"):
        subject_name = st.text_input("Subject Name", placeholder="e.g., Physics")
        module_name = st.text_input("Module Name", placeholder="e.g., Kinematics")
        syllabus_text = st.text_area("Paste Module Syllabus Here", height=200)
        submitted = st.form_submit_button("Initialize Module")

        if submitted and subject_name and module_name and syllabus_text:
            mcp_study.initialize_module(subject_name, module_name, syllabus_text)
            st.session_state.subject_structure = mcp_study.load_subject_structure()
            st.rerun()

def display_study_hub():
    st.sidebar.title("🎓 Study Hub")
    
    subjects = list(st.session_state.subject_structure.keys())
    selected_subject = st.sidebar.selectbox("Select Subject", subjects)

    if selected_subject:
        st.sidebar.markdown("---")
        if st.sidebar.button("🚀 Launch Web Dev App"):
            launch_web_dev_app(selected_subject)

        modules = list(st.session_state.subject_structure[selected_subject]["modules"].keys())
        if modules:
            selected_module = st.sidebar.selectbox("Select Module", modules)
            
            if selected_module:
                st.sidebar.markdown("---")
                if st.sidebar.button(f"🚀 Launch {selected_module} App"):
                    launch_module_app(selected_subject, selected_module)
        else:
            st.warning("No modules found. Add a new module below.")

    with st.sidebar.expander("Add New Module"):
        with st.form("new_module_form"):
            new_module_subject = st.selectbox("Subject", subjects, index=subjects.index(selected_subject) if selected_subject in subjects else 0)
            new_module_name = st.text_input("New Module Name")
            new_syllabus = st.text_area("Syllabus for New Module")
            if st.form_submit_button("Create New Module"):
                if new_module_name and new_syllabus:
                    mcp_study.initialize_module(new_module_subject, new_module_name, new_syllabus)
                    st.session_state.subject_structure = mcp_study.load_subject_structure()
                    st.rerun()
                else:
                    st.error("Please provide a name and syllabus for the new module.")

    st.markdown("## Welcome to the Dynamic AI Study Companion!")
    st.markdown("Select a subject and module from the sidebar to launch a dedicated learning app.")

def launch_module_app(subject_name, module_name):
    app_path = pathlib.Path("subjects") / subject_name / module_name / f"{module_name}_app.py"
    if app_path.exists():
        try:
            subprocess.Popen(["streamlit", "run", str(app_path)])
            st.success(f"Launching {module_name} app in a new tab...")
        except Exception as e:
            st.error(f"Failed to launch module app: {e}")
    else:
        st.error(f"Module app not found at: {app_path}")

def launch_web_dev_app(subject_name):
    app_path = pathlib.Path("subjects") / subject_name / f"{subject_name}_web_dev.py"
    if app_path.exists():
        try:
            subprocess.Popen(["streamlit", "run", str(app_path)])
            st.success(f"Launching {subject_name} web dev app in a new tab...")
        except Exception as e:
            st.error(f"Failed to launch web dev app: {e}")
    else:
        st.error(f"Web dev app not found at: {app_path}")

if __name__ == "__main__":
    main()