import streamlit as st
import mcp_study
import os
import pathlib

def main():
    st.set_page_config(page_title="Gemini Study Companion v3", layout="wide")

    # Initialize session state
    if 'subjects' not in st.session_state:
        st.session_state.subjects = mcp_study.load_subjects()
    if 'selected_subject' not in st.session_state:
        st.session_state.selected_subject = None
    if 'topics' not in st.session_state:
        st.session_state.topics = []
    if 'active_content' not in st.session_state:
        st.session_state.active_content = None

    # Main App Router
    if not st.session_state.subjects:
        display_setup_wizard()
    else:
        display_study_hub()

def display_setup_wizard():
    st.title("📚 Welcome: Create a New Subject")
    with st.form("setup_form"):
        subject_name = st.text_input("Subject Name (e.g., 'Formal Language and Automata Theory')")
        syllabus_text = st.text_area("Paste the entire syllabus here", height=250)
        submitted = st.form_submit_button("Create Subject")

        if submitted and subject_name and syllabus_text:
            success = mcp_study.initialize_subject(subject_name, syllabus_text)
            if success:
                # Refresh the subjects list and set the new one as active
                st.session_state.subjects = mcp_study.load_subjects()
                st.session_state.selected_subject = subject_name
                st.rerun()

def display_study_hub():
    st.sidebar.title("🎓 Study Hub")
    subject_list = list(st.session_state.subjects.keys())
    
    # Use index to handle selectbox changes properly
    if st.session_state.selected_subject not in subject_list:
        st.session_state.selected_subject = subject_list[0]

    selected_subject_index = subject_list.index(st.session_state.selected_subject)
    new_selected_subject = st.sidebar.selectbox("Select Subject", subject_list, index=selected_subject_index)

    # If the subject changes, update state and rerun
    if new_selected_subject != st.session_state.selected_subject:
        st.session_state.selected_subject = new_selected_subject
        st.session_state.topics = [] # Clear topics for the new subject
        st.session_state.active_content = None
        st.rerun()

    st.sidebar.markdown("---")

    # Generate and display topics for the selected subject
    if not st.session_state.topics:
        with st.spinner("AI is analyzing the syllabus and generating topics..."):
            syllabus_text = st.session_state.subjects[st.session_state.selected_subject]
            topic_data = mcp_study.generate_topics_from_syllabus(syllabus_text)
            if topic_data:
                st.session_state.topics = topic_data.topics
            else:
                st.error("Could not generate topics from the syllabus.")
    
    if st.session_state.topics:
        selected_topic_name = st.sidebar.radio("Select a Topic", [t.name for t in st.session_state.topics])
        display_topic_hub(st.session_state.selected_subject, selected_topic_name)

def display_topic_hub(subject_name, topic_name):
    st.title(topic_name)

    # Find the summary for the selected topic
    topic_summary = ""
    for topic in st.session_state.topics:
        if topic.name == topic_name:
            topic_summary = topic.summary
            break
    st.info(topic_summary)
    st.markdown("---")

    # --- Interactive Action Buttons ---
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔎 Explain the Concept"):
            with st.spinner("AI is generating a detailed explanation..."):
                explanation = mcp_study.generate_topic_explanation(topic_name, subject_name)
                st.session_state.active_content = explanation

    with col2:
        if st.button("🧩 Generate an Interactive Quiz"):
            with st.spinner("AI is generating an interactive quiz..."):
                prompt = f"Create a multiple-choice quiz with 3-4 questions for the topic '{topic_name}'. The quiz should be a self-contained HTML component with CSS for styling and simple Javascript to show feedback on selection."
                component = mcp_study.generate_creative_component(prompt)
                if component:
                    # Inject the generated CSS and HTML into the template
                    template = pathlib.Path("subjects") / subject_name / "template.html"
                    if template.exists():
                        template_html = template.read_text()
                        final_html = template_html.replace("{{CSS}}", component.css).replace("{{HTML}}", component.html)
                        st.session_state.active_content = final_html
                    else:
                        st.session_state.active_content = "Error: template.html not found."
                else:
                    st.session_state.active_content = "Failed to generate quiz component."

    with col3:
        if st.button("🗺️ Create a Concept Map"):
            with st.spinner("AI is generating a concept map..."):
                # This can be expanded to generate a Graphviz component
                st.session_state.active_content = f"Concept map generation for '{topic_name}' is under development."

    # --- Display Generated Content ---
    if st.session_state.active_content:
        st.markdown("### Generated Content")
        if "<html" in str(st.session_state.active_content).lower():
            st.components.v1.html(st.session_state.active_content, height=500, scrolling=True)
        else:
            st.markdown(st.session_state.active_content)

if __name__ == "__main__":
    main()