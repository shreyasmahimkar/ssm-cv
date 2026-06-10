import streamlit as st
import json
import os
from resume_parser import get_resume_data, DOC_URL

# Set page configurations
st.set_page_config(
    page_title="Shreyas Mahimkar - Resume Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Apply font to all elements */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Gradient text for name */
.profile-name {
    background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 2.8rem;
    margin-bottom: 0px;
}

/* Job title styling */
.profile-title {
    font-size: 1.35rem;
    color: #4b5563;
    font-weight: 500;
    margin-top: 2px;
    margin-bottom: 15px;
}

/* Section header styling */
.sec-header {
    font-size: 1.6rem;
    font-weight: 600;
    color: #1e3a8a;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 6px;
    margin-top: 25px;
    margin-bottom: 15px;
}

/* Resume experience/education cards */
.resume-card {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}
.resume-card:hover {
    transform: translateY(-2px);
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

/* Badge for skills */
.skill-tag {
    display: inline-block;
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.18);
    color: #2563eb;
    padding: 5px 12px;
    border-radius: 16px;
    margin: 4px;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Timeline elements */
.job-meta {
    font-size: 0.9rem;
    color: #6b7280;
    font-weight: 400;
    margin-bottom: 8px;
}

.job-company {
    font-size: 1.15rem;
    font-weight: 600;
    color: #111827;
}

/* Adjustments for dark theme automatically */
@media (prefers-color-scheme: dark) {
    .profile-title {
        color: #9ca3af;
    }
    .sec-header {
        color: #60a5fa;
        border-bottom-color: #60a5fa;
    }
    .job-company {
        color: #f9fafb;
    }
    .job-meta {
        color: #9ca3af;
    }
    .skill-tag {
        color: #60a5fa;
        background: rgba(96, 165, 250, 0.12);
        border-color: rgba(96, 165, 250, 0.25);
    }
    .resume-card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
}
</style>
""", unsafe_allow_html=True)

# Fetching Data
@st.cache_data(ttl=3600)  # cache for 1 hour
def fetch_data(force=False):
    return get_resume_data(force_refresh=force)

# Session state to handle force refreshes
if "force_refresh" not in st.session_state:
    st.session_state.force_refresh = False

data = fetch_data(force=st.session_state.force_refresh)

# Reset force refresh state
if st.session_state.force_refresh:
    st.session_state.force_refresh = False
    st.rerun()

if not data:
    st.error("Could not load resume data. Please check your internet connection or Google Doc configuration.")
    st.stop()

# --- SIDEBAR CONTENT ---
with st.sidebar:
    # A elegant CSS initials badge
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 15px;">
        <div style="
            background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
            color: white;
            font-size: 2.2rem;
            font-weight: 700;
            width: 75px;
            height: 75px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        ">
            SM
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; margin-bottom: 0px;'>{data['name']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.9rem; margin-top: 2px;'>{data['contact'].get('title', '')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Contact Details
    st.markdown("#### 📞 Contact Details")
    contact = data["contact"]
    if contact.get("email"):
        st.markdown(f"📧 **Email:** [{contact['email']}](mailto:{contact['email']})")
    if contact.get("phone"):
        st.markdown(f"📱 **Phone:** `{contact['phone']}`")
    if contact.get("location"):
        st.markdown(f"📍 **Location:** {contact['location']}")
    if contact.get("linkedin"):
        st.markdown(f"🔗 **LinkedIn:** [Profile]({contact['linkedin']})")
        
    st.markdown("---")
    
    # Doc source & Controls
    st.markdown("#### ⚙️ Data Source")
    st.markdown(f"📄 [Google Doc Source Link]({DOC_URL})")
    
    if st.button("🔄 Sync Live from Google Doc", use_container_width=True):
        st.session_state.force_refresh = True
        st.rerun()
        
    # Download options
    st.markdown("#### 📥 Download Resume")
    json_str = json.dumps(data, indent=2)
    st.download_button(
        label="Download Structured JSON",
        data=json_str,
        file_name="shreyas_mahimkar_resume.json",
        mime="application/json",
        use_container_width=True
    )

# --- MAIN CONTENT ---

# Header Section
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"<div class='profile-name'>{data['name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-title'>{data['contact'].get('title', '')}</div>", unsafe_allow_html=True)
with col2:
    # Small status indicator
    st.markdown("""
    <div style='text-align: right; padding-top: 15px;'>
        <span style='background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;'>
            ● Open to Network
        </span>
    </div>
    """, unsafe_allow_html=True)

# Overview tab logic
tabs = st.tabs(["💼 Experience", "🛠️ Skills", "🚀 Projects & Education", "🏅 Certifications & Summary"])

# --- TAB 1: EXPERIENCE ---
with tabs[0]:
    st.markdown("<div class='sec-header'>Professional Experience</div>", unsafe_allow_html=True)
    
    for job in data["experience"]:
        # Company header card style
        st.markdown(f"""
        <div style="margin-top: 15px; margin-bottom: 5px;">
            <span class='job-company'>{job['company']}</span>
            <span class='job-meta'> — {job['location']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        for role in job["roles"]:
            with st.container():
                st.markdown(f"""
                <div class='resume-card'>
                    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                        <strong style="font-size: 1.1rem; color: #2563eb;">{role['title']}</strong>
                        <span style="font-size: 0.9rem; color: #6b7280; font-weight: 500;">📅 {role['dates']}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if role["description"]:
                    st.markdown(f"<p style='margin-top: 8px; font-size: 0.95rem; font-style: italic;'>{role['description']}</p>", unsafe_allow_html=True)
                
                if role["bullets"]:
                    st.markdown("<ul style='margin-top: 8px; padding-left: 20px; font-size: 0.95rem;'>", unsafe_allow_html=True)
                    for bullet in role["bullets"]:
                        st.markdown(f"<li>{bullet}</li>", unsafe_allow_html=True)
                    st.markdown("</ul>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: SKILLS ---
with tabs[1]:
    st.markdown("<div class='sec-header'>Technical Skills</div>", unsafe_allow_html=True)
    
    # We display skills as categorized cards
    cols = st.columns(len(data["skills"]))
    for index, (category, skill_list) in enumerate(data["skills"].items()):
        with cols[index]:
            st.markdown(f"""
            <div style="
                border: 1px solid rgba(128,128,128,0.2); 
                border-radius: 12px; 
                padding: 18px; 
                height: 100%; 
                background-color: rgba(255, 255, 255, 0.02);
            ">
                <h4 style="margin-top: 0px; border-bottom: 1px solid rgba(128,128,128,0.1); padding-bottom: 8px; color: #3b82f6;">{category}</h4>
                <div style="margin-top: 10px;">
            """, unsafe_allow_html=True)
            
            for skill in skill_list:
                st.markdown(f"<span class='skill-tag'>{skill}</span>", unsafe_allow_html=True)
                
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 3: PROJECTS & EDUCATION ---
with tabs[2]:
    col_proj, col_edu = st.columns([1, 1])
    
    with col_proj:
        st.markdown("<div class='sec-header'>Key Projects</div>", unsafe_allow_html=True)
        for proj in data["projects"]:
            st.markdown(f"""
            <div class='resume-card'>
                <strong style="font-size: 1.1rem; color: #10b981;">🚀 {proj['name']}</strong>
                <p style="margin-top: 10px; font-size: 0.95rem; line-height: 1.5;">{proj['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_edu:
        st.markdown("<div class='sec-header'>Education</div>", unsafe_allow_html=True)
        for edu in data["education"]:
            st.markdown(f"""
            <div class='resume-card'>
                <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                    <strong style="font-size: 1.15rem; color: #3b82f6;">🎓 {edu['institution']}</strong>
                    <span style="font-size: 0.85rem; color: #6b7280;">📍 {edu['location']}</span>
                </div>
                <div style="font-weight: 500; margin-top: 6px; font-size: 0.95rem;">{edu['degree']}</div>
            """, unsafe_allow_html=True)
            if edu["details"]:
                st.markdown("<ul style='margin-top: 6px; padding-left: 20px; font-size: 0.9rem;'>", unsafe_allow_html=True)
                for detail in edu["details"]:
                    st.markdown(f"<li>{detail}</li>", unsafe_allow_html=True)
                st.markdown("</ul>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 4: CERTIFICATIONS & SUMMARY ---
with tabs[3]:
    st.markdown("<div class='sec-header'>Professional Summary</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        font-size: 1.05rem; 
        line-height: 1.6; 
        padding: 20px; 
        background-color: rgba(59, 130, 246, 0.05); 
        border-left: 4px solid #3b82f6; 
        border-radius: 4px;
        margin-bottom: 25px;
    ">
        {data['summary']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sec-header'>Certifications & Honors</div>", unsafe_allow_html=True)
    for cert in data["certifications"]:
        st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            padding: 12px 16px; 
            background: rgba(255, 255, 255, 0.02); 
            border: 1px solid rgba(128,128,128,0.15); 
            border-radius: 8px; 
            margin-bottom: 10px;
        ">
            <span style="font-size: 1.3rem; margin-right: 12px;">🏅</span>
            <span style="font-size: 0.95rem;">{cert}</span>
        </div>
        """, unsafe_allow_html=True)
