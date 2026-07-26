"""
pages/4_Recomandari.py
------------------------
Afișează recomandările generate de motorul de matching (matching.py) după
completarea profilului. Fiecare recomandare are propriul procent de
potrivire, skill-urile comune și acces direct la roadmap.
"""

import streamlit as st

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from components import render_recommendation_card
from state import reset_wizard
from matching import compute_recommendations  # <-- IMPORT NOU pentru recuperarea automată

bootstrap_page("Recomandări", icon="🎯")
require_login()
render_nav_sidebar()
render_account_sidebar()

st.markdown(
    '<div class="sj-topbar"><div><p class="sj-eyebrow">Rezultate</p>'
    '<h2 class="sj-title">Recomandările tale</h2>'
    '<p class="sj-subtitle">Pe baza profilului tău, acestea sunt ocupațiile cele mai potrivite.</p></div></div>',
    unsafe_allow_html=True)

recommendations = st.session_state.get("recommendations")
wd = st.session_state.get("wizard_data", {})

# --- RECUPERARE AUTOMATĂ ---
# Dacă recomandările lipsesc, dar avem hard_skills salvate în sesiune, le calculăm pe loc!
if not recommendations and wd.get("hard_skills"):
    recommendations = compute_recommendations(wd, top_n=3)
    st.session_state.recommendations = recommendations

# Dacă tot nu există nicio dată, trimitem utilizatorul spre profilare
if not recommendations:
    st.info("Nu ai completat încă profilul pentru a primi recomandări.")
    st.write("")
    st.page_link("pages/1_Profil.py", label="📝 Mergi la completarea profilului")
    st.stop()

# Afișarea dinamică a cardurilor de recomandare
for i, rec in enumerate(recommendations):
    render_recommendation_card(rec)

    # Aliniem butonul de Roadmap în partea dreaptă-jos a cardului pentru un UX mai bun
    col1, col2 = st.columns([2, 1])
    with col2:
        # type="primary" pentru vizibilitate maximă și contrast bun
        if st.button(f"🗺️ Vezi Roadmap", key=f"rec_rm_{rec.get('job', i)}", use_container_width=True, type="primary"):
            st.session_state.selected_job = rec.get("job")
            st.switch_page("pages/3_Roadmap.py")

    st.write("") # Spațiu suplimentar între recomandări

st.markdown("---")

if st.button("🔁 Refă profilul de la zero", use_container_width=False):
    # Trimiterea către pasul 1 pentru a începe iar, curățând memoria în avans
    reset_wizard()
    st.switch_page("pages/1_Profil.py")