"""
pages/2_Categorii.py
---------------------
Explorare pe categorii/domenii cu sistem de paginare și căutare globală live.
Prevenim blocarea interfeței când avem mii de ocupații prin grupare inteligentă.
"""

import math
import streamlit as st

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from components import render_category_card
from database import DOMAIN_META, JOBS

bootstrap_page("Categorii", icon="🗂️")
require_login()
render_nav_sidebar()
render_account_sidebar()

# --- Inițializare variabile de stare pentru navigare ---
if "cat_active_domain" not in st.session_state:
    st.session_state.cat_active_domain = None
if "cat_search" not in st.session_state:
    st.session_state.cat_search = ""
if "cat_page" not in st.session_state:
    st.session_state.cat_page = 1

def reset_and_set_domain(domain_name):
    st.session_state.cat_active_domain = domain_name
    st.session_state.cat_search = ""
    st.session_state.cat_page = 1

def reset_category_view():
    st.session_state.cat_active_domain = None
    st.session_state.cat_search = ""
    st.session_state.cat_page = 1

# =====================================================================
# VEDEREA 1: CĂUTARE GLOBALĂ SAU LISTA CELOR 10 DOMENII MARI (ISCO)
# =====================================================================
if not st.session_state.cat_active_domain:
    st.markdown(
        '<div class="sj-topbar"><div><p class="sj-eyebrow">Explorare & Căutare</p>'
        '<h2 class="sj-title">Găsește-ți vocația</h2>'
        '<p class="sj-subtitle">Caută direct o meserie sau alege un domeniu pentru a explora.</p></div></div>',
        unsafe_allow_html=True)

    # NOU: Bară de căutare GLOBALĂ
    global_search = st.text_input(
        "Caută ocupație global",
        value="",
        placeholder="🔍 Ex: inginer, medic, manager...",
        label_visibility="collapsed"
    )
    st.write("")

    # Dacă utilizatorul a tastat ceva, afișăm rezultatele GRUPATE (Sistemul Premium)
    if global_search.strip():
        search_results = [j for j in JOBS.keys() if global_search.lower() in j.lower()]

        if not search_results:
            st.warning(f"Nu am găsit nicio meserie care să conțină '{global_search}'. Încearcă alte cuvinte cheie.")
        else:
            # 1. Grupăm rezultatele după domeniu
            grouped_results = {}
            for job in search_results:
                domain = JOBS[job].get("domain", "Altele")
                if domain not in grouped_results:
                    grouped_results[domain] = []
                grouped_results[domain].append(job)

            st.markdown(f"<p class='sj-wizard-sub'>Am găsit <b>{len(search_results)}</b> rezultate. Le-am grupat pe domenii pentru tine:</p>", unsafe_allow_html=True)
            st.write("")

            # 2. Afișăm grid-ul de carduri pe 2 coloane
            for domain, jobs in grouped_results.items():
                st.markdown(f"#### 📁 {domain} <span style='color: #8A93A3; font-size: 1rem;'>({len(jobs)} rezultate)</span>", unsafe_allow_html=True)

                cols = st.columns(2)
                for i, job in enumerate(jobs):
                    with cols[i % 2]:
                        with st.container(border=True):
                            # Forțăm înălțimea pentru a păstra alinierea butoanelor indiferent de lungimea textului
                            st.markdown(
                                f"<div style='font-weight: 600; font-size: 0.95rem; color: #1B2430; margin-bottom: 12px; min-height: 2.8rem;'>{job}</div>",
                                unsafe_allow_html=True
                            )
                            # Păstrăm legătura cu pagina ta de detalii
                            if st.button("📄 Vezi Detalii", key=f"btn_glob_{job}", use_container_width=True):
                                st.session_state.selected_job = job
                                st.switch_page("pages/5_Detalii_Job.py")

                st.write("")
                st.markdown("---")

    # Dacă NU a tastat nimic, afișăm cele 10 domenii clasice
    else:
        cols = st.columns(2)
        for i, (domain_name, meta) in enumerate(DOMAIN_META.items()):
            job_count = len([j for j, info in JOBS.items() if info.get("domain") == domain_name])

            with cols[i % 2]:
                render_category_card(domain_name, meta, job_count)
                if st.button(f"Explorează {domain_name}", key=f"cat_select_{domain_name}", use_container_width=True):
                    reset_and_set_domain(domain_name)
                    st.rerun()

# =====================================================================
# VEDEREA 2: JOBURILE DIN DOMENIUL SELECTAT (CU PAGINARE)
# =====================================================================
else:
    active_domain = st.session_state.cat_active_domain
    meta = DOMAIN_META.get(active_domain, {"icon": "🔹", "description": ""})

    if st.button("⬅ Înapoi la toate categoriile"):
        reset_category_view()
        st.rerun()

    st.markdown(
        f'<div class="sj-topbar" style="margin-top: 1rem;"><div>'
        f'<p class="sj-eyebrow">{meta["description"]}</p>'
        f'<h2 class="sj-title">{meta["icon"]} Ocupații: {active_domain}</h2>'
        f'</div></div>',
        unsafe_allow_html=True)

    # Bara de căutare LOCALĂ (doar în domeniul selectat)
    st.markdown('<div class="sj-search">', unsafe_allow_html=True)
    search_query = st.text_input("Caută ocupație", value=st.session_state.cat_search,
                                 placeholder="Filtrează ocupațiile din acest domeniu...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if search_query != st.session_state.cat_search:
        st.session_state.cat_search = search_query
        st.session_state.cat_page = 1
        st.rerun()

    domain_jobs = {j: info for j, info in JOBS.items() if info.get("domain") == active_domain}
    if search_query:
        filtered_jobs = [(j, info) for j, info in domain_jobs.items() if search_query.lower() in j.lower()]
    else:
        filtered_jobs = list(domain_jobs.items())

    # Sistemul de Paginare (Fixat indexarea)
    ITEMS_PER_PAGE = 12
    total_items = len(filtered_jobs)
    total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

    if st.session_state.cat_page > total_pages:
        st.session_state.cat_page = total_pages
    elif st.session_state.cat_page < 1:
        st.session_state.cat_page = 1

    current_page = st.session_state.cat_page
    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    jobs_to_display = filtered_jobs[start_idx:end_idx]

    st.write("")

    if not jobs_to_display:
        st.info(f"Nu s-a găsit nicio ocupație care să conțină '{search_query}'.")
    else:
        for i in range(0, len(jobs_to_display), 2):
            row_cols = st.columns(2)
            for j, col in enumerate(row_cols):
                if i + j < len(jobs_to_display):
                    job_name, info = jobs_to_display[i + j]
                    with col:
                        st.markdown(
                            f'<div class="sj-card" style="margin-bottom:1rem; padding:1.2rem;">'
                            f'<h4 style="margin:0 0 0.4rem 0; font-size:1.05rem;">{job_name}</h4>'
                            f'<p style="font-size:0.8rem; color:var(--text-soft); line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">'
                            f'{info.get("description", "Nu există descriere disponibilă.")}</p>'
                            f'</div>',
                            unsafe_allow_html=True)

                        if st.button("📄 Vezi Detalii", key=f"det_{job_name}", use_container_width=True):
                            st.session_state.selected_job = job_name
                            st.switch_page("pages/5_Detalii_Job.py")

    if total_pages > 1:
        st.markdown("---")
        pc1, pc2, pc3 = st.columns([1, 2, 1])
        with pc1:
            if current_page > 1:
                if st.button("⬅ Înapoi", use_container_width=True):
                    st.session_state.cat_page -= 1
                    st.rerun()
        with pc2:
            st.markdown(f"<div style='text-align:center; padding-top:0.5rem; color:var(--text-soft);'>Pagina <b>{current_page}</b> din <b>{total_pages}</b> <br><small>({total_items} rezultate)</small></div>", unsafe_allow_html=True)
        with pc3:
            if current_page < total_pages:
                if st.button("Înainte ➡", use_container_width=True):
                    st.session_state.cat_page += 1
                    st.rerun()