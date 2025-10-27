Smart Resume Parser - Demo Codebase
=====================================

What you get:
- smart_parser.py       : lightweight parser module (regex + heuristics)
- streamlit_app.py      : Streamlit UI to upload a .txt resume and view results
- run_parsing.py        : batch runner that parses all .txt resumes in folder
- 5 sample resumes      : resume_1_jane_doe.txt ... resume_5_omar_sanchez.txt
- per-resume parsed JSON files (one for each sample resume)
- parsed_resumes.csv    : combined CSV of all parsed resumes
- README.md             : this file

How to run locally:
1. Install Python 3.9+
2. (Optional) create a virtualenv: python -m venv venv && source venv/bin/activate
3. Install Streamlit if you want the UI: pip install streamlit
4. Run the parser on all text resumes: python run_parsing.py
5. Run the Streamlit UI: streamlit run streamlit_app.py
Note: This demo uses plain-text resumes (.txt). For PDF/DOCX support, use PyMuPDF and python-docx to extract text, then call parse_resume_text(text).

Optional spaCy enhancement:
- If you prefer to use spaCy for NER (better name/email extraction) install spaCy and a model, then replace the contact extraction in smart_parser.py with spaCy NER calls.

Deliverables are zipped in smart_resume_parser.zip
