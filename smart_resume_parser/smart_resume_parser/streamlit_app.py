"""
streamlit_app.py
A simple Streamlit UI for uploading resumes (.txt, .pdf, .docx) and viewing parsed results.
This example uses the lightweight parser in smart_parser.py.
To run: streamlit run streamlit_app.py
"""
import streamlit as st
from smart_parser import parse_resume_text, to_json
import io, json, csv

st.set_page_config(page_title="Smart Resume Parser", layout="wide")

st.title("Smart Resume Parser — Demo")
st.markdown("Upload a resume (.txt supported in this demo). The app extracts contact, skills, education and experience.")

uploaded = st.file_uploader("Upload resume (.txt)", type=["txt"], accept_multiple_files=False)
if uploaded:
    raw = uploaded.read().decode("utf-8", errors="ignore")
    parsed = parse_resume_text(raw)
    st.subheader("Parsed JSON")
    st.code(to_json(parsed), language="json")
    st.subheader("Structured view")
    st.write("Name:", parsed.get("name",""))
    st.write("Email:", parsed.get("email",""))
    st.write("Phone:", parsed.get("phone",""))
    st.write("Skills:", parsed.get("skills",[]))
    st.write("Education:", parsed.get("education",[]))
    st.write("Experience entries:", parsed.get("experience_parsed",[]))

    # export buttons
    json_bytes = json.dumps(parsed, indent=2).encode("utf-8")
    st.download_button("Download JSON", data=json_bytes, file_name="parsed_resume.json", mime="application/json")
    # CSV export - flatten skills and experience
    import pandas as pd
    df = pd.DataFrame({
        "name":[parsed.get("name","")],
        "email":[parsed.get("email","")],
        "phone":[parsed.get("phone","")],
        "skills":[", ".join(parsed.get("skills",[]))],
        "education":[ " | ".join(parsed.get("education",[])) ],
        "experience":[ " || ".join(parsed.get("experience_parsed",[])) ]
    })
    st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="parsed_resume.csv", mime="text/csv")
