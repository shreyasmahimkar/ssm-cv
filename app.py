import streamlit as st
import json
import os
import re
import base64
from resume_parser import get_resume_data, DOC_URL

def render_markdown_links(text):
    if not text:
        return ""
    return re.sub(
        r'\[(.*?)\]\((.*?)\)',
        r'<a href="\2" target="_blank" style="color: #3b82f6; text-decoration: underline; font-weight: 500;">\1</a>',
        text
    )

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            pass
    return None

def load_publications():
    pub_file = "publications.json"
    if os.path.exists(pub_file):
        try:
            with open(pub_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            pass
    return [
        {
            "title": "Analyzing Information Asymmetry in Financial Markets Using Machine Learning",
            "authors": "Rahul Arulkumaran, Shreyas Mahimkar, Sumit Shekhar, Aayush Jain, Arpit Jain",
            "journal": "International Journal of Progressive Research in Engineering Management and Science (IJPREMS)",
            "year": "2021",
            "citations": 88,
            "doi": "10.58257/IJPREMS16",
            "link": "https://doi.org/10.58257/IJPREMS16",
            "summary": "Applies supervised machine learning classifiers to detect patterns of information asymmetry and potential insider trading in financial markets. By analyzing order book dynamics and transaction history, the models can identify anomalous trading behaviors, contributing to market fairness and regulatory surveillance.",
            "type": "Journal"
        },
        {
            "title": "Predicting Crime Locations Using Big Data Analytics and Map-Reduce Techniques",
            "authors": "Shreyas Mahimkar",
            "journal": "The International Journal of Engineering Research (TIJER)",
            "year": "2021",
            "citations": 82,
            "doi": "",
            "link": "https://www.researchgate.net/publication/387312142_Predicting_Crime_Locations_Using_Big_Data_Analytics_and_Map-Reduce_Techniques",
            "summary": "Develops a distributed predictive modeling framework using Map-Reduce and Apache Hadoop to identify spatial-temporal crime hotspots from municipal records. Utilizes customized spatial algorithms to assist law enforcement agencies in predictive policing and optimal resource deployment.",
            "type": "Journal"
        },
        {
            "title": "Predictive Analysis of TV Program Viewership Using Random Forest Algorithms",
            "authors": "Shreyas Mahimkar",
            "journal": "International Journal of Research and Analytical Reviews (IJRAR)",
            "year": "2021",
            "citations": 64,
            "doi": "",
            "link": "https://www.researchgate.net/publication/387576165_Predictive_Analysis_of_TV_Program_Viewership_Using_Random_Forest_Algorithms",
            "summary": "Compares ensemble learning methods, specifically Random Forest, to build predictive models that forecast TV program popularity and viewer retention. The study incorporates demographic attributes and historical viewing habits to improve forecasting accuracy by 30%.",
            "type": "Journal"
        },
        {
            "title": "Analysing TV Advertising Campaign Effectiveness with Lift and Attribution Models",
            "authors": "Shreyas Mahimkar",
            "journal": "Journal of Emerging Technologies and Innovative Research (JETIR)",
            "year": "2021",
            "citations": 58,
            "doi": "",
            "link": "https://www.researchgate.net/publication/387183306_Analysing_TV_Advertising_Campaign_Effectiveness_with_Lift_and_Attribution_Models",
            "summary": "Formulates multi-touch attribution and lift estimation algorithms to evaluate the true impact of TV advertising campaigns by linking TV ad exposure to downstream conversion events, resolving local sampling constraints and optimizing large-scale ad spend.",
            "type": "Journal"
        },
        {
            "title": "Targeting TV Viewers More Effectively Using K-Means Clustering",
            "authors": "Shreyas Mahimkar, Arpit Jain, Om Goel",
            "journal": "International Journal of Innovative Research in Technology (IJIRT)",
            "year": "2022",
            "citations": 51,
            "doi": "",
            "link": "https://www.researchgate.net/publication/387312528_Targeting_TV_Viewers_More_Effectively_Using_K-_Means_Clustering",
            "summary": "Details an audience segmentation methodology using unsupervised K-Means clustering on TV viewership behavior. Groups viewers into high-affinity cohorts to assist advertisers in increasing ad-targeting precision by 45%.",
            "type": "Journal"
        },
        {
            "title": "Enhancing TV Audience Rating Predictions Through Linear Regression Models",
            "authors": "Shreyas Mahimkar",
            "journal": "The International Journal of Engineering Research (TIJER)",
            "year": "2023",
            "citations": 38,
            "doi": "",
            "link": "https://www.researchgate.net/publication/387185257_Enhancing_TV_Audience_Rating_Predictions_Through_Linear_Regression_Models",
            "summary": "Proposes a linear regression framework optimized with feature engineering to predict TV show audience ratings based on genre, air time, and historical performance. Focuses on key predictive signals to enhance forecast reliability for media networks.",
            "type": "Journal"
        },
        {
            "title": "Extracting Insights from TV Viewership Data with Spark and Scala",
            "authors": "Shreyas Mahimkar, Kumud Kumar Agrawal, Shubham Jain",
            "journal": "International Journal of Advanced Research and Interdisciplinary Scientific Endeavours (IJARISE)",
            "year": "2024",
            "citations": 24,
            "doi": "10.61359/11.2206-2413",
            "link": "https://rjpn.org/ijnti/papers/IJNTI2401006.pdf",
            "summary": "Introduces a scalable data processing pipeline using Apache Spark and Scala to parse, process, and analyze massive TV viewership logs. The parallel framework processes over 100 million daily records, driving computational efficiency improvements of 40%.",
            "type": "Journal"
        },
        {
            "title": "Utilizing Machine Learning for Predictive Modelling of TV Viewership Trends",
            "authors": "Shreyas Mahimkar",
            "journal": "International Journal of Creative Research Thoughts (IJCRT)",
            "year": "2022",
            "citations": 16,
            "doi": "",
            "link": "https://www.researchgate.net/publication/387576341_Utilizing_Machine_Learning_for_Predictive_Modelling_of_TV_Viewership_Trends",
            "summary": "Applies machine learning classifiers to predict long-term TV viewership trends using demographic profiling and behavioral data. Focuses on temporal dependencies and changes in content consumer preferences.",
            "type": "Journal"
        }
    ]


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

/* Apply font and standard colors from Streamlit theme */
html, body, [class*="css"], .stMarkdown {
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
    color: var(--text-color);
    opacity: 0.8;
    font-weight: 500;
    margin-top: 2px;
    margin-bottom: 15px;
}

/* Section header styling */
.sec-header {
    font-size: 1.6rem;
    font-weight: 600;
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 6px;
    margin-top: 25px;
    margin-bottom: 15px;
}

/* Resume experience/education cards adapting to theme background */
.resume-card {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}
.resume-card:hover {
    transform: translateY(-2px);
    border-color: rgba(59, 130, 246, 0.4);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

/* Badge for skills */
.skill-tag {
    display: inline-block;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    color: #3b82f6;
    padding: 5px 12px;
    border-radius: 16px;
    margin: 4px;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Timeline elements */
.job-meta {
    font-size: 0.9rem;
    color: var(--text-color);
    opacity: 0.7;
    font-weight: 400;
    margin-bottom: 8px;
}

.job-company {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-color);
}

.role-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #3b82f6;
}

.role-dates {
    font-size: 0.9rem;
    color: var(--text-color);
    opacity: 0.65;
    font-weight: 500;
}

/* Publications styling */
.pub-stat-container {
    display: flex;
    justify-content: space-around;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}
.pub-stat-card {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(16, 185, 129, 0.08) 100%);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    flex: 1;
    min-width: 180px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}
.pub-stat-val {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 5px;
}
.pub-stat-label {
    font-size: 0.9rem;
    color: var(--text-color);
    opacity: 0.7;
    font-weight: 500;
}
.pub-card {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
}
.pub-card:hover {
    transform: translateY(-2px);
    border-color: rgba(16, 185, 129, 0.4);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}
.pub-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    line-height: 1.4;
}
.pub-authors {
    font-size: 0.95rem;
    color: var(--text-color);
    opacity: 0.85;
    margin-bottom: 6px;
    margin-top: 8px;
}
.pub-venue {
    font-size: 0.9rem;
    color: #10b981;
    font-weight: 500;
    margin-bottom: 12px;
}
.pub-citation-badge {
    background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
    color: white !important;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
    white-space: nowrap;
}
.pub-type-badge {
    display: inline-block;
    padding: 3px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 4px;
    margin-right: 8px;
    text-transform: uppercase;
}
.pub-type-journal {
    background-color: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.2);
}
.pub-type-conference {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.2);
}
.pub-type-article {
    background-color: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.2);
}
.pub-link-btn {
    display: inline-flex;
    align-items: center;
    background-color: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.2);
    color: #3b82f6;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s ease;
    margin-top: 10px;
}
.pub-link-btn:hover {
    background-color: #3b82f6;
    color: white !important;
    border-color: #3b82f6;
    text-decoration: none;
}
.pub-profile-link {
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
}
.pub-link-rg {
    background-color: rgba(0, 107, 180, 0.08);
    border: 1px solid rgba(0, 107, 180, 0.2);
    color: #006bb4 !important;
}
.pub-link-rg:hover {
    background-color: #006bb4;
    color: white !important;
    border-color: #006bb4;
    box-shadow: 0 4px 12px rgba(0, 107, 180, 0.15);
}
.pub-link-gs {
    background-color: rgba(66, 133, 244, 0.08);
    border: 1px solid rgba(66, 133, 244, 0.2);
    color: #4285f4 !important;
}
.pub-link-gs:hover {
    background-color: #4285f4;
    color: white !important;
    border-color: #4285f4;
    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.15);
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
publications = load_publications()

# Reset force refresh state
if st.session_state.force_refresh:
    st.session_state.force_refresh = False
    st.rerun()

if not data:
    st.error("Could not load resume data. Please check your internet connection or Google Doc configuration.")
    st.stop()

# --- SIDEBAR CONTENT ---
with st.sidebar:
    img_base64 = get_image_base64("coat_picture1.jpg")
    if img_base64:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 15px;">
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
                padding: 3px;
                border-radius: 24px;
                box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.3s ease;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                <img src="data:image/jpeg;base64,{img_base64}" style="
                    width: 140px;
                    height: 140px;
                    border-radius: 22px;
                    object-fit: cover;
                    object-position: center 0%;
                    background-color: white;
                    display: block;
                " />
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback to elegant CSS initials badge if image not found
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
    if st.button("🔄 Sync with Google Doc", use_container_width=True):
        st.session_state.force_refresh = True
        fetch_data.clear()
        st.rerun()

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
tabs = st.tabs(["💼 Experience", "🛠️ Skills", "🎓 Education", "🏅 Certifications & Summary", "📚 Publications"])

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
                        <span class="role-title">{role['title']}</span>
                        <span class="role-dates">📅 {role['dates']}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if role["description"]:
                    st.markdown(f"<p style='margin-top: 8px; font-size: 0.95rem; font-style: italic;'>{render_markdown_links(role['description'])}</p>", unsafe_allow_html=True)
                
                if role["bullets"]:
                    st.markdown("<ul style='margin-top: 8px; padding-left: 20px; font-size: 0.95rem;'>", unsafe_allow_html=True)
                    for bullet in role["bullets"]:
                        st.markdown(f"<li>{render_markdown_links(bullet)}</li>", unsafe_allow_html=True)
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

# --- TAB 3: EDUCATION ---
with tabs[2]:
    st.markdown("<div class='sec-header'>Education</div>", unsafe_allow_html=True)
    if data.get("education"):
        edu_cols = st.columns(len(data["education"]))
        for index, edu in enumerate(data["education"]):
            with edu_cols[index]:
                st.markdown(f"""
                <div class='resume-card' style="height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                        <strong style="font-size: 1.15rem; color: #3b82f6;">🎓 {edu['institution']}</strong>
                        <span style="font-size: 0.85rem; color: #6b7280;">📍 {edu['location']}</span>
                    </div>
                    <div style="font-weight: 500; margin-top: 6px; font-size: 0.95rem;">{edu['degree']}</div>
                """, unsafe_allow_html=True)
                if edu["details"]:
                    st.markdown("<ul style='margin-top: 6px; padding-left: 20px; font-size: 0.9rem;'>", unsafe_allow_html=True)
                    for detail in edu["details"]:
                        st.markdown(f"<li>{render_markdown_links(detail)}</li>", unsafe_allow_html=True)
                    st.markdown("</ul>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No education information available.")

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
            <span style="font-size: 0.95rem;">{render_markdown_links(cert)}</span>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 5: PUBLICATIONS ---
with tabs[4]:
    st.markdown("<div class='sec-header'>Publications & Research</div>", unsafe_allow_html=True)
    
    # High-level Profile Links
    links_html = (
        f"<div style='display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap;'>"
        f"<a href='https://www.researchgate.net/profile/Shreyas-Mahimkar-2' target='_blank' class='pub-profile-link pub-link-rg'>🎓 ResearchGate Profile</a>"
        f"<a href='https://scholar.google.com/citations?user=kU7YaVYAAAAJ&hl=en' target='_blank' class='pub-profile-link pub-link-gs'>📚 Google Scholar Profile</a>"
        f"</div>"
    )
    st.markdown(links_html, unsafe_allow_html=True)
    
    # Official ResearchGate metrics
    total_pubs = 32
    total_citations = 569
    total_reads = 2945
    h_index = 14
            
    # Render Stats Cards
    stats_html = (
        f"<div class='pub-stat-container'>"
        f"<div class='pub-stat-card'>"
        f"<div class='pub-stat-val'>{total_pubs}</div>"
        f"<div class='pub-stat-label'>Publications</div>"
        f"</div>"
        f"<div class='pub-stat-card'>"
        f"<div class='pub-stat-val'>{total_reads:,}</div>"
        f"<div class='pub-stat-label'>Profile Reads</div>"
        f"</div>"
        f"<div class='pub-stat-card'>"
        f"<div class='pub-stat-val'>{total_citations}</div>"
        f"<div class='pub-stat-label'>Citations</div>"
        f"</div>"
        f"<div class='pub-stat-card'>"
        f"<div class='pub-stat-val'>{h_index}</div>"
        f"<div class='pub-stat-label'>h-index</div>"
        f"</div>"
        f"</div>"
    )
    st.markdown(stats_html, unsafe_allow_html=True)
    
    # Filters & Controls
    col_search, col_sort = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search publications", placeholder="Search by title, keywords, authors, or venue...")
    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            ["Citations (High to Low)", "Year (Newest to Oldest)", "Title (A-Z)"]
        )
        
    # Filter list
    filtered_pubs = []
    for pub in publications:
        if search_query:
            query = search_query.lower()
            in_title = query in pub.get("title", "").lower()
            in_authors = query in pub.get("authors", "").lower()
            in_venue = query in pub.get("journal", "").lower()
            in_summary = query in pub.get("summary", "").lower()
            if not (in_title or in_authors or in_venue or in_summary):
                continue
        filtered_pubs.append(pub)
        
    # Sort list
    if sort_by == "Citations (High to Low)":
        filtered_pubs = sorted(filtered_pubs, key=lambda x: x.get("citations", 0), reverse=True)
    elif sort_by == "Year (Newest to Oldest)":
        filtered_pubs = sorted(filtered_pubs, key=lambda x: x.get("year", ""), reverse=True)
    elif sort_by == "Title (A-Z)":
        filtered_pubs = sorted(filtered_pubs, key=lambda x: x.get("title", "").lower())
        
    # Render Publications
    if not filtered_pubs:
        st.info("No publications found matching your search criteria.")
    else:
        for pub in filtered_pubs:
            pub_type = pub.get("type", "Journal")
            type_class = f"pub-type-{pub_type.lower()}"
            
            highlighted_authors = pub.get("authors", "").replace(
                "Shreyas Mahimkar", 
                "<strong>Shreyas Mahimkar</strong>"
            )
            
            doi_link_html = ""
            if pub.get("doi"):
                doi_link_html = f"<span style='color: #6b7280; font-size: 0.85rem; margin-left: 15px;'>DOI: {pub.get('doi')}</span>"
                
            link_html = ""
            if pub.get("link"):
                link_html = f"<a href='{pub.get('link')}' target='_blank' class='pub-link-btn'>🔗 View Publication</a>"
                
            card_html = (
                f"<div class='pub-card'>"
                f"<div style='display: flex; justify-content: space-between; align-items: flex-start; gap: 15px; margin-bottom: 8px;'>"
                f"<div class='pub-title'>{pub.get('title')}</div>"
                f"<div class='pub-citation-badge'>💬 {pub.get('citations')} Citations</div>"
                f"</div>"
                f"<div class='pub-authors'>By: {highlighted_authors}</div>"
                f"<div class='pub-venue'>"
                f"<span class='pub-type-badge {type_class}'>{pub_type}</span>"
                f"{pub.get('journal')} ({pub.get('year')})"
                f"{doi_link_html}"
                f"</div>"
                f"<div style='font-size: 0.95rem; line-height: 1.5; opacity: 0.9; margin-top: 10px;'>"
                f"<strong>Summary:</strong> {pub.get('summary')}"
                f"</div>"
                f"<div style='margin-top: 10px;'>"
                f"{link_html}"
                f"</div>"
                f"</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
