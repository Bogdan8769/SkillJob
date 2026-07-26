"""
pages/5_Detalii_Job.py
----------------------
Pagina dedicată pentru o ocupație specifică.
Afișează descrierea detaliată din ESCO și toate competențele necesare.
"""

import streamlit as st

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from database import JOBS

bootstrap_page("Detalii Ocupație", icon="📄")
require_login()
render_nav_sidebar()
render_account_sidebar()

# --- CSS Specific Paginii ---
PAGE_CSS = """
<style>
.sj-roadmap-header {
    background: linear-gradient(120deg, #1B2430, #2F6F5E);
    border-radius: 20px; padding: 2rem 2.2rem; color: #fff;
}
.sj-roadmap-header .sj-eyebrow2 {
    text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.72rem;
    font-weight: 700; color: #C99A56; margin: 0;
}
.sj-tag {
    display: inline-block; padding: 4px 10px; margin: 4px 4px 0 0;
    border-radius: 6px; font-size: 0.85rem; font-weight: 600;
}
.sj-tag.matched { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7; }
.sj-tag.soft { background-color: #FFFDF8; color: #93691E; border: 1px dashed #C99A56; }
</style>
"""
st.markdown(PAGE_CSS, unsafe_allow_html=True)

job_name = st.session_state.get("selected_job")

# Dacă a ajuns pe pagină fără să selecteze un job
if not job_name or job_name not in JOBS:
    st.info("Nu ai selectat nicio ocupație.")
    st.page_link("pages/2_Categorii.py", label="🗂️ Mergi la Explorare Categorii")
    st.stop()

info = JOBS[job_name]

#buton
st.write("")  # O mică spațiere
if st.button("🔎 Caută joburi reale pentru această ocupație", type="primary", use_container_width=True):
    st.switch_page("pages/8_Joburi_Reale.py")

# Buton rapid de întoarcere
if st.button("⬅ Înapoi la Explorare"):
    st.switch_page("pages/2_Categorii.py")

# --- Antetul Paginii (Header) ---
st.markdown(
    f'''<div class="sj-roadmap-header" style="margin-top: 1rem;">
        <div class="sj-eyebrow2">{info.get("domain", "")}</div>
        <h2 style="font-size: 2.2rem; margin-bottom: 0.8rem;">{job_name}</h2>
        <p style="font-size: 1rem; line-height: 1.6; opacity: 0.9;">{info.get("description", "Fără descriere disponibilă.")}</p>
    </div>''', unsafe_allow_html=True)

# --- Secțiunea de Skill-uri ---
st.markdown("### Competențe și abilități necesare (ESCO)")
st.markdown("<p style='color: var(--text-soft); font-size:0.9rem; margin-top:-0.5rem;'>Acestea sunt aptitudinile extrase din standardul european pentru această ocupație.</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Folosim container nativ Streamlit pentru a evita cutiile albe
    with st.container(border=True):
        st.markdown("#### 🛠️ Hard Skills (Tehnice)")
        hard_skills = info.get("hard_skills", [])
        if hard_skills:
            tags_html = "".join([f'<span class="sj-tag matched">{s}</span>' for s in hard_skills[:20]])
            st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
            if len(hard_skills) > 20:
                st.caption(f"• alte {len(hard_skills) - 20} competențe tehnice secundare.")
        else:
            st.write("Nu s-au găsit date tehnice specifice.")

with col2:
    with st.container(border=True):
        st.markdown("#### 🤝 Soft Skills & Trăsături")
        soft_skills = info.get("soft_skills", [])
        if soft_skills:
            tags_html = "".join([f'<span class="sj-tag soft">{s}</span>' for s in soft_skills[:15]])
            st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
        else:
            st.write("Competențele de bază sunt integrate în secțiunea tehnică de către ESCO.")

st.write("")
st.markdown("---")
st.write("")

# --- Call to Action: Roadmap ---
st.markdown(
    "<h3 style='text-align:center;'>Ești pregătit să înveți?</h3>"
    "<p style='text-align:center; color:var(--text-soft); margin-bottom:1.5rem;'>Descoperă traseul vizual pas-cu-pas pentru a ajunge la această meserie.</p>",
    unsafe_allow_html=True
)

_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    if st.button("🗺️ Generează Roadmap-ul Interactiv", type="primary", use_container_width=True):
        st.switch_page("pages/3_Roadmap.py")