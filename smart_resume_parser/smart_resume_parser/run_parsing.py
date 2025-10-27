"""
run_parsing.py
Parses all .txt resumes in the directory and writes JSON and a combined CSV.
"""
import json, csv, glob, os
from smart_parser import parse_resume_text, to_json

DATA_DIR = os.path.dirname(__file__)
resumes = glob.glob(os.path.join(DATA_DIR, "*.txt"))

all_parsed = []
for r in resumes:
    with open(r, "r", encoding="utf-8") as f:
        txt = f.read()
    parsed = parse_resume_text(txt)
    parsed["_source_file"] = os.path.basename(r)
    all_parsed.append(parsed)
    # write per-resume json
    with open(r + ".parsed.json", "w", encoding="utf-8") as jf:
        jf.write(to_json(parsed))

# write combined CSV
csv_path = os.path.join(DATA_DIR, "parsed_resumes.csv")
with open(csv_path, "w", newline='', encoding="utf-8") as cf:
    writer = csv.DictWriter(cf, fieldnames=["_source_file","name","email","phone","skills","education","experience"])
    writer.writeheader()
    for p in all_parsed:
        writer.writerow({
            "_source_file": p.get("_source_file",""),
            "name": p.get("name",""),
            "email": p.get("email",""),
            "phone": p.get("phone",""),
            "skills": "; ".join(p.get("skills",[])),
            "education": " | ".join(p.get("education",[])),
            "experience": " || ".join(p.get("experience_parsed",[]))
        })
print("Parsing complete. Wrote per-resume JSON files and combined CSV:", csv_path)
