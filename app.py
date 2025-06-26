import streamlit as st
import pandas as pd
from resume_parser import parse_resume_file
from jd_parser import parse_job_description
from similarity_scorer import calculate_score
from skill_matcher import extract_skills_from_text, get_skill_match_score
from fpdf import FPDF
import base64

# ------------------------
# 1️⃣ Simple Login System
# ------------------------
def login():
    st.session_state['authenticated'] = False
    with st.form("login"):
        st.subheader("🔐 HR Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if username == "hr" and password == "secure123":
                st.success("✅ Login successful!")
                st.session_state['authenticated'] = True
            else:
                st.error("❌ Invalid credentials.")

if "authenticated" not in st.session_state:
    login()
    st.stop()

# ------------------------
# 2️⃣ Simulated Job Descriptions
# ------------------------
job_descriptions = {
    "Software Engineer (Python)": """
Looking for a skilled Python developer with:
- Flask or Django
- REST APIs
- PostgreSQL or MySQL
- Docker, Git
- Cloud (AWS or Azure)
- Bachelor's in Computer Science
""",
    "Frontend Developer": """
Need a Frontend Developer with:
- HTML, CSS, JS
- React/Angular
- API integration
- UI/UX design
""",
    "Data Analyst": """
Seeking a Data Analyst with:
- Excel, SQL
- Python for cleaning
- Power BI or Tableau
- KPI reporting
"""
}

# ------------------------
# 3️⃣ Page Setup
# ------------------------
st.set_page_config(page_title="ATS Resume Scorer", layout="wide")
st.title("📂 ATS Resume Scoring Dashboard")

# ------------------------
# 4️⃣ Upload + JD Selection
# ------------------------
uploaded_resumes = st.file_uploader("📄 Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

selected_role = st.selectbox("🧭 Select Job Role", list(job_descriptions.keys()))
job_description = job_descriptions[selected_role]
cleaned_jd = parse_job_description(job_description)
jd_skills = extract_skills_from_text(cleaned_jd)

with st.expander("📄 View Job Description"):
    st.code(job_description.strip(), language="markdown")

# ------------------------
# 5️⃣ PDF Report Generator
# ------------------------
def generate_pdf(resume_name, similarity_score, skill_score, matched_skills, missing_skills):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, txt="ATS Resume Match Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Resume: {resume_name}", ln=True)
    pdf.cell(200, 10, txt=f"Semantic Score: {similarity_score:.2f}/100", ln=True)
    pdf.cell(200, 10, txt=f"Skill Match Score: {skill_score:.2f}/100", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Matched Skills:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, ", ".join(sorted(matched_skills)) if matched_skills else "None")
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Missing Skills:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, ", ".join(sorted(missing_skills)) if missing_skills else "None")
    if missing_skills:
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt="Recommendations:", ln=True)
        pdf.set_font("Arial", size=12)
        for skill in sorted(missing_skills):
            pdf.cell(200, 10, txt=f"Consider learning: {skill.capitalize()}", ln=True)
    return pdf.output(dest='S').encode('latin1')

# ------------------------
# 6️⃣ Process and Score Resumes
# ------------------------
if uploaded_resumes:
    st.markdown("### 📊 Scored Resumes")
    results = []

    for resume in uploaded_resumes:
        resume_text = parse_resume_file(resume, resume.name)
        if not resume_text:
            st.error(f"Failed to parse {resume.name}")
            continue

        resume_skills = extract_skills_from_text(resume_text)
        skill_score, matched, missing = get_skill_match_score(resume_skills, jd_skills)
        sim_score = calculate_score(resume_text, cleaned_jd)

        results.append({
            "name": resume.name,
            "semantic_score": sim_score,
            "skill_score": skill_score,
            "matched": matched,
            "missing": missing,
            "text": resume_text
        })

    # ------------------------
    # 7️⃣ Show Sorted Results
    # ------------------------
    results.sort(key=lambda x: (x["semantic_score"] + x["skill_score"]) / 2, reverse=True)

    for res in results:
        with st.container():
            st.subheader(f"📄 {res['name']}")
            col1, col2 = st.columns(2)
            col1.metric("🧠 Semantic Score", f"{res['semantic_score']:.2f}/100")
            col2.metric("🛠️ Skill Match", f"{res['skill_score']:.2f}/100")

            st.markdown("**✅ Matched Skills**")
            st.success(", ".join(res["matched"]) if res["matched"] else "None")

            st.markdown("**❌ Missing Skills**")
            st.error(", ".join(res["missing"]) if res["missing"] else "None")

            if res["missing"]:
                st.markdown("**💡 Recommendations**")
                for skill in res["missing"]:
                    st.info(f"Consider learning: {skill.capitalize()}")

            with st.expander("🧾 View Parsed Resume Text"):
                st.text_area("Resume Text", res["text"][:3000], height=200)

            pdf_data = generate_pdf(res["name"], res["semantic_score"], res["skill_score"], res["matched"], res["missing"])
            b64 = base64.b64encode(pdf_data).decode()
            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{res["name"]}_report.pdf">📄 Download PDF Report</a>', unsafe_allow_html=True)
