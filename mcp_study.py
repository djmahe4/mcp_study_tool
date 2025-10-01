import os
import re
import pathlib
import streamlit as st
from typing import List, Optional
# LangChain & Pydantic Imports
from pydantic import BaseModel, Field
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

# --- Pydantic Models for a Clear Structure ---

class Topic(BaseModel):
    """A single, well-defined topic extracted from a syllabus."""
    name: str = Field(description="The descriptive name of the topic.")
    summary: str = Field(description="A concise, one-sentence summary of the topic.")

class SyllabusTopics(BaseModel):
    """A structured list of topics derived from a syllabus."""
    topics: List[Topic] = Field(description="The structured list of topics parsed from the syllabus.")

class GeneratedCode(BaseModel):
    """A model to hold generated code for creative components."""
    html: str = Field(description="The complete, self-contained HTML code for the component.")
    css: str = Field(description="The complete, self-contained CSS code for the component.")

# --- Configuration & Robust Model Cache ---

def get_gemini_model(structured_output_model=None, force_reinit=False):
    """Caches and returns the Gemini model instance, handling re-initialization."""
    model_key = 'gemini_model'
    model_name = "gemini-flash-latest"

    if force_reinit and model_key in st.session_state:
        del st.session_state[model_key]

    if model_key not in st.session_state:
        try:
            api_key = os.environ.get('GOOGLE_API_KEY') or st.secrets.get("GOOGLE_API_KEY")
            if not api_key:
                st.error("Google API Key not found. Please set it in your environment or Streamlit secrets.")
                return None
            st.session_state[model_key] = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.7, convert_system_message_to_human=True)
        except Exception as e:
            st.error(f"Failed to initialize Gemini model: {e}")
            return None
    
    model = st.session_state[model_key]
    if structured_output_model:
        return model.with_structured_output(structured_output_model)
    return model

def invoke_model_with_retry(model, prompt):
    """Invokes the model and retries once with re-initialization on failure."""
    try:
        return model.invoke(prompt)
    except Exception as e:
        st.warning(f"AI model call failed: {e}. Retrying once after re-initializing model...")
        structured_schema = model.pydantic_schema if hasattr(model, 'pydantic_schema') else None
        reinitialized_model = get_gemini_model(structured_output_model=structured_schema, force_reinit=True)
        if reinitialized_model:
            return reinitialized_model.invoke(prompt)
        else:
            raise e

# --- Core AI-Powered Functions ---

def generate_topics_from_syllabus(syllabus_text: str) -> Optional[SyllabusTopics]:
    """Uses AI to parse a syllabus and extract a structured list of topics."""
    prompt = f"""
    You are an expert instructional designer. Your task is to parse the following syllabus and identify the main learning topics.
    For each topic, provide a clear name and a concise one-sentence summary.

    Syllabus Text:
    ---
    {syllabus_text}
    ---
    """
    structured_llm = get_gemini_model(SyllabusTopics)
    if structured_llm:
        response = invoke_model_with_retry(structured_llm, prompt)
        # Directly check if the response is the Pydantic model we expect
        if isinstance(response, SyllabusTopics):
            return response
    return None

def generate_topic_explanation(topic_name: str, subject_context: str) -> str:
    """Generates a comprehensive Markdown explanation for a given topic."""
    model = get_gemini_model()
    prompt = f"""
    **Persona:** Act as an expert instructional designer.
    **Task:** Generate a comprehensive, Markdown-formatted explanation for the topic: '{topic_name}'.
    **Methodology:** Use fragmentation, simplification, concept linking, and an exam-oriented approach.
    **Subject Context:** {subject_context}
    """
    if model:
        response = invoke_model_with_retry(model, prompt)
        return response.content
    return "Error: AI model is not available."

def generate_creative_component(prompt: str) -> Optional[GeneratedCode]:
    """Generates HTML and CSS for a creative component based on a prompt."""
    structured_llm = get_gemini_model(GeneratedCode)
    full_prompt = f"""
    You are an expert frontend developer. Generate self-contained HTML and CSS for the following component request.
    User Request: "{prompt}"
    """
    if structured_llm:
        response = invoke_model_with_retry(structured_llm, full_prompt)
        if isinstance(response, GeneratedCode):
            return response
    return None

# --- File System Management ---

def initialize_subject(subject_name: str, syllabus_text: str) -> bool:
    """Initializes a new subject directory, saves the syllabus, and creates HTML/CSS templates."""
    subject_dir = pathlib.Path("subjects") / subject_name
    if subject_dir.exists():
        st.error(f"Subject '{subject_name}' already exists.")
        return False
    
    subject_dir.mkdir(parents=True)

    # Save the syllabus
    (subject_dir / "syllabus.txt").write_text(syllabus_text, encoding="utf-8")

    # Save boilerplate HTML and CSS for creative components
    html_boilerplate = """
<!DOCTYPE html>
<html>
<head>
<style>
{{CSS}}
</style>
</head>
<body>
{{HTML}}
</body>
</html>
"""
    (subject_dir / "template.html").write_text(html_boilerplate, encoding="utf-8")

    st.success(f"Subject '{subject_name}' initialized successfully.")
    return True

def load_subjects() -> dict:
    """Loads all existing subjects and their syllabus text."""
    subjects_dir = pathlib.Path("subjects")
    if not subjects_dir.is_dir():
        #print("lol")
        return {}
    
    subjects = {}
    for subject_dir in subjects_dir.iterdir():
        print(subject_dir)
        if subject_dir.is_dir():
            #module_path = subject_dir
            for mod in subject_dir.iterdir():
                #print(part)
                mod_path = mod
                print(mod_path)
                if mod_path.exists():
                    syllabus_path = mod_path / "syllabus.txt"
                    if syllabus_path.exists():
                        #print(syllabus_path.read_text(encoding="utf-8"))
                        subjects[subject_dir.name] = syllabus_path.read_text(encoding="utf-8")
    return subjects
if __name__== "__main__":
    # Example usage
    print(load_subjects())