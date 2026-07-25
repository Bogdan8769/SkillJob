"""
pages/3_Roadmap.py
--------------------
Randează roadmap-ul (stil roadmap.sh) pentru jobul selectat.
Include export de date PDF și resurse de învățare dinamice.
"""

import urllib.parse
import streamlit as st
import datetime
from fpdf import FPDF

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from database import JOBS
from roadmap_mermaid import (
    generate_roadmap_mermaid,
    render_mermaid_roadmap,
    render_roadmap_legend,
    _split_into_tiers_by_relation,
    TIER_LABELS,
    TIER_ICONS
)

bootstrap_page("Roadmap", icon="🗺️")
require_login()
render_nav_sidebar()
render_account_sidebar()

ROADMAP_CSS = """
<style>
.sj-roadmap-header {
    background: linear-gradient(120deg, #1B2430, #2F6F5E);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.2rem;
    color: #fff;
}
.sj-roadmap-header .sj-eyebrow2 {
    text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.72rem;
    font-weight: 700; color: #C99A56; margin: 0;
}
.sj-roadmap-header h2 { margin: 0.2rem 0; font-size: 1.8rem; font-weight: 800; }
.sj-roadmap-header p { margin: 0; color: rgba(255,255,255,0.82); font-size: 0.92rem; }

.sj-salary-badge { 
    margin-top: 1rem; display: inline-block; background: rgba(255,255,255,0.15); 
    padding: 6px 14px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; 
    border: 1px solid rgba(255,255,255,0.3); 
}

.sj-roadmap-shell { 
    background: #FBFCFD; border: 1px solid #ECEFF3; border-radius: 20px; 
    padding: 0.6rem 1rem 1.2rem 1rem; box-shadow: 0 10px 30px rgba(16,24,40,0.06); 
}

/* FIX PENTRU EXPANDERE (Negru pe Negru) */
[data-testid="stExpander"] details summary {
    background-color: #1B2430 !important; 
    border-radius: 8px !important;
    padding: 10px 15px !important;
}
[data-testid="stExpander"] details summary p {
    color: #FFFFFF !important; 
    font-weight: 600 !important;
    font-size: 1.05rem !important;
}
[data-testid="stExpander"] details summary svg {
    color: #C99A56 !important; 
}
[data-testid="stExpander"] details {
    border: 1px solid #ECEFF3 !important;
    border-radius: 8px !important;
    background: #FFFFFF !important; 
}

/* Stiluri pentru link-urile de învățare */
.sj-learn-link {
    text-decoration: none; font-size: 0.75rem; font-weight: 600;
    padding: 2px 8px; border-radius: 4px; margin-left: 6px;
    display: inline-block; transition: opacity 0.2s;
}
.sj-learn-link:hover { opacity: 0.8; }
.sj-yt { background-color: #FF0000; color: white !important; }
.sj-gg { background-color: #4285F4; color: white !important; }
</style>
"""
st.markdown(ROADMAP_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# UTILITARE & GENERATOR PDF
# ---------------------------------------------------------------------------
def get_learning_links(skill_name):
    query_yt = urllib.parse.quote(f"tutorial {skill_name}")
    query_gg = urllib.parse.quote(f"curs {skill_name}")
    link_yt = f"<a href='https://www.youtube.com/results?search_query={query_yt}' target='_blank' class='sj-learn-link sj-yt'>▶ YouTube</a>"
    link_gg = f"<a href='https://www.google.com/search?q={query_gg}' target='_blank' class='sj-learn-link sj-gg'>🔍 Cursuri</a>"
    return f"{link_yt} {link_gg}"

def sanitize_pdf_text(text):
    """Înlocuiește diacriticele pentru fontul standard PDF"""
    if not text: return ""
    replacements = {'ă':'a', 'â':'a', 'î':'i', 'ș':'s', 'ț':'t', 'Ă':'A', 'Â':'A', 'Î':'I', 'Ș':'S', 'Ț':'T'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

@st.cache_data(show_spinner=False)
def generate_pdf_export(job, domain, sal_lo, sal_hi, user_h, user_s, req_h, req_s):
    pdf = FPDF()
    pdf.add_page()

    # Culorile tale de brand
    color_moss = (47, 111, 94)
    color_brass = (201, 154, 86)
    color_text = (27, 36, 48)

    # Header colorat
    pdf.set_fill_color(*color_moss)
    pdf.rect(0, 0, 210, 40, 'F')

    pdf.set_y(15)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Plan de Cariera", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*color_brass)
    job_clean = sanitize_pdf_text(job.upper())
    pdf.cell(0, 8, job_clean, align="C", new_x="LMARGIN", new_y="NEXT")

    # Informații generale
    pdf.set_y(50)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*color_text)
    pdf.cell(0, 7, f"Domeniu: {sanitize_pdf_text(domain)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Salariu estimat: {sal_lo} - {sal_hi} RON", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Data generarii: {datetime.date.today().strftime('%d.%m.%Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    missing_h = [s for s in req_h if s not in user_h]
    owned_h = [s for s in req_h if s in user_h]

    # Secțiune: Hard Skills
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*color_moss)
    pdf.cell(0, 10, "1. Competente Tehnice (Hard Skills)", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*color_text)
    pdf.cell(0, 8, "Dezvoltate deja:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if not owned_h:
        pdf.cell(5); pdf.cell(0, 6, "Niciuna bifata inca.", new_x="LMARGIN", new_y="NEXT")
    for s in owned_h:
        pdf.cell(5); pdf.cell(0, 6, f"[+] {sanitize_pdf_text(s)}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "De invatat / Aprofundat:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for s in missing_h:
        pdf.cell(5); pdf.cell(0, 6, f"[-] {sanitize_pdf_text(s)}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    # Secțiune: Soft Skills
    missing_s = [s for s in req_s if s not in user_s]
    owned_s = [s for s in req_s if s in user_s]

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*color_brass)
    pdf.cell(0, 10, "2. Abilitati Personale (Soft Skills)", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*color_text)
    pdf.cell(0, 8, "Dezvoltate deja:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if not owned_s:
        pdf.cell(5); pdf.cell(0, 6, "Niciuna bifata inca.", new_x="LMARGIN", new_y="NEXT")
    for s in owned_s:
        pdf.cell(5); pdf.cell(0, 6, f"[+] {sanitize_pdf_text(s)}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "De invatat / Imbunatatit:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for s in missing_s:
        pdf.cell(5); pdf.cell(0, 6, f"[-] {sanitize_pdf_text(s)}", new_x="LMARGIN", new_y="NEXT")

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Generat de platforma SkillJob", align="C")

    return bytes(pdf.output())


# ---------------------------------------------------------------------------
# LOGICA PAGINII
# ---------------------------------------------------------------------------
job_name = st.session_state.get("selected_job")

if not job_name or job_name not in JOBS:
    st.info("Nu a fost selectată nicio ocupație încă.")
    st.write("")
    st.page_link("pages/2_Categorii.py", label="🗂️ Mergi la Categorii pentru a alege un job")
    st.stop()

info = JOBS.get(job_name, {})
salary_lo, salary_hi = info.get("salary_range", (0, 0))
hard_skills = info.get("hard_skills", [])
soft_skills = info.get("soft_skills", [])

# ==========================================
# 1. HEADER
# ==========================================
st.markdown(
    f'''<div class="sj-roadmap-header">
        <p class="sj-eyebrow2">Roadmap · {info.get("domain", "")}</p>
        <h2>{job_name}</h2>
        <p>{info.get("description", "")}</p>
        <div class="sj-salary-badge">💰 Salariu estimat pe piață: {salary_lo} - {salary_hi} RON</div>
    </div>''', unsafe_allow_html=True)

wd = st.session_state.get("wizard_data", {})
user_hard = wd.get("hard_skills", [])
user_soft = wd.get("soft_skills", [])
skill_relations = info.get("skill_relations", {})

# ==========================================
# 2. GRAFICUL MERMAID
# ==========================================
st.markdown('<div class="sj-roadmap-shell">', unsafe_allow_html=True)
if hard_skills:
    mermaid_code = generate_roadmap_mermaid(
        job_name, hard_skills, soft_skills,
        skill_relations=skill_relations, user_hard_skills=user_hard, user_soft_skills=user_soft
    )
    n_nodes = len(hard_skills) + len(soft_skills) + 1
    render_mermaid_roadmap(mermaid_code, height=min(760, 420 + n_nodes * 12))
    render_roadmap_legend()
else:
    st.markdown("<div style='padding: 3rem; text-align: center;'>Roadmap în curs de actualizare. 🚧</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. LISTA DETALIATĂ & RESURSE DE ÎNVĂȚARE
# ==========================================
if hard_skills or soft_skills:
    st.write("")
    st.markdown("### 🔍 Analiza completă a competențelor")
    st.markdown("<p style='color: var(--text-soft); font-size: 0.95rem; margin-bottom: 1.5rem;'>Descoperă resurse de învățare pentru abilitățile care îți lipsesc.</p>", unsafe_allow_html=True)

if hard_skills:
    n_tiers = min(4, max(1, len(hard_skills)))
    tiers = _split_into_tiers_by_relation(hard_skills, skill_relations, n_tiers)

    # Competențe tehnice
    for idx, tier_skills in enumerate(tiers):
        if not tier_skills: continue

        tier_name = TIER_LABELS[idx % len(TIER_LABELS)]
        tier_icon = TIER_ICONS[idx % len(TIER_ICONS)]
        owned_count = sum(1 for s in tier_skills if s in user_hard)

        with st.expander(f"{tier_icon} {tier_name} ({len(tier_skills)} competențe | Deții: {owned_count})"):
            for skill in tier_skills:
                if skill in user_hard:
                    st.markdown(f"<div style='color: #2E7D32; font-weight: 600; padding: 6px 0; border-bottom: 1px solid #F1F3F6;'>✅ {skill}</div>", unsafe_allow_html=True)
                else:
                    links = get_learning_links(skill)
                    st.markdown(f"<div style='color: #1B2430; padding: 6px 0; border-bottom: 1px solid #F1F3F6; display: flex; justify-content: space-between; align-items: center;'><span>◽ {skill}</span> <span>{links}</span></div>", unsafe_allow_html=True)

if soft_skills:
    owned_soft_count = sum(1 for s in soft_skills if s in user_soft)
    with st.expander(f"🤝 Soft Skills ({len(soft_skills)} competențe | Deții: {owned_soft_count})"):
        for skill in soft_skills:
            if skill in user_soft:
                st.markdown(f"<div style='color: #2E7D32; font-weight: 600; padding: 6px 0; border-bottom: 1px solid #F1F3F6;'>✅ {skill}</div>", unsafe_allow_html=True)
            else:
                links = get_learning_links(skill)
                st.markdown(f"<div style='color: #1B2430; padding: 6px 0; border-bottom: 1px solid #F1F3F6; display: flex; justify-content: space-between; align-items: center;'><span>◽ {skill}</span> <span>{links}</span></div>", unsafe_allow_html=True)

st.write("")

# ==========================================
# 4. BUTON DE EXPORT (DESCĂRCARE PDF)
# ==========================================
pdf_bytes = generate_pdf_export(
    job_name, info.get("domain", ""), salary_lo, salary_hi,
    user_hard, user_soft, hard_skills, soft_skills
)

st.download_button(
    label="📥 Descarcă Planul de Carieră (PDF)",
    data=pdf_bytes,
    file_name=f"Roadmap_{job_name.replace(' ', '_')}.pdf",
    mime="application/pdf",
    use_container_width=True,
    type="primary"
)

st.markdown("---")

# Butoane navigare inferioară
b1, b2, _ = st.columns([1, 1, 3])
with b1:
    if st.button("🗂️ Înapoi la Categorii", use_container_width=True):
        st.session_state.selected_category = info.get("domain")
        st.switch_page("pages/2_Categorii.py")
with b2:
    if st.session_state.get("recommendations"):
        if st.button("🎯 Înapoi la Recomandări", use_container_width=True):
            st.switch_page("pages/4_Recomandari.py")