"""
smart_parser.py
A lightweight resume parser using regex + simple heuristics.
Optional spaCy integration points are commented where applicable.
"""

import re, json
from typing import Dict, List

EMAIL_RE = re.compile(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}")
SECTION_HEADERS = [
    "summary","objective","skills","technical skills","education","experience","work experience",
    "projects","certifications","certificates","publications","courses","interests","languages"
]

def clean_text(text: str) -> str:
    # normalize newlines and remove repeated spaces
    return re.sub(r"\\r", "\\n", text).strip()

def find_section_ranges(lines: List[str]) -> Dict[str, tuple]:
    # locate lines that look like section headers
    idxs = {}
    for i, line in enumerate(lines):
        l = line.strip().lower().rstrip(":")
        if l in SECTION_HEADERS or any(l.startswith(h + ":") for h in SECTION_HEADERS):
            # map header to line index
            idxs[i] = l
    # build ranges: header line -> (start, end)
    sorted_headers = sorted(idxs.items(), key=lambda x: x[0])
    ranges = {}
    for j, (i, header) in enumerate(sorted_headers):
        start = i + 1
        end = (sorted_headers[j+1][0]) if j+1 < len(sorted_headers) else len(lines)
        ranges[header] = (start, end)
    return ranges

def extract_list_block(lines: List[str], start: int, end: int) -> List[str]:
    items = []
    for line in lines[start:end]:
        line = line.strip()
        if not line: 
            continue
        # treat lines starting with '-' or bullet chars as items; or short comma-separated lists
        if line.startswith(("-", "*", "•")) or len(line) < 120 and "," in line:
            # split by commas if it's a single line list
            if "," in line and not line.startswith(("-", "*", "•")):
                parts = [p.strip() for p in line.split(",") if p.strip()]
                items.extend(parts)
            else:
                items.append(re.sub(r"^[-*•\s]+", "", line))
        else:
            # if line looks like "Skill1, Skill2, Skill3" inline, split
            if "," in line and len(line.split(",")) <= 10:
                parts = [p.strip() for p in line.split(",") if p.strip()]
                items.extend(parts)
            else:
                # otherwise add as paragraph (could be experience bullet)
                items.append(line)
    return items

def parse_resume_text(text: str) -> Dict:
    t = clean_text(text)
    lines = [ln for ln in t.splitlines()]
    text_join = " ".join(lines)
    data = {}
    # contact
    emails = re.findall(EMAIL_RE, text_join)
    phones = re.findall(PHONE_RE, text_join)
    data["email"] = emails[0] if emails else ""
    data["phone"] = "".join(phones[0]) if phones else ""
    # name heuristic: first non-empty line, up to 4 words, Title Case
    first_lines = [ln.strip() for ln in lines if ln.strip()][:3]
    name = ""
    if first_lines:
        cand = first_lines[0]
        if 2 <= len(cand.split()) <= 4 and any(ch.isupper() for ch in cand[0:1]):
            name = cand
        else:
            # fallback to second line
            if len(first_lines) > 1 and 2 <= len(first_lines[1].split()) <= 4:
                name = first_lines[1]
    data["name"] = name

    # sections
    sec_ranges = find_section_ranges(lines)
    # default blocks if not found: try search for "experience", "education", "skills" in text
    def get_block(header_variants):
        for hv in header_variants:
            for h, rng in sec_ranges.items():
                if hv in h:
                    return extract_list_block(lines, rng[0], rng[1])
        return []

    data["skills"] = get_block(["skills","technical skills"])
    data["education"] = get_block(["education"])
    data["experience"] = get_block(["experience","work experience","projects"])

    # fallback heuristics: try to extract simple "Skills:" inline
    m = re.search(r"skills[:\\s]*(.+)", text_join, re.I)
    if m and not data["skills"]:
        # take up to 120 chars after "skills:" and split commas/semi
        skills_str = m.group(1)[:400]
        parts = re.split(r"[;\\n\\|•\\-]", skills_str)
        parts = [p.strip() for p in re.split(r",", skills_str) if p.strip()]
        data["skills"] = parts

    # experience parsing: try to split bullet paragraphs into job entries by blank lines or date patterns
    ex = data["experience"]
    jobs = []
    current = []
    date_re = re.compile(r"(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\\s+\\d{4}\\b)|(?:\\b\\d{4}\\b)|(?:\\b\\d{2}/\\d{4}\\b)",
                         re.I)
    for line in ex:
        if date_re.search(line) and current:
            jobs.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        jobs.append(" ".join(current))
    data["experience_parsed"] = jobs if jobs else ex

    return data

def to_json(data: dict) -> str:
    return json.dumps(data, indent=2)
