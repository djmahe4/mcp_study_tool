# Dynamic AI Study Companion

This project is a dynamic and interactive study application that uses a Large Language Model (LLM) to generate personalized learning content. It's designed to be a flexible and engaging learning partner that helps you understand complex topics, prepare for exams, and build your own web-based study notes.

## Features

*   **Dynamic Module Creation:** Create new study modules on the fly by simply providing a syllabus.
*   **Interactive Learning Tools:** Generate a variety of interactive learning tools for each topic, including:
    *   **Conceptual Breakdowns:** Get detailed explanations of complex topics.
    *   **Visual Concept Maps:** Visualize the relationships between key concepts using Graphviz.
    *   **Interactive Quizzes:** Test your knowledge with interactive quizzes.
    *   **Mnemonics:** Get help memorizing key information with AI-generated mnemonics.
*   **Personal Web-Folio:** Automatically generate a personal website for each subject to document your learning journey.
*   **Web Development Practice:** Edit the HTML of your web-folio to practice your web development skills.

## Project Structure

```
/
├── subjects/
│   ├── [subject_name]/
│   │   ├── [module_name]/
│   │   │   ├── module_context.txt
│   │   │   ├── syllabus.txt
│   │   │   └── [module_name]_app.py
│   │   ├── subject_context.txt
│   │   ├── index.html
│   │   ├── style.css
│   │   ├── script.js
│   │   └── [subject_name]_web_dev.py
├── mcp_study.py
├── streamlit_app.py
└── README.md
```

*   **`subjects/`**: This directory contains all the study materials, organized by subject and module.
*   **`mcp_study.py`**: The backend "brain" of the application. It contains all the logic for generating content, managing files, and interacting with the LLM.
*   **`streamlit_app.py`**: The main Streamlit application that serves as the entry point and allows you to manage your subjects and modules.
*   **`subject_context.txt`**: A configuration file for each subject that defines the subject's context and tracks saved content.
*   **`module_context.txt`**: A configuration file for each module that defines the module's topics and features.
*   **`index.html`, `style.css`, `script.js`**: The files for your personal web-folio for each subject.

## Getting Started

1.  **Install dependencies:** `pip install -r requirements.txt`
2.  **Set up your Google API Key:** Make sure you have a `GOOGLE_API_KEY` environment variable set up, or add it to your Streamlit secrets.
3.  **Run the application:** `streamlit run streamlit_app.py`

## Future Work (TODO)

- [ ] **PYQ Processing:**
    - [ ] Implement a file uploader for PYQ PDF files.
    - [ ] Create a `process_pyq_pdf` function in `mcp_study.py` that uses `PyMuPDF` and `Pytesseract` to extract questions from PDFs.
    - [ ] Implement support for custom parameters to handle different question paper formats (e.g., marks per section, question patterns).
    - [ ] Store the extracted questions in a structured format (e.g., a JSON file).