import os
import json
import html
from typing import List

import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# ================================================================
# CAREER COMPASS AI
# Install: py -m pip install -U streamlit google-genai pydantic
# Run:     py -m streamlit run app.py
# ================================================================

# ================================================================
# GEMINI API KEY - PASTE YOUR NEW KEY HERE FOR LOCAL TESTING
# Better: set the GEMINI_API_KEY environment variable.
# Do not reuse the key previously shared in chat.
# ================================================================
GEMINI_API_KEY = "AQ.Ab8RN6LGx7usnT7rpkxg-AH8cqLFg2ZqqQlW6hIa5fy18g8kqw"
MODEL_NAME = "gemini-flash-lite-latest"

st.set_page_config(
    page_title="Career Compass AI",
    page_icon="Career Compass",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = r"""
<style>
:root {
  --bg:#050816; --surface:#0e1528; --surface2:#121c33;
  --text:#f8fafc; --muted:#94a3b8; --purple:#8b5cf6;
  --blue:#3b82f6; --cyan:#22d3ee; --green:#34d399;
}
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 10% 10%, rgba(139,92,246,.18), transparent 28%),
    radial-gradient(circle at 90% 15%, rgba(34,211,238,.11), transparent 28%),
    radial-gradient(circle at 50% 100%, rgba(59,130,246,.10), transparent 30%),
    var(--bg);
  color:var(--text);
}
.block-container {max-width:1450px;padding-top:2rem;padding-bottom:4rem;}
.hero {
  position:relative;overflow:hidden;padding:58px 48px;margin-bottom:32px;
  border-radius:30px;border:1px solid rgba(255,255,255,.09);
  background:linear-gradient(135deg,rgba(139,92,246,.24),rgba(59,130,246,.10),rgba(14,21,40,.97));
  box-shadow:0 30px 100px rgba(0,0,0,.38);
}
.hero:before {content:"";position:absolute;width:380px;height:380px;border-radius:50%;right:-120px;top:-190px;background:radial-gradient(circle,rgba(139,92,246,.42),transparent 70%);}
.hero-content {position:relative;z-index:2;}
.brand {color:#c4b5fd;font-size:15px;font-weight:800;letter-spacing:1.4px;}
.hero h1 {font-size:clamp(42px,6vw,76px);line-height:1;letter-spacing:-3px;margin:18px 0;font-weight:900;}
.gradient-text {background:linear-gradient(90deg,#a78bfa,#60a5fa,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-description {color:#b7c3d8;max-width:820px;font-size:18px;line-height:1.75;}
.section-title {font-size:30px;font-weight:800;margin-top:20px;margin-bottom:5px;}
.section-subtitle {color:var(--muted);margin-bottom:24px;line-height:1.6;}
.glass-card {padding:24px;margin:14px 0 20px;border-radius:22px;border:1px solid rgba(255,255,255,.08);background:linear-gradient(145deg,rgba(18,28,51,.96),rgba(8,13,27,.96));box-shadow:0 15px 55px rgba(0,0,0,.22);}
.career-card {padding:28px;margin:28px 0 16px;border-radius:23px;border:1px solid rgba(139,92,246,.28);background:linear-gradient(135deg,rgba(139,92,246,.20),rgba(34,211,238,.07));}
.career-name {font-size:29px;font-weight:850;}
.ai-score {display:inline-block;margin-top:10px;padding:7px 13px;border-radius:999px;color:#6ee7b7;background:rgba(52,211,153,.10);border:1px solid rgba(52,211,153,.25);font-size:12px;font-weight:800;}
.metric-card {min-height:110px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:18px;margin-bottom:14px;border-radius:18px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.035);}
.metric-number {font-size:31px;font-weight:900;}
.metric-label {margin-top:5px;color:#8fa0b9;font-size:12px;}
.roadmap-item {display:flex;gap:16px;margin-bottom:16px;}
.roadmap-number {min-width:48px;height:48px;display:flex;align-items:center;justify-content:center;border-radius:50%;font-weight:900;background:linear-gradient(135deg,#8b5cf6,#06b6d4);}
.roadmap-content {flex:1;padding:18px;border-radius:17px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.035);}
.roadmap-content li {color:#aab7cc;margin-bottom:7px;line-height:1.55;}
.stTextInput input,.stTextArea textarea {background:#0a1222!important;color:#f8fafc!important;border:1px solid #27344e!important;border-radius:12px!important;}
div[data-baseweb="select"] > div {background:#0a1222!important;border-color:#27344e!important;}
.stButton > button {width:100%;min-height:54px;border:none;border-radius:14px;color:white;font-size:16px;font-weight:800;background:linear-gradient(135deg,#7c3aed,#2563eb);box-shadow:0 12px 35px rgba(124,58,237,.30);}
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#080d1b,#050812);border-right:1px solid rgba(255,255,255,.07);}
.sidebar-brand {font-size:24px;font-weight:850;}
.sidebar-description {margin-top:9px;color:#8997af;font-size:13px;line-height:1.7;}
.footer {text-align:center;color:#64748b;padding:45px 0 12px;line-height:1.8;font-size:13px;}
@media(max-width:768px){.hero{padding:38px 24px}.hero h1{font-size:42px;letter-spacing:-2px}.hero-description{font-size:15px}}

/* FORCE HIGH-CONTRAST TEXT */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4 { color:#F8FAFC; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 { color:#F8FAFC; }
[data-testid="stWidgetLabel"] p { color:#E2E8F0!important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color:#E2E8F0; }
.stTextInput input,.stTextArea textarea { -webkit-text-fill-color:#F8FAFC!important; caret-color:#FFFFFF!important; }
.stTextInput input::placeholder,.stTextArea textarea::placeholder { color:#91A4C4!important; -webkit-text-fill-color:#91A4C4!important; opacity:1!important; }
div[data-baseweb="select"] span { color:#F8FAFC!important; }
[data-testid="stAlert"] p { color:inherit!important; }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color:#F8FAFC!important; }

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


class CareerMatch(BaseModel):
    career: str
    fit_score: int = Field(ge=0, le=100, description="Profile alignment score, not an employment probability")
    why_it_matches: List[str]
    education_fit: str
    skill_fit: str
    interest_fit: str
    skill_gaps: List[str]
    job_titles: List[str]
    industries: List[str]
    tradeoffs: List[str]


class Roadmap(BaseModel):
    first_90_days: List[str]
    months_3_6: List[str]
    months_6_12: List[str]


class PortfolioProject(BaseModel):
    name: str
    description: str
    skills: List[str]


class CareerAnalysis(BaseModel):
    profile_summary: str
    career_matches: List[CareerMatch]
    recommended_path: Roadmap
    projects: List[PortfolioProject]
    next_skills: List[str]
    important_note: str


def safe(value) -> str:
    return html.escape(str(value))


def get_api_key() -> str:
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        secret_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if secret_key:
            return secret_key
    except Exception:
        pass
    local_key = GEMINI_API_KEY.strip()
    if local_key and local_key != "PASTE_YOUR_NEW_GEMINI_API_KEY_HERE":
        return local_key
    return ""


def validate_profile(education: str, degree: str, skills: str, interests: str) -> List[str]:
    errors = []
    if not education:
        errors.append("Please select your education level.")
    if not degree.strip():
        errors.append("Please enter your degree or specialization.")
    if not skills.strip():
        errors.append("Please enter your current skills.")
    if not interests.strip():
        errors.append("Please enter your interests.")
    return errors


def analyze_career(education, degree, skills, interests, experience, work_preferences, location, goals):
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Gemini API key is missing.")

    client = genai.Client(api_key=api_key)
    preferences = ", ".join(work_preferences) if work_preferences else "Not provided"
    experience_value = experience.strip() or "Not provided"
    location_value = location.strip() or "Not provided"
    goals_value = goals.strip() or "Not provided"

    prompt = f"""
You are Career Compass AI, a practical career exploration assistant for students and early-career professionals.

USER PROFILE
Education: {education}
Degree / specialization: {degree}
Current skills: {skills}
Interests: {interests}
Experience: {experience_value}
Preferred work areas: {preferences}
Preferred location: {location_value}
Career goal: {goals_value}

TASK
Return exactly 4 realistic, distinct career directions.
For every career provide the career name, a fit score from 0 to 100, reasons for the match, education fit, skill fit, interest fit, realistic skill gaps, possible early-career job titles, relevant industries, and meaningful trade-offs.

Then create one practical 12-month roadmap divided into first 90 days, months 3-6, and months 6-12.
Recommend practical portfolio projects and identify the most useful next skills.

RULES
The fit score is only an AI profile-alignment heuristic and is not an employment probability.
Do not guarantee employment, salary, promotion, success, or future demand.
Do not invent employers, current vacancies, salaries, statistics, or certifications.
If important profile information is missing, say so in the important note.
Keep the result specific, realistic, and actionable.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type="application/json",
            response_schema=CareerAnalysis,
        ),
    )

    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, CareerAnalysis):
            return parsed
        return CareerAnalysis.model_validate(parsed)

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return CareerAnalysis.model_validate_json(response.text)


st.markdown(r"""
<div class="hero">
  <div class="hero-content">
    <div class="brand">CAREER COMPASS AI</div>
    <h1>Find the career<br><span class="gradient-text">built around you.</span></h1>
    <div class="hero-description">
      Discover career possibilities based on your skills, education, interests and ambitions.<br><br>
      Career Compass AI analyzes your profile, identifies skill gaps and creates a personalized 12-month roadmap.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-brand">Career Compass</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-description">AI-powered career discovery for students and early-career professionals.</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### Career Journey")
    st.markdown("""
**01 · Build Profile**  
Education, skills and interests

**02 · AI Analysis**  
Analyze your profile

**03 · Career Matches**  
Explore different directions

**04 · Skill Gaps**  
Discover what to learn

**05 · Roadmap**  
Build a 12-month plan

**06 · Portfolio**  
Create evidence of your skills
""")
    st.divider()
    if get_api_key():
        st.success("Gemini AI Connected")
    else:
        st.warning("Gemini API Key Missing")
    st.caption("AI guidance is informational and does not guarantee career outcomes.")

st.markdown('<div class="section-title">Build Your Career Profile</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Tell Career Compass about your education, skills, interests and career ambitions.</div>', unsafe_allow_html=True)

left, right = st.columns(2)
with left:
    education = st.selectbox("Education Level", ["High School", "Diploma", "Bachelor's Degree", "Master's Degree", "MBA / PGDM", "PhD", "Other"])
    degree = st.text_input("Degree / Specialization", placeholder="Example: B.Tech Computer Science", max_chars=300)
    skills = st.text_area("Current Skills", placeholder="Python, Excel, SQL, communication, analytics...", height=150, max_chars=3000)
with right:
    interests = st.text_area("Interests", placeholder="AI, technology, business, finance, psychology...", height=150, max_chars=3000)
    experience = st.text_area("Experience / Projects", placeholder="Internships, jobs, projects, freelancing, college projects...", height=150, max_chars=3000)

work_preferences = st.multiselect("Work Areas That Interest You", [
    "Artificial Intelligence", "Software Engineering", "Data & Analytics", "Cybersecurity",
    "Cloud Computing", "Business & Strategy", "Product Management", "Consulting", "Finance",
    "Marketing", "Research", "Design & Creativity", "Operations", "Leadership", "Entrepreneurship"
])

location_col, goal_col = st.columns(2)
with location_col:
    location = st.text_input("Preferred Location", placeholder="Mumbai, Pune, Bengaluru, Dubai, Remote...", max_chars=200)
with goal_col:
    goals = st.text_input("Career Goal", placeholder="Example: Become an AI Engineer", max_chars=500)

analyze_button = st.button("CREATE MY AI CAREER ROADMAP", use_container_width=True, type="primary")

if analyze_button:
    errors = validate_profile(education, degree, skills, interests)
    if errors:
        for error in errors:
            st.warning(error)
    elif not get_api_key():
        st.error("Gemini API key is missing.")
        st.info('At the top of app.py, replace PASTE_YOUR_NEW_GEMINI_API_KEY_HERE with your NEW key, or set the GEMINI_API_KEY environment variable.')
    else:
        progress = st.progress(10, text="Preparing your profile...")
        try:
            progress.progress(35, text="Analyzing your skills and interests...")
            result = analyze_career(education, degree, skills, interests, experience, work_preferences, location, goals)
            progress.progress(80, text="Building your roadmap...")
            st.session_state["career_result"] = result
            progress.progress(100, text="Career roadmap complete!")
            st.success("Your personalized Career Compass is ready!")
        except Exception as error:
            progress.empty()
            st.error("Career analysis failed.")
            st.info("Check your Gemini API key, internet connection, model access, and installed packages.")
            with st.expander("Technical Error Details"):
                st.code(str(error))

if "career_result" in st.session_state:
    result: CareerAnalysis = st.session_state["career_result"]
    st.divider()
    st.markdown('<div class="section-title">Your AI Career Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Explore several directions based on the profile information you provided.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="glass-card"><h3>Profile Insight</h3><p style="color:#AAB7CC;line-height:1.8;margin-bottom:0">{safe(result.profile_summary)}</p></div>', unsafe_allow_html=True)

    for index, career in enumerate(result.career_matches, start=1):
        st.markdown(f'<div class="career-card"><div class="career-name">{index}. {safe(career.career)}</div><div class="ai-score">AI FIT SCORE · {career.fit_score}/100</div></div>', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{career.fit_score}</div><div class="metric-label">PROFILE ALIGNMENT</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{len(career.skill_gaps)}</div><div class="metric-label">SKILL GAPS</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-number">{len(career.job_titles)}</div><div class="metric-label">JOB DIRECTIONS</div></div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Why This Career Matches")
            for reason in career.why_it_matches:
                st.write("✓", reason)
            st.markdown("### Education Fit")
            st.info(career.education_fit)
            st.markdown("### Skill Fit")
            st.info(career.skill_fit)
        with col_b:
            st.markdown("### Interest Fit")
            st.info(career.interest_fit)
            st.markdown("### Skill Gaps")
            for gap in career.skill_gaps:
                st.markdown(f'<div class="glass-card" style="padding:14px;margin:8px 0">{safe(gap)}</div>', unsafe_allow_html=True)

        st.markdown("### Possible Job Titles")
        for job in career.job_titles:
            st.write("•", job)
        st.markdown("### Relevant Industries")
        for industry in career.industries:
            st.write("•", industry)
        st.markdown("### Things To Consider")
        for tradeoff in career.tradeoffs:
            st.write("•", tradeoff)
        st.divider()

    st.markdown('<div class="section-title">Your 12-Month Career Roadmap</div>', unsafe_allow_html=True)
    roadmap_stages = [
        ("01", "First 90 Days", result.recommended_path.first_90_days),
        ("02", "Months 3-6", result.recommended_path.months_3_6),
        ("03", "Months 6-12", result.recommended_path.months_6_12),
    ]
    for number, title, actions in roadmap_stages:
        items = "".join(f"<li>{safe(action)}</li>" for action in actions)
        st.markdown(f'<div class="roadmap-item"><div class="roadmap-number">{number}</div><div class="roadmap-content"><h4>{safe(title)}</h4><ul>{items}</ul></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Portfolio Projects</div>', unsafe_allow_html=True)
    for project in result.projects:
        project_skills = " · ".join(safe(skill) for skill in project.skills)
        st.markdown(f'<div class="glass-card"><h3>{safe(project.name)}</h3><p style="color:#AAB7CC;line-height:1.7">{safe(project.description)}</p><div style="color:#8FA0B9;font-size:13px"><strong>Skills:</strong> {project_skills}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Skills To Learn Next</div>', unsafe_allow_html=True)
    if result.next_skills:
        count = min(4, len(result.next_skills))
        cols = st.columns(count)
        for index, skill in enumerate(result.next_skills):
            with cols[index % count]:
                st.markdown(f'<div class="metric-card"><div class="metric-number">{index + 1}</div><div style="margin-top:8px;font-weight:700">{safe(skill)}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="glass-card"><h3>Career Compass Advice</h3><p style="color:#AAB7CC;line-height:1.8;margin-bottom:0">{safe(result.important_note)}</p></div>', unsafe_allow_html=True)

    report_json = json.dumps(result.model_dump(mode="json"), indent=4, ensure_ascii=False)
    st.download_button("DOWNLOAD MY CAREER REPORT", data=report_json, file_name="career_compass_report.json", mime="application/json", use_container_width=True)

st.markdown(r"""
<div class="footer">
<strong>Career Compass AI</strong><br><br>
Discover possibilities · Build skills · Create your path<br><br>
AI-generated career guidance is informational. Research career options independently and consider real-world experience and current job requirements.
</div>
""", unsafe_allow_html=True)
