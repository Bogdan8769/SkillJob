"""
pages/1_Profil.py
------------------
Wizard-ul de profilare profesional (Arhitectură Drill-Down / Cascadă).
Versiune exclusiv manuală.
"""

import time
import streamlit as st

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from database import DOMAIN_META, JOBS
from components import render_domain_card
from state import wizard_next, wizard_back, reset_wizard
from matching import compute_recommendations

bootstrap_page("Profil", icon="📝")
require_login()
render_nav_sidebar()
render_account_sidebar()

# --- INIȚIALIZARE STARE WIZARD ---
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {}

WIZARD_STEPS = ["Domeniu", "Ramură", "Ocupație", "Competențe", "Preferințe", "Sumar"]

PREMIUM_CSS = """
<style>
.sj-onboard-wrap { max-width: 1000px; margin: 0 auto; }
.sj-progress-track { width: 100%; height: 6px; background: #EDEFF3; border-radius: 999px; overflow: hidden; margin: 0 0 1.8rem 0; }
.sj-progress-fill { height: 100%; background: linear-gradient(90deg, #C99A56, #2F6F5E); border-radius: 999px; transition: width 0.45s ease; }
.sj-progress-caption { font-size: 0.78rem; color: #8A93A3; font-weight: 600; margin: -1.3rem 0 1.6rem 0; text-align: right; }
.sj-topbar { margin-bottom: 1.5rem; }
.sj-eyebrow { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.75rem; font-weight: 700; color: #C99A56; margin: 0; }
.sj-title { font-size: 2rem; font-weight: 800; margin: 0.2rem 0 0.2rem 0; color: #1B2430; }
.sj-subtitle { color: #5B6472; margin: 0; }
.sj-steps { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 2rem; }
.sj-step { display: flex; flex-direction: column; align-items: center; gap: 0.4rem; flex: 0 0 auto; }
.sj-step-circle { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #F1F3F6; color: #8A93A3; font-weight: 700; font-size: 0.85rem; border: 2px solid #E3E7ED; transition: all 0.25s ease; }
.sj-step.active .sj-step-circle { background: #2F6F5E; border-color: #2F6F5E; color: #fff; box-shadow: 0 0 0 4px rgba(47,111,94,0.15); }
.sj-step.done .sj-step-circle { background: #C99A56; border-color: #C99A56; color: #fff; }
.sj-step-label { font-size: 0.72rem; color: #8A93A3; font-weight: 600; white-space: nowrap; }
.sj-step.active .sj-step-label, .sj-step.done .sj-step-label { color: #1B2430; }
.sj-step-line { flex: 1 1 auto; height: 2px; background: #E3E7ED; margin: 17px 6px 0 6px; border-radius: 2px; }
.sj-step-line.done { background: #C99A56; }
.sj-wizard-card { background: #FFFFFF; border: 1px solid #ECEFF3; border-radius: 20px; padding: 2.4rem 2.6rem; box-shadow: 0 10px 30px rgba(16,24,40,0.06); margin-bottom: 1.4rem; }
.sj-wizard-heading { font-size: 1.35rem; font-weight: 700; color: #1B2430; margin: 0 0 0.3rem 0; }
.sj-wizard-sub { color: #5B6472; font-size: 0.92rem; margin: 0 0 1.4rem 0; }
.sj-domain-pill { display: inline-block; background: #F1F3F6; color: #1B2430; font-weight: 700; padding: 0.35rem 0.9rem; border-radius: 999px; font-size: 0.85rem; margin-bottom: 1rem; }
.sj-subcat-tile { border: 2px solid #ECEFF3; border-radius: 14px; padding: 1.2rem 1.3rem; margin-bottom: 0.7rem; transition: all 0.2s ease; background: #fff; }
.sj-subcat-tile.selected { border-color: #C99A56; background: rgba(201,154,86,0.06); }
.sj-subcat-tile h4 { margin: 0 0 0.2rem 0; font-size: 1.05rem; color: #1B2430; }
.sj-subcat-count { font-size: 0.78rem; color: #8A93A3; font-weight: 600; }
.sj-section-label { font-weight: 700; font-size: 0.95rem; color: #1B2430; margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.4rem; }
.sj-summary-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed #ECEFF3; }
.sj-summary-row:last-child { border-bottom: none; }
.sj-summary-label { color: #8A93A3; font-weight: 600; font-size: 0.85rem; }
.sj-summary-value { color: #1B2430; font-weight: 700; font-size: 0.92rem; text-align: right; }
div[data-testid="stSegmentedControl"] label { border-radius: 999px !important; }
.stButton button[kind="primary"] { background: linear-gradient(90deg, #2F6F5E, #24594A); border: none; border-radius: 12px; font-weight: 700; box-shadow: 0 6px 16px rgba(47,111,94,0.25); }
.stButton button[kind="secondary"] { border-radius: 12px; font-weight: 600; }
div[data-testid="stExpander"] { border-radius: 14px !important; }
.stButton button { height: auto !important; min-height: 2.8rem; padding: 0.4rem 0.6rem !important; }
.stButton button p { white-space: normal !important; font-size: 0.85rem !important; line-height: 1.3 !important; }
</style>
"""
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

wd = st.session_state.wizard_data
step = st.session_state.wizard_step

def render_step_indicator(current_step):
    steps_html = '<div class="sj-steps">'
    for i, name in enumerate(WIZARD_STEPS):
        step_num = i + 1
        status_class = "done" if step_num < current_step else ("active" if step_num == current_step else "")
        steps_html += f'<div class="sj-step {status_class}"><div class="sj-step-circle">{step_num}</div><div class="sj-step-label">{name}</div></div>'
        if step_num < len(WIZARD_STEPS):
            line_class = "done" if step_num < current_step else ""
            steps_html += f'<div class="sj-step-line {line_class}"></div>'
    steps_html += '</div>'
    st.markdown(steps_html, unsafe_allow_html=True)

def get_subcategories(domain, jobs_dict):
    rules = {
        "IT & Comunicații": ["software", "date", "rețea", "it", "web", "programator", "dezvoltator", "informatic", "calculator", "sistem"],
        "Sănătate & Medicină": ["medic", "asistent", "terapeut", "farmacist", "sănătate", "clinic", "stomatolog", "psiholog", "infirmier"],
        "Educație & Cercetare": ["profesor", "învățător", "educator", "cercetător", "formator", "academic", "științ"],
        "Inginerie & Tehnic": ["inginer", "tehnician", "mecanic", "electric", "proiectant", "arhitect", "tehnolog"],
        "Finanțe & Legal": ["contabil", "auditor", "financiar", "avocat", "jurist", "legal", "bancar", "economic"],
        "Vânzări & Marketing": ["vânzări", "marketing", "comercial", "agent", "publicitate", "PR"],
        "Management & HR": ["manager", "director", "resurse umane", "recrutare", "proiect", "coordonator", "șef"],
        "Logistică & Transport": ["șofer", "logistic", "transport", "depozit", "curier", "rutier", "marfă"],
        "Construcții & Amenajări": ["constructor", "zidar", "instalator", "șantier", "macaragiu", "zugrav"],
        "Artă, Design & Media": ["designer", "artist", "jurnalist", "redactor", "grafician", "foto", "muzic"],
    }
    subcats = {k: [] for k in rules.keys()}
    subcats["Altele"] = []
    domain_jobs = [j for j, info in jobs_dict.items() if info.get("domain") == domain]
    for job in domain_jobs:
        job_lower = job.lower()
        matched = False
        for subcat, keywords in rules.items():
            if any(kw in job_lower for kw in keywords):
                subcats[subcat].append(job)
                matched = True
                break
        if not matched: subcats["Altele"].append(job)
    return {k: sorted(v) for k, v in subcats.items() if len(v) > 0}

def group_jobs_by_prefix(jobs):
    groups = {}
    keywords = ["inginer", "dezvoltator", "analist", "profesor", "manager", "tehnician", "operator", "specialist", "consultant", "director", "ofițer", "asistent", "mecanic", "medic", "programator", "administrator", "proiectant", "inspector", "lucrător", "agent", "tehnolog", "cercetător", "arhitect", "designer", "șef", "electrician", "software"]
    for job in jobs:
        job_lower = job.lower()
        placed = False
        for kw in keywords:
            if job_lower.startswith(kw) or f" {kw} " in job_lower:
                g_name = kw.capitalize()
                if g_name not in groups: groups[g_name] = []
                groups[g_name].append(job)
                placed = True
                break
        if not placed:
            if "Altele" not in groups: groups["Altele"] = []
            groups["Altele"].append(job)
    sorted_groups = {k: sorted(v) for k, v in sorted(groups.items(), key=lambda item: len(item[1]), reverse=True) if k != "Altele"}
    if "Altele" in groups: sorted_groups["Altele"] = sorted(groups["Altele"])
    return sorted_groups

def render_dual_listbox(state_key, available_items_left, icon, title, cols_count=2):
    if state_key not in wd: wd[state_key] = []
    selected = wd[state_key]
    unselected = [s for s in available_items_left if s not in selected]

    st.markdown(f"#### {icon} {title}")
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            st.markdown(f"<p class='sj-section-label'>➕ Disponibile aici</p>", unsafe_allow_html=True)
            search_query = st.text_input(f"Caută {state_key}", placeholder="🔍 Caută în listă...", label_visibility="collapsed", key=f"search_{state_key}")
            filtered_unselected = [s for s in unselected if search_query.lower() in s.lower()] if search_query else unselected
            st.caption(f"Afișez {len(filtered_unselected)} din {len(unselected)} variante")

            if not filtered_unselected:
                st.info(f"Niciun rezultat găsit." if search_query else "Nu mai sunt opțiuni disponibile în acest grup.")
            else:
                in_cols = st.columns(cols_count)
                for i, item in enumerate(filtered_unselected):
                    with in_cols[i % cols_count]:
                        if st.button(f"{item}", key=f"add_{state_key}_{item}", use_container_width=True):
                            wd[state_key].append(item)
                            st.rerun()

    with col_right:
        with st.container(border=True):
            st.markdown(f"<p class='sj-section-label' style='color: var(--moss);'>✅ Adăugate în profil ({len(selected)})</p>", unsafe_allow_html=True)
            if not selected:
                st.info("Apasă pe opțiunile din stânga pentru a le adăuga.")
            else:
                in_cols = st.columns(cols_count)
                for i, item in enumerate(selected):
                    with in_cols[i % cols_count]:
                        if st.button(f"❌ {item}", key=f"rem_{state_key}_{item}", use_container_width=True):
                            wd[state_key].remove(item)
                            st.rerun()

def segmented(label, options, current, key):
    idx = options.index(current) if current in options else 0
    if hasattr(st, "segmented_control"):
        val = st.segmented_control(label, options, default=options[idx], key=key)
        return val if val is not None else options[idx]
    return st.radio(label, options, index=idx, horizontal=True, key=key)

st.markdown('<div class="sj-onboard-wrap">', unsafe_allow_html=True)
st.markdown('<div class="sj-topbar"><p class="sj-eyebrow">Onboarding Profesional</p><h2 class="sj-title">Hai să-ți construim profilul</h2><p class="sj-subtitle">Urmează pașii de mai jos pentru a-ți personaliza parcursul manual.</p></div>', unsafe_allow_html=True)

progress_pct = int((step - 1) / max(len(WIZARD_STEPS) - 1, 1) * 100)
st.markdown(f'<div class="sj-progress-track"><div class="sj-progress-fill" style="width:{progress_pct}%;"></div></div><p class="sj-progress-caption">Pasul {step} din {len(WIZARD_STEPS)}</p>', unsafe_allow_html=True)

render_step_indicator(step)
st.markdown('<div class="sj-wizard-card">', unsafe_allow_html=True)

if step == 1:
    st.markdown('<p class="sj-wizard-heading">În ce domeniu mare activezi sau vrei să intri?</p><p class="sj-wizard-sub">Alege domeniul ISCO care ți se potrivește cel mai bine.</p>', unsafe_allow_html=True)
    domains = list(DOMAIN_META.items())
    for i in range(0, len(domains), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(domains):
                domain_name, meta = domains[i + j]
                with cols[j]:
                    render_domain_card(domain_name, meta, selected=(wd.get("domain") == domain_name))
                    if st.button("Selectează", key=f"pick_domain_{domain_name}", use_container_width=True, type="secondary"):
                        if wd.get("domain") != domain_name:
                            wd["sub_domain"] = None; wd["target_jobs"] = []; wd["hard_skills"] = []; wd["soft_skills"] = []
                        wd["domain"] = domain_name
                        wizard_next(); st.rerun()

elif step == 2:
    if not wd.get("domain"): wizard_back(); st.rerun()
    meta = DOMAIN_META.get(wd["domain"], {"icon": "🔹"})
    st.markdown(f'<span class="sj-domain-pill">{meta["icon"]} {wd["domain"]}</span><p class="sj-wizard-heading">Alege ramura specifică</p>', unsafe_allow_html=True)
    subcats = get_subcategories(wd["domain"], JOBS)
    sc_keys = list(subcats.keys())
    for i in range(0, len(sc_keys), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(sc_keys):
                sc_name = sc_keys[i + j]
                count = len(subcats[sc_name])
                with cols[j]:
                    is_selected = (wd.get("sub_domain") == sc_name)
                    sel_cls = "selected" if is_selected else ""
                    st.markdown(f'<div class="sj-subcat-tile {sel_cls}"><h4>{sc_name}</h4><span class="sj-subcat-count">{count} ocupații disponibile</span></div>', unsafe_allow_html=True)
                    if st.button(f"Explorează {sc_name}", key=f"sc_{sc_name}", use_container_width=True, type="secondary"):
                        if wd.get("sub_domain") != sc_name:
                            wd["target_jobs"] = []; wd["hard_skills"] = []; wd["soft_skills"] = []; wd["selected_job_group"] = None
                        wd["sub_domain"] = sc_name
                        wizard_next(); st.rerun()

elif step == 3:
    if not wd.get("sub_domain"): wizard_back(); st.rerun()
    st.markdown(f'<span class="sj-domain-pill">📁 {wd["sub_domain"]}</span><p class="sj-wizard-heading">Ce meserie te interesează direct?</p>', unsafe_allow_html=True)
    subcats = get_subcategories(wd["domain"], JOBS)
    available_jobs = subcats.get(wd["sub_domain"], [])
    job_groups = group_jobs_by_prefix(available_jobs)

    if not wd.get("selected_job_group"):
        group_keys = list(job_groups.keys())
        for i in range(0, len(group_keys), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(group_keys):
                    g_name = group_keys[i + j]
                    count = len(job_groups[g_name])
                    with cols[j]:
                        st.markdown(f'<div class="sj-subcat-tile"><h4>{g_name}</h4><span class="sj-subcat-count">{count} variante disponibile</span></div>', unsafe_allow_html=True)
                        if st.button(f"Vezi {g_name}", key=f"g_{g_name}", use_container_width=True, type="secondary"):
                            wd["selected_job_group"] = g_name
                            st.rerun()
    else:
        g_name = wd["selected_job_group"]
        st.markdown(f'<p class="sj-wizard-sub">Ai ales familia <b>{g_name}</b>. Selectează rolurile dorite:</p>', unsafe_allow_html=True)
        if st.button("⬅️ Înapoi la familiile de ocupații"):
            wd["selected_job_group"] = None
            st.rerun()
        st.write("")
        render_dual_listbox("target_jobs", job_groups[g_name], "🎯", f"Variante pentru {g_name}", cols_count=1)

elif step == 4:
    if not wd.get("target_jobs"):
        st.warning("Te rugăm să alegi o ocupație la pasul anterior.")
        wizard_back(); st.rerun()
    st.markdown('<p class="sj-wizard-heading">Expertiza ta</p>', unsafe_allow_html=True)
    targeted_hard = set(); targeted_soft = set()
    for job_name in wd["target_jobs"]:
        targeted_hard.update(JOBS[job_name].get("hard_skills", []))
        targeted_soft.update(JOBS[job_name].get("soft_skills", []))
    render_dual_listbox("hard_skills", sorted(list(targeted_hard)), "🛠️", "Competențe Tehnice", cols_count=2)
    st.write(""); st.markdown("---"); st.write("")
    render_dual_listbox("soft_skills", sorted(list(targeted_soft)), "🤝", "Soft Skills", cols_count=2)

elif step == 5:
    st.markdown('<p class="sj-wizard-heading">Cum preferi să lucrezi?</p>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="sj-section-label">🎓 Experiență & Educație</p>', unsafe_allow_html=True)
        wd["education"] = segmented("Ultima diplomă / Stadiu actual:", ["Fără studii", "Student (în curs)", "Licență", "Master / Doctorat"], wd.get("education", "Student (în curs)"), key="seg_edu")
        st.write("")
        wd["experience_years"] = segmented("Nivelul de experiență:", ["Entry-level (0-2 ani)", "Mid-level (3-5 ani)", "Senior (5+ ani)"], wd.get("experience_years", "Entry-level (0-2 ani)"), key="seg_exp")
    st.write("")
    with st.container(border=True):
        st.markdown('<p class="sj-section-label">💼 Angajamentul dorit</p>', unsafe_allow_html=True)
        wd["contract_type"] = segmented("Tipul de contract:", ["Full-time", "Part-time", "Proiect", "Internship"], wd.get("contract_type", "Full-time"), key="seg_contract")
        st.write("")
        wd["work_mode"] = segmented("Modul de lucru:", ["Remote", "Hibrid", "La birou", "Pe teren"], wd.get("work_mode", "Remote"), key="seg_workmode")

elif step == 6:
    st.markdown('<p class="sj-wizard-heading">Totul este pregătit!</p>', unsafe_allow_html=True)
    with st.container(border=True):
        rows = [
            ("Domeniu", f'{wd.get("domain")} ➜ {wd.get("sub_domain")}'),
            ("Ocupații vizate", ", ".join(wd.get("target_jobs", [])) or "—"),
            ("Competențe tehnice", f'{len(wd.get("hard_skills", []))} bifate'),
            ("Soft skills", f'{len(wd.get("soft_skills", []))} bifate'),
            ("Experiență", wd.get("experience_years", "—")),
            ("Educație", wd.get("education", "—")),
            ("Contract", wd.get("contract_type", "—")),
            ("Mod de lucru", wd.get("work_mode", "—")),
        ]
        rows_html = "".join(f'<div class="sj-summary-row"><span class="sj-summary-label">{label}</span><span class="sj-summary-value">{value}</span></div>' for label, value in rows)
        st.markdown(rows_html, unsafe_allow_html=True)

    st.write("")
    if st.button("🚀 Calculează Potrivirile ESCO", use_container_width=True, type="primary"):
        with st.spinner("Generăm recomandările pe baza standardului european..."):
            time.sleep(1)
            st.session_state.recommendations = compute_recommendations(wd, top_n=3)
        st.switch_page("pages/4_Recomandari.py")

st.markdown('</div>', unsafe_allow_html=True)

nav_l, nav_c, nav_r = st.columns([1, 2, 1])
with nav_l:
    if step > 1:
        if st.button("⬅ Înapoi", use_container_width=True, type="secondary"):
            wizard_back(); st.rerun()
with nav_r:
    if step > 2 and step < len(WIZARD_STEPS):
        if st.button("Continuă ➜", use_container_width=True, type="primary"):

            # --- FIX: Sincronizăm forțat datele la Pasul 5 înainte să mergem mai departe ---
            if step == 5:
                wd["education"] = st.session_state.get("seg_edu", wd.get("education"))
                wd["experience_years"] = st.session_state.get("seg_exp", wd.get("experience_years"))
                wd["contract_type"] = st.session_state.get("seg_contract", wd.get("contract_type"))
                wd["work_mode"] = st.session_state.get("seg_workmode", wd.get("work_mode"))
            # -------------------------------------------------------------------------------

            wizard_next()
            st.rerun()

if step > 1:
    st.write("")
    if st.button("🔁 Resetează Profilul", use_container_width=False, type="secondary"):
        reset_wizard(); st.rerun()

st.markdown('</div>', unsafe_allow_html=True)