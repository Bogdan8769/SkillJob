"""
pages/0_Dashboard.py
--------------------
Dashboard-ul principal al aplicației.
"""
import streamlit as st
from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from database import DOMAIN_META, JOBS, HARD_SKILLS_BY_DOMAIN
from components import render_category_card

bootstrap_page("Dashboard", icon="🏠")
require_login()
render_nav_sidebar()
render_account_sidebar()

def get_smart_category(job_title):
    job_lower = job_title.lower()
    categories = {
        "💻 IT & Software": ["software", "date", "rețea", "sistem", "aplicați", "web", "cloud", "securitate", "it", "informatic", "programator", "dezvoltator", "inteligență"],
        "🏗️ Construcții & Arhitectură": ["construcți", "civil", "arhitect", "structur", "șantier", "clădiri", "topograf", "urbanism", "demolări", "hidrotehnic", "drumuri", "poduri"],
        "⚙️ Mecanică & Industrial": ["mecanic", "industrial", "producție", "fabric", "mașini", "echipamente", "sudură", "metal", "ansambl", "mentenanț", "componente", "materiale"],
        "⚡ Electric & Energie": ["electric", "energi", "electro", "iluminat", "baterii", "regenerabil", "termic", "nuclear"],
        "📡 Telecomunicații & Electronică": ["electronic", "telecomunicați", "comunicați", "semnal", "radio", "audio", "video", "rețele"],
        "⚕️ Sănătate & Biomedicină": ["medic", "clinic", "sănătate", "asistent", "terapeut", "farmac", "stomatolog", "biomedical", "aparate medicale"],
        "🚚 Transport & Auto": ["transport", "auto", "aeronautic", "aerospațial", "naval", "feroviar", "logistic", "vehicul", "rutier"],
        "📊 Management & Finanțe": ["manager", "director", "proiect", "afaceri", "vânzări", "marketing", "consultant", "hr", "resurse", "finanț", "contabil", "audit", "calitate", "fiabilitate"],
        "🔬 Științe & Cercetare": ["cercet", "științ", "laborator", "geolog", "biolog", "chim", "fizic", "matematic", "mediu", "ecolog", "carier", "agricol"]
    }
    for cat, keywords in categories.items():
        if any(kw in job_lower for kw in keywords):
            return cat
    return "📁 Alte Specializări"

# Inițializăm variabilele de sesiune pentru drill-down-ul din căutare
if "dash_search_group" not in st.session_state:
    st.session_state.dash_search_group = None
if "last_search_query" not in st.session_state:
    st.session_state.last_search_query = ""

fname = st.session_state.user_name.split()[0] if st.session_state.user_name else ""
st.markdown(
    f'<div class="sj-topbar"><div><p class="sj-eyebrow">Dashboard</p>'
    f'<h2 class="sj-title">Salut, {fname} 👋</h2>'
    f'<p class="sj-subtitle">Iată o privire de ansamblu asupra platformei SkillJob.</p></div></div>',
    unsafe_allow_html=True)

_, col2, _ = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="sj-search">', unsafe_allow_html=True)
    search_query = st.text_input("Search", placeholder="Caută ocupatii (ex: inginer, constructii)...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if search_query != st.session_state.last_search_query:
    st.session_state.dash_search_group = None
    st.session_state.last_search_query = search_query

st.write("")

if search_query:
    matches = [j for j in JOBS if search_query.lower() in j.lower()]
    if matches:
        if not st.session_state.dash_search_group:
            st.markdown(f'<p class="sj-section-title">Am găsit {len(matches)} rezultate. Alege specializarea:</p>', unsafe_allow_html=True)

            grouped_results = {}
            for job in matches:
                cat = get_smart_category(job)
                if cat not in grouped_results:
                    grouped_results[cat] = []
                grouped_results[cat].append(job)

            sorted_groups = sorted(grouped_results.items(), key=lambda x: len(x[1]), reverse=True)

            cols = st.columns(2)
            for i, (cat_name, cat_jobs) in enumerate(sorted_groups):
                with cols[i % 2]:
                    if st.button(f"{cat_name}\n({len(cat_jobs)} variante)", key=f"grp_{cat_name}", use_container_width=True):
                        st.session_state.dash_search_group = cat_name
                        st.rerun()

        else:
            active_grp = st.session_state.dash_search_group
            st.markdown(f'<p class="sj-section-title">{active_grp}</p>', unsafe_allow_html=True)

            if st.button("⬅️ Înapoi la specializări", type="secondary"):
                st.session_state.dash_search_group = None
                st.rerun()

            st.write("")

            grp_jobs = [j for j in matches if get_smart_category(j) == active_grp]

            cols = st.columns(2)
            for i, job in enumerate(grp_jobs):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(
                            f"<div style='font-weight: 600; font-size: 0.95rem; color: #1B2430; margin-bottom: 12px; min-height: 2.8rem;'>{job}</div>",
                            unsafe_allow_html=True
                        )
                        if st.button("🗺️ Vezi Roadmap", key=f"search_rm_{job}", use_container_width=True):
                            st.session_state.selected_job = job
                            st.switch_page("pages/3_Roadmap.py")

    else:
        st.info(f"Niciun rezultat pentru: **{search_query}**")

else:
    total_hard_skills = sum(len(v) for v in HARD_SKILLS_BY_DOMAIN.values())
    stats = [
        ("💼", str(len(JOBS)), "Ocupații listate"),
        ("🎯", str(total_hard_skills), "Hard skills catalogate"),
        ("📌", "27", "Job-uri active azi"),
    ]

    for col, (icon, num, lbl) in zip(st.columns(3), stats):
        col.markdown(
            f'<div class="sj-stat"><div class="sj-stat-icon">{icon}</div>'
            f'<div><div class="sj-stat-number">{num}</div><div class="sj-stat-label">{lbl}</div></div></div>',
            unsafe_allow_html=True)

    st.write("")
    st.markdown('<p class="sj-section-title">Categorii populare</p>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (domain_name, meta) in enumerate(DOMAIN_META.items()):
        job_count = len([j for j, info in JOBS.items() if info["domain"] == domain_name])
        with cols[i % 2]:
            render_category_card(domain_name, meta, job_count)
            if st.button(f"Explorează {domain_name}", key=f"dash_cat_{domain_name}", use_container_width=True):
                st.session_state.selected_category = domain_name
                st.switch_page("pages/2_Categorii.py")

    st.markdown('<p class="sj-section-title">Nu știi de unde să începi?</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sj-card" style="margin-bottom: 1rem;"><p style="margin:0; color:var(--text-soft);">'
        'Completează profilul tău (Mini-CV) în câțiva pași și primești recomandări de ocupații '
        'potrivite abilităților și personalității tale.</p></div>',
        unsafe_allow_html=True)

    if st.button("📝 Completează profilul acum", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Profil.py")