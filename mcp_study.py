import os
import re
import pathlib
import streamlit as st
from typing import List, Optional, Dict
import configparser

# LangChain & Pydantic Imports
from pydantic import BaseModel, Field
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

# --- Pydantic Models ---

class Topic(BaseModel):
    name: str = Field(description="The descriptive name of the topic.")
    slug: str = Field(description="A URL-friendly slug for the topic.")

class ModuleTopics(BaseModel):
    topics: List[Topic] = Field(description="The structured list of topics.")

class GeneratedCode(BaseModel):
    html: str = Field(description="The self-contained HTML code.")
    css: str = Field(description="The self-contained CSS code.")
    javascript: str = Field(description="The self-contained JavaScript code.")

# --- Model Cache ---

def get_gemini_model(structured_output_model=None, force_reinit=False):
    model_key = 'gemini_model'
    model_name = "gemini-pro"
    if force_reinit and model_key in st.session_state:
        del st.session_state[model_key]
    if model_key not in st.session_state:
        try:
            api_key = os.environ.get('GOOGLE_API_KEY') or st.secrets.get("GOOGLE_API_KEY")
            st.session_state[model_key] = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.7)
        except Exception as e:
            st.error(f"Failed to initialize Gemini model: {e}")
            return None
    model = st.session_state[model_key]
    if structured_output_model:
        return model.with_structured_output(structured_output_model)
    return model

def invoke_model_with_retry(model, prompt):
    try:
        return model.invoke(prompt)
    except Exception as e:
        st.warning(f"AI model call failed: {e}. Retrying...")
        structured_schema = model.pydantic_schema if hasattr(model, 'pydantic_schema') else None
        reinitialized_model = get_gemini_model(structured_output_model=structured_schema, force_reinit=True)
        if reinitialized_model:
            return reinitialized_model.invoke(prompt)
        else:
            raise e

# --- File System & Content Management ---

def initialize_subject(subject_name: str):
    subject_dir = pathlib.Path("subjects") / subject_name
    subject_dir.mkdir(parents=True, exist_ok=True)

    subject_context_path = subject_dir / "subject_context.txt"
    if not subject_context_path.exists():
        config = configparser.ConfigParser()
        config['subject'] = {'name': subject_name, 'context': f'The study of {subject_name}.'}
        config['cross_module_concepts'] = {'concept1': 'Description1'}
        config['saved_content'] = {}
        with open(subject_context_path, "w") as f:
            config.write(f)

    # Create web-folio files
    if not (subject_dir / "index.html").exists():
        (subject_dir / "index.html").write_text("<html><head><link rel=\"stylesheet\" href=\"style.css\"></head><body><h1>My Web-Folio</h1><div id=\"content\"></div><script src=\"script.js\"></script></body></html>")
    if not (subject_dir / "style.css").exists():
        (subject_dir / "style.css").write_text("body { font-family: sans-serif; }")
    if not (subject_dir / "script.js").exists():
        (subject_dir / "script.js").write_text("console.log('Web-Folio loaded');")
    
    create_web_dev_app(subject_name)

def create_web_dev_app(subject_name: str):
    subject_dir = pathlib.Path("subjects") / subject_name
    web_dev_app_path = subject_dir / f"{subject_name}_web_dev.py"

    app_template = f"""
import streamlit as st
import pathlib

st.set_page_config(page_title=f"{subject_name} Web Dev")
st.title("Web-Folio Editor")

subject_dir = pathlib.Path(__file__).parent
index_path = subject_dir / "index.html"

if index_path.exists():
    html_content = index_path.read_text()
    edited_html = st.text_area("HTML Content", html_content, height=500)

    if st.button("Save Changes"):
        index_path.write_text(edited_html)
        st.success("Changes saved!")
"""
    web_dev_app_path.write_text(app_template)

def initialize_module(subject_name: str, module_name: str, syllabus_text: str):
    initialize_subject(subject_name)
    module_dir = pathlib.Path("subjects") / subject_name / module_name
    module_dir.mkdir(parents=True, exist_ok=True)

    llm_for_topics = get_gemini_model(ModuleTopics)
    prompt = f"Parse the syllabus for '{module_name}' to extract topics. Create a URL-friendly slug for each. Syllabus: {syllabus_text}"
    if llm_for_topics:
        response = invoke_model_with_retry(llm_for_topics, prompt)
        if isinstance(response, ModuleTopics):
            config = configparser.ConfigParser()
            config['module'] = {'name': module_name, 'context': 'Initial context.'}
            config['topics'] = {topic.slug: topic.name for topic in response.topics}
            config['features'] = {
                'conceptual_breakdown': 'true',
                'visual_concept_map': 'true',
                'interactive_quiz': 'true',
                'mnemonics': 'true'
            }
            with open(module_dir / "module_context.txt", "w") as f:
                config.write(f)
        else:
            st.error("Failed to parse syllabus.")
            return

    app_template = f"""
import streamlit as st
import pathlib
import configparser
import sys
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
import mcp_study
st.set_page_config(page_title="{module_name}", layout="wide")
st.title("{module_name}")

module_path = pathlib.Path(__file__).parent
subject_name = module_path.parent.name
config = configparser.ConfigParser()
config.read(module_path / "module_context.txt")

topics = dict(config['topics']) if 'topics' in config else {{}}
features = dict(config['features']) if 'features' in config else {{}}

selected_topic_slug = st.sidebar.radio("Select Topic", list(topics.keys()), format_func=lambda slug: topics[slug])

if selected_topic_slug:
    topic_name = topics[selected_topic_slug]
    st.header(topic_name)

    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = {{}}

    if features.get('conceptual_breakdown') == 'true':
        if st.button("Conceptual Breakdown"):
            with st.spinner("Generating explanation..."):
                explanation = mcp_study.generate_topic_explanation(topic_name, "", "")
                st.session_state.generated_content['explanation'] = explanation
                st.markdown(explanation)
        if 'explanation' in st.session_state.generated_content and st.session_state.generated_content['explanation']:
            if st.button("Save Explanation to Web-Folio"):
                mcp_study.update_web_folio(subject_name, topic_name, st.session_state.generated_content['explanation'], "markdown")
                st.success("Explanation saved to Web-Folio!")

    if features.get('visual_concept_map') == 'true':
        if st.button("Visual Concept Map"):
            with st.spinner("Generating map..."):
                dot_string = mcp_study.generate_visual_map(topic_name)
                st.session_state.generated_content['map'] = dot_string
                st.graphviz_chart(dot_string)
        if 'map' in st.session_state.generated_content and st.session_state.generated_content['map']:
            if st.button("Save Map to Web-Folio"):
                mcp_study.update_web_folio(subject_name, topic_name, st.session_state.generated_content['map'], "graphviz")
                st.success("Map saved to Web-Folio!")

    if features.get('interactive_quiz') == 'true':
        if st.button("Interactive Quiz"):
            with st.spinner("Generating quiz..."):
                code = mcp_study.generate_interactive_quiz(topic_name)
                st.session_state.generated_content['quiz'] = code
                if code:
                    st.components.v1.html(f'<style>{"code.css"}</style>{"code.html"}', height=500)
        if 'quiz' in st.session_state.generated_content and st.session_state.generated_content['quiz']:
            if st.button("Save Quiz to Web-Folio"):
                mcp_study.update_web_folio(subject_name, topic_name, st.session_state.generated_content['quiz'].html, "html")
                st.success("Quiz saved to Web-Folio!")

    if features.get('mnemonics') == 'true':
        if st.button("Generate Mnemonics"):
            with st.spinner("Generating mnemonics..."):
                mnemonics = mcp_study.generate_mnemonics(topic_name)
                st.session_state.generated_content['mnemonics'] = mnemonics
                st.markdown(mnemonics)
        if 'mnemonics' in st.session_state.generated_content and st.session_state.generated_content['mnemonics']:
            if st.button("Save Mnemonics to Web-Folio"):
                mcp_study.update_web_folio(subject_name, topic_name, st.session_state.generated_content['mnemonics'], "markdown")
                st.success("Mnemonics saved to Web-Folio!")

"""
    (module_dir / f"{module_name}_app.py").write_text(app_template)
    (module_dir / "syllabus.txt").write_text(syllabus_text)
    st.success(f"Module '{module_name}' initialized.")

def update_web_folio(subject_name: str, topic_name: str, content: str, content_type: str):
    subject_dir = pathlib.Path("subjects") / subject_name
    index_path = subject_dir / "index.html"
    context_path = subject_dir / "subject_context.txt"

    model = get_gemini_model()
    prompt = f"Format the following {content_type} content for a web page section about '{topic_name}'. Use stylish and modern HTML. Content: {content}"
    if model:
        response = invoke_model_with_retry(model, prompt)
        html_content = response.content

        if index_path.exists():
            existing_html = index_path.read_text()
            new_html = existing_html.replace("<div id=\"content\">", f"<div id=\"content\">\n{html_content}")
            index_path.write_text(new_html)
    
    config = configparser.ConfigParser()
    config.read(context_path)
    if not config.has_section('saved_content'):
        config.add_section('saved_content')
    
    saved_types = config.get('saved_content', topic_name, fallback="")
    if content_type not in saved_types:
        new_types = saved_types + ("," if saved_types else "") + content_type
        config.set('saved_content', topic_name, new_types)

    with open(context_path, "w") as f:
        config.write(f)

def load_subject_structure(base_path: str = "subjects") -> Dict:
    structure = {}
    base_dir = pathlib.Path(base_path)
    if not base_dir.exists():
        return structure
    for subject_dir in base_dir.iterdir():
        if subject_dir.is_dir():
            subject_name = subject_dir.name
            structure[subject_name] = {"modules": {}, "context": ""}
            subject_context_path = subject_dir / "subject_context.txt"
            if subject_context_path.exists():
                config = configparser.ConfigParser()
                config.read(subject_context_path)
                if 'subject' in config and 'context' in config['subject']:
                    structure[subject_name]['context'] = config['subject']['context']
            for module_dir in subject_dir.iterdir():
                if module_dir.is_dir():
                    module_name = module_dir.name
                    module_context_path = module_dir / "module_context.txt"
                    if module_context_path.exists():
                        config = configparser.ConfigParser()
                        config.read(module_context_path)
                        topics = dict(config['topics']) if 'topics' in config else {{}}
                        structure[subject_name]["modules"][module_name] = {"topics": topics}
    return structure

# --- Pedagogical LLM Functions ---

def generate_topic_explanation(topic_name: str, module_context: str, subject_context: str) -> str:
    model = get_gemini_model()
    prompt = f"""
    Generate a comprehensive, Markdown-formatted explanation for '{topic_name}'.
    - Break down the topic into core sub-points.
    - Use simple analogies.
    - Include an 'Exam Prep' section with key terms, formulas, and sample questions.
    - Provide a glossary for symbols and terms.
    """
    if model:
        response = invoke_model_with_retry(model, prompt)
        return response.content
    return "Error: AI model not available."

def generate_visual_map(topic_context: str) -> str:
    model = get_gemini_model()
    prompt = f"Generate a Graphviz DOT string for a concept map on: {topic_context}."
    if model:
        response = invoke_model_with_retry(model, prompt)
        dot_match = re.search(r"```dot(.*)```", response.content, re.DOTALL)
        if dot_match:
            return dot_match.group(1).strip()
    return 'digraph G { error[label="Failed to generate map"]; }'

def generate_interactive_quiz(topic_name: str) -> Optional[GeneratedCode]:
    structured_llm = get_gemini_model(GeneratedCode)
    prompt = f"Create a multiple-choice quiz with 3-4 questions for '{topic_name}'. Provide HTML, CSS for styling, and JS for feedback."
    if structured_llm:
        response = invoke_model_with_retry(structured_llm, prompt)
        if isinstance(response, GeneratedCode):
            return response
    return None

def generate_mnemonics(topic_name: str) -> str:
    model = get_gemini_model()
    prompt = f"Generate helpful mnemonics for the key concepts in '{topic_name}'."
    if model:
        response = invoke_model_with_retry(model, prompt)
        return response.content
    return "Error: AI model not available."
