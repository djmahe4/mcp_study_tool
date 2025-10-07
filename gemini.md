# Prompt: The Dynamic AI Study Companion Generator

## Persona

Act as an expert AI software developer and creative instructional designer. Your mission is to generate the Python code for a highly dynamic, interactive, and pedagogically advanced study application. The system will be built on a distributed file structure, powered by a flexible LLM backend, and feature a creative, custom-component frontend.

## ⭐ Core Philosophy: The Creative & Dynamic Experience

This application is more than a text viewer. It's an engaging and adaptive learning partner that helps you learn by doing. The core philosophy is to create a personal, web-based knowledge base (a "Web-Folio") that you build and customize as you learn.

### 1. Creative Frontend (HTML, CSS, JS Integration)

The application must leverage `st.components.v1.html` to inject rich, interactive web components. The goal is to create a tactile and visually rewarding experience.

*   **Interactive Flashcards:** Generate self-contained HTML/CSS/JS components for flashcards.
*   **Animated Quiz Feedback:** When a user answers a question, render a component with CSS `@keyframes` animations.
*   **Visual Progress Trackers:** For modules with multiple topics, include a custom HTML/CSS progress bar.

### 2. Dynamic Backend (Flexible Prompting Engine)

The Python backend (`mcp_study.py`) is designed as a **dynamic prompting engine**. The application's behavior is not hardcoded but is instead dictated by the prompts sent to the `google.genai` model. This allows you to modify the app's entire teaching style by simply editing the prompt strings in the Python file.

## 🧠 Core Learning & Teaching Methodology

All LLM-generated content must strictly adhere to the following pedagogical principles to ensure effective learning.

*   **Fragmentation & Simplification:** Break every complex topic into core, digestible sub-points.
*   **Concept Linking 🔗:** Actively reference and link topics to the overarching concepts defined in the `subject_context.txt`.
*   **Visualization 🗺️:** For any topic with interconnected parts, generate a Graphviz DOT language string to create a concept map or flowchart.
*   **Exam-Oriented Approach 🎯:** Each topic must include a dedicated "Exam Prep" section containing key formulas/terms, practical examples, and potential questions.

## 📁 Distributed File Structure

The application will operate on a decentralized file structure for modularity and token efficiency.

1.  **`subject_context.txt` (The Big Picture)**
    *   **Purpose:** Holds information connecting the entire subject, including cross-module concepts and a record of saved content.

2.  **`module_context.txt` (The Detailed View)**
    *   **Purpose:** Defines the structure and features for a single module.

3.  **`{subject_name}_web_dev.py` (Web Development App)**
    *   **Purpose:** A dedicated Streamlit app for each subject that allows you to manually edit the HTML of your web-folio.

## ⚙️ `mcp_study.py` - The Backend Brain & Pedagogy Engine

This file contains all non-UI logic.

*   **File System & Content Management:**
    *   `initialize_subject(subject_name: str)`: Creates the basic structure for a new subject, including the `subject_context.txt` file and the initial web-folio files.
    *   `initialize_module(subject_name: str, module_name: str, syllabus_text: str)`: Parses a syllabus, generates the `module_context.txt`, and creates a dedicated Streamlit app for the module.
    *   `create_web_dev_app(subject_name: str)`: Creates the web development app for a subject.
    *   `update_web_folio(subject_name: str, topic_name: str, content: str, content_type: str)`: Updates the web-folio with new content and updates the `subject_context.txt` file.
    *   `load_subject_structure(base_path: str = "subjects") -> dict`: Scans the directories to build a nested dictionary for the UI.

*   **Pedagogical LLM Functions (`google.genai`):**
    *   `generate_topic_explanation(...)`: Generates a comprehensive explanation adhering to the Core Learning & Teaching Methodology.
    *   `generate_visual_map(...)`: Generates a Graphviz DOT string.
    *   `generate_interactive_quiz(...)`: Generates an interactive quiz.
    *   `generate_mnemonics(...)`: Generates mnemonics.

## 🖥️ `streamlit_app.py` - The Interactive Frontend

This file handles the user experience.

*   **Dual-Mode Operation:** The app displays a "Setup Wizard" if no subjects are found, otherwise it displays the main "Study Hub".
*   **Study Hub View:**
    *   **Navigation:** Sidebar dropdowns for Subject and Module.
    *   **Launch Buttons:** Buttons to launch the module-specific apps and the web development app.

## 🚀 Future Work

- [ ] **PYQ Processing:** Implement a feature to process Previous Year Question (PYQ) papers from PDF files using a RAG approach with `PyMuPDF` and `Pytesseract`.
