import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Career Compass AI", page_icon="🎯", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#07111f,#0b1d35,#102a43);color:#f8fafc}.block-container{max-width:1180px;padding-top:2rem}.hero{padding:28px;border:1px solid #29435c;border-radius:24px;background:rgba(8,20,36,.82);box-shadow:0 18px 55px #0004}.hero h1{font-size:3rem;margin:0;background:linear-gradient(90deg,#67e8f9,#a78bfa);-webkit-background-clip:text;color:transparent}.hero p{font-size:1.12rem;color:#cbd5e1}.badge{display:inline-block;padding:7px 12px;border-radius:999px;background:#122b46;color:#67e8f9;margin-bottom:12px;font-weight:700}[data-testid="stForm"]{background:#0f1f31b3;padding:22px;border-radius:22px;border:1px solid #29435c}div.stButton>button,div.stFormSubmitButton>button{border:0;border-radius:12px;background:linear-gradient(90deg,#06b6d4,#7c3aed);color:white;font-weight:800;min-height:48px;width:100%}[data-testid="stSidebar"]{background:#071421}
</style>""", unsafe_allow_html=True)
st.markdown("""<div class="hero"><div class="badge">AI CAREER INTELLIGENCE</div><h1>Find the career built around you.</h1><p>Turn your skills, education, interests and ambitions into a personalized career roadmap powered by NVIDIA NIM and DeepSeek.</p></div>""", unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.header("⚙️ AI Settings")
    secret_key = "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"
    try: secret_key = st.secrets.get("NVIDIA_API_KEY", "")
    except Exception: pass
    api_key = "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"
    model = "meta/muse-glimmer-30b"
    st.caption("Paste the exact model ID from NVIDIA Build if model availability changes.")

left,right=st.columns([1.05,.95],gap="large")
with left:
    st.subheader("👤 Build your career profile")
    with st.form("career_form"):
        name=st.text_input("Name",placeholder="Your name")
        education=st.selectbox("Current education",["School (8-10)","Higher Secondary (11-12)","Diploma","Undergraduate","Postgraduate","Working professional","Other"])
        field=st.text_input("Field / specialization",placeholder="e.g. Computer Science, Commerce")
        skills=st.text_area("Skills",placeholder="Python, communication, Excel, design...")
        interests=st.text_area("Interests",placeholder="AI, finance, healthcare, creativity...")
        strengths=st.text_area("Strengths",placeholder="Analytical thinking, leadership...")
        goals=st.text_area("Career goals",placeholder="What work, life or impact do you want?")
        location=st.text_input("Preferred location / work mode",placeholder="e.g. Mumbai, India, Remote")
        experience=st.slider("Experience (years)",0,30,0)
        submitted=st.form_submit_button("✨ Build My Career Roadmap")
with right:
    st.subheader("🚀 What you will get")
    st.info("Top career matches • skill gaps • learning plan • projects • 90-day action plan • alternatives")
    st.markdown("### How it works\n**1. Profile** → Tell the AI what you know and enjoy.\n\n**2. Match** → DeepSeek evaluates suitable directions.\n\n**3. Roadmap** → Get practical next steps and portfolio ideas.")

if submitted:
    if not api_key:
        st.error("Add your NVIDIA API key in the sidebar first."); st.stop()
    if not skills.strip() or not interests.strip():
        st.warning("Please add at least your skills and interests."); st.stop()
    prompt=f"""You are Career Compass AI, a practical professional career coach. Analyze this profile without guaranteeing employment or salary.
Name: {name or 'Not provided'}
Education: {education}
Field: {field or 'Not provided'}
Skills: {skills}
Interests: {interests}
Strengths: {strengths or 'Not provided'}
Goals: {goals or 'Not provided'}
Location/work mode: {location or 'Not provided'}
Experience: {experience} years

Return polished Markdown with these sections:
# Career Compass Result
## Profile Snapshot
## Top 5 Career Matches
For each give a heuristic fit score /100, why it fits, typical work, strengths, skill gaps and first step.
## Best Match: Deep Dive
## Skills Gap Matrix
Use table: Skill | Current signal | Target level | Action.
## Personalized Learning Roadmap
0-30, 31-60, 61-90 days, and 3-12 months.
## Portfolio Projects
Three projects from beginner to advanced.
## Job Search Strategy
## Alternative Paths
## This Week
Five specific actions. Be encouraging, realistic and concise. Never invent current local statistics."""
    try:
        client=OpenAI(base_url="https://integrate.api.nvidia.com/v1",api_key=api_key)
        with st.spinner("DeepSeek is building your roadmap..."):
            r=client.chat.completions.create(model=model.strip(),messages=[{"role":"system","content":"You are a professional career guidance assistant."},{"role":"user","content":prompt}],temperature=.6,top_p=.9,max_tokens=3500)
        result=r.choices[0].message.content or "No response returned."
        st.divider(); st.markdown(result)
        st.download_button("⬇️ Download Career Roadmap",result,file_name="career_roadmap.md",mime="text/markdown",use_container_width=True)
    except Exception as e:
        st.error("NVIDIA API request failed."); st.code(str(e)); st.caption("Check the API key, exact model ID, connectivity and model access.")

st.divider(); st.caption("Career Compass AI • AI guidance should support, not replace, your own research and judgment.")
