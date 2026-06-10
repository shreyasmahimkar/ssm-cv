import re
import requests
import json
import os
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs

DOC_URL = "https://docs.google.com/document/d/1bbPRlF2jy3Jkh94Vuw2scdsqQUB51RF8pINoiZ3GUv8/export?format=html"
FALLBACK_FILE = "resume_fallback.json"

class GoogleDocHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.current_line = []
        self.in_body = False
        self.in_link = False
        self.link_href = ""
        self.link_text = ""
        self.list_nesting = 0
        
    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True
            return
        if not self.in_body:
            return
            
        if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
            self.flush_line()
            if tag == 'li':
                self.current_line.append("* ")
        elif tag in ['ul', 'ol']:
            self.list_nesting += 1
        elif tag == 'hr':
            self.flush_line()
            self.output.append("________________")
        elif tag == 'a':
            self.in_link = True
            self.link_text = ""
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            if "google.com/url?q=" in href:
                parsed_url = urlparse(href)
                q_params = parse_qs(parsed_url.query)
                if 'q' in q_params:
                    href = q_params['q'][0]
            self.link_href = href
            
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
            self.flush_line()
            return
        if not self.in_body:
            return
            
        if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
            self.flush_line()
        elif tag in ['ul', 'ol']:
            self.list_nesting = max(0, self.list_nesting - 1)
        elif tag == 'a':
            self.in_link = False
            cleaned_text = self.link_text.strip()
            if cleaned_text and self.link_href:
                self.current_line.append(f"[{cleaned_text}]({self.link_href})")
            elif cleaned_text:
                self.current_line.append(cleaned_text)
            self.link_href = ""
            self.link_text = ""
            
    def handle_data(self, data):
        if not self.in_body:
            return
        if self.in_link:
            self.link_text += data
        else:
            self.current_line.append(data)
            
    def flush_line(self):
        if self.current_line:
            line_str = "".join(self.current_line).strip()
            if line_str:
                self.output.append(line_str)
            self.current_line = []
            
    def get_markdown(self):
        self.flush_line()
        return "\n".join(self.output)

def fetch_resume_raw(url=DOC_URL):
    """Fetches raw HTML and converts it to Markdown representation."""
    try:
        # If url doesn't specify format, make sure it exports format=html
        if "export?format=" not in url:
            if "edit" in url:
                # Replace edit with export
                url = url.split("/edit")[0] + "/export?format=html"
            else:
                url = url.rstrip("/") + "/export?format=html"
        elif "format=txt" in url:
            url = url.replace("format=txt", "format=html")
            
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        parser = GoogleDocHTMLParser()
        parser.feed(response.text)
        return parser.get_markdown()
    except Exception as e:
        print(f"Error fetching/parsing resume HTML: {e}")
        return None

def parse_resume_text(text):
    """Parses raw resume text into structured dict."""
    lines = [line.strip() for line in text.split('\n')]
    
    # Structure we want to populate
    resume = {
        "name": "",
        "contact": {},
        "summary": "",
        "skills": {},
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": []
    }
    
    # 1. Parse Header
    # Typically name is the first non-empty line
    non_empty_lines = [l for l in lines if l]
    if not non_empty_lines:
        return resume
        
    resume["name"] = non_empty_lines[0]
    
    # Contact info line is usually the second line
    contact_line = ""
    for l in non_empty_lines[1:]:
        if "|" in l and ("@" in l or "linkedin.com" in l or "+" in l):
            contact_line = l
            break
            
    if contact_line:
        parts = [p.strip() for p in contact_line.split("|")]
        resume["contact"]["title"] = parts[0]
        for p in parts[1:]:
            if "@" in p:
                resume["contact"]["email"] = p
            elif "linkedin.com" in p or "http" in p:
                m = re.search(r'\[.*?\]\((.*?)\)', p)
                resume["contact"]["linkedin"] = m.group(1) if m else p
            elif re.search(r'\+?\d[\d\s-]{8,}', p):
                resume["contact"]["phone"] = p
            else:
                resume["contact"]["location"] = p

    # 2. Extract sections
    # We will identify sections based on section headers
    sections = {
        "summary": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": []
    }
    
    current_section = None
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        # Detect section headers
        lower_line = cleaned_line.lower()
        if "professional summary" in lower_line:
            current_section = "summary"
            continue
        elif "technical skills" in lower_line:
            current_section = "skills"
            continue
        elif "professional experience" in lower_line:
            current_section = "experience"
            continue
        elif "key projects" in lower_line:
            current_section = "projects"
            continue
        elif "education" in lower_line:
            current_section = "education"
            continue
        elif "certifications & honors" in lower_line or "certifications" in lower_line:
            current_section = "certifications"
            continue
        elif re.match(r'^_{3,}$', cleaned_line):
            # Divider line, skip or reset section if not experience
            if current_section not in ["experience", "projects", "education"]:
                current_section = None
            continue
            
        if current_section:
            sections[current_section].append(cleaned_line)

    # Clean and structure each section
    
    # 2a. Professional Summary
    resume["summary"] = "\n".join(sections["summary"])
    
    # 2b. Technical Skills
    # Format: * AI & Agentic Frameworks: Multi-Agent Orchestration (MAS), ...
    for line in sections["skills"]:
        if line.startswith("*"):
            line = line.lstrip("*").strip()
            if ":" in line:
                category, skill_list = line.split(":", 1)
                # Split skills by comma, ignoring commas inside parentheses
                skills_arr = [s.strip() for s in re.split(r',\s*(?![^()]*\))', skill_list) if s.strip()]
                resume["skills"][category.strip()] = skills_arr
            else:
                skills_arr = [s.strip() for s in re.split(r',\s*(?![^()]*\))', line) if s.strip()]
                resume["skills"]["General"] = skills_arr

    # 2c. Professional Experience
    # We parse experience line by line
    # Companies are preceded by divider or are uppercase titles
    # Format: 
    # COMPANY | LOCATION
    # ROLE | DATES
    # SUMMARY / DESC
    # * BULLET POINTS
    exp_list = []
    curr_job = None
    
    for line in sections["experience"]:
        # If the line contains "|" and is likely a company name or role
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            # Check if this is a company line or role line
            # A role line usually has a date range in it (e.g. Mar 2025 – Present, or a year)
            is_role = False
            for p in parts:
                if any(x in p.lower() for x in ["present", "201", "202", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                    is_role = True
                    break
            
            if not is_role:
                # It's a Company Line!
                if curr_job:
                    exp_list.append(curr_job)
                curr_job = {
                    "company": parts[0],
                    "location": parts[1] if len(parts) > 1 else "",
                    "roles": []
                }
            else:
                # It's a Role Line!
                if curr_job is None:
                    # Fallback if company was somehow missed
                    curr_job = {"company": "Unknown Company", "location": "", "roles": []}
                
                # Check for dates
                role_title = parts[0]
                dates_raw = parts[1] if len(parts) > 1 else ""
                
                # Check if dates_raw contains * (meaning a bullet starts there)
                bullets = []
                dates = dates_raw
                if "*" in dates_raw:
                    date_parts = dates_raw.split("*", 1)
                    dates = date_parts[0].strip()
                    bullets.append(date_parts[1].strip())
                
                curr_job["roles"].append({
                    "title": role_title,
                    "dates": dates,
                    "description": "",
                    "bullets": bullets
                })
        else:
            if curr_job and curr_job["roles"]:
                active_role = curr_job["roles"][-1]
                if line.startswith("*"):
                    active_role["bullets"].append(line.lstrip("*").strip())
                else:
                    if active_role["description"]:
                        active_role["description"] += "\n" + line
                    else:
                        active_role["description"] = line
                        
    if curr_job:
        exp_list.append(curr_job)
    resume["experience"] = exp_list

    # 2d. Key Projects
    proj_list = []
    for line in sections["projects"]:
        if line.startswith("*"):
            line = line.lstrip("*").strip()
            if ":" in line:
                name, desc = line.split(":", 1)
                proj_list.append({
                    "name": name.strip(),
                    "description": desc.strip()
                })
            else:
                proj_list.append({
                    "name": "Project",
                    "description": line
                })
        else:
            if proj_list:
                proj_list[-1]["description"] += "\n" + line
            else:
                proj_list.append({
                    "name": "Project",
                    "description": line
                })
    resume["projects"] = proj_list

    # 2e. Education
    edu_list = []
    curr_edu = None
    for line in sections["education"]:
        if any(kw in line.lower() for kw in ["university", "institute", "college", "school"]):
            if curr_edu:
                edu_list.append(curr_edu)
            parts = [p.strip() for p in line.split("|")]
            curr_edu = {
                "institution": parts[0],
                "location": parts[1] if len(parts) > 1 else "",
                "degree": "",
                "details": []
            }
        else:
            if curr_edu:
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if not curr_edu["degree"]:
                        curr_edu["degree"] = parts[0]
                    curr_edu["details"].extend(parts[1:])
                else:
                    if not curr_edu["degree"]:
                        curr_edu["degree"] = line
                    else:
                        curr_edu["details"].append(line)
            else:
                parts = [p.strip() for p in line.split("|")]
                curr_edu = {
                    "institution": parts[0],
                    "location": parts[1] if len(parts) > 1 else "",
                    "degree": "",
                    "details": []
                }
    if curr_edu:
        edu_list.append(curr_edu)
    resume["education"] = edu_list

    # 2f. Certifications
    certs_list = []
    for line in sections["certifications"]:
        if line.startswith("*"):
            certs_list.append(line.lstrip("*").strip())
        else:
            certs_list.append(line)
    resume["certifications"] = certs_list

    return resume

def get_resume_data(url=DOC_URL, force_refresh=False):
    """
    Retrieves the resume data, either by fetching it live or
    using a local cached JSON file as a fallback.
    """
    if not force_refresh and os.path.exists(FALLBACK_FILE):
        try:
            with open(FALLBACK_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading local cache: {e}")
            
    text = fetch_resume_raw(url) if url else None
    if text:
        resume_data = parse_resume_text(text)
        # Cache it locally
        try:
            with open(FALLBACK_FILE, 'w') as f:
                json.dump(resume_data, f, indent=2)
        except Exception as e:
            print(f"Failed to cache resume: {e}")
        return resume_data
    
    # Fallback to local cache if exists
    if os.path.exists(FALLBACK_FILE):
        with open(FALLBACK_FILE, 'r') as f:
            return json.load(f)
            
    return None

if __name__ == "__main__":
    # Test fetch and parse
    raw = fetch_resume_raw()
    if raw:
        data = parse_resume_text(raw)
        print(json.dumps(data, indent=2))
        with open(FALLBACK_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("Success! Parsed and saved to fallback.")
    else:
        print("Failed to fetch raw resume.")
