"""
layout.py
---------
Modul de infrastructură pentru centralizarea UI-ului recurent
(setări pagină, meniu lateral, verificare autentificare) în aplicația multi-page.
"""

import streamlit as st
from styles import CUSTOM_CSS, EXTRA_CSS
from state import init_session_state, logout


def bootstrap_page(title: str, icon: str = "🧭"):
    """Se apelează ca prim lucru în fiecare pagină."""
    st.set_page_config(
        page_title=f"SkillJob · {title}",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    init_session_state()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(EXTRA_CSS, unsafe_allow_html=True)


def require_login():
    """Blochează accesul la o pagină dacă utilizatorul nu e autentificat."""
    if not st.session_state.get("logged_in", False):
        st.warning("🔒 Trebuie să te autentifici pentru a accesa această pagină.")
        # Am înlocuit st.page_link cu un buton care face rerun,
        # lăsând app.py să preia automat afișarea ecranului de login.
        if st.button("⬅ Mergi la pagina de autentificare"):
            st.rerun()
        st.stop()


def render_nav_sidebar():
    """Meniul lateral de navigare principal."""
    with st.sidebar:
        st.title("🧭 SkillJob")
        st.markdown("---")

        # FIX: Am actualizat destinația către noul fișier creat
        st.page_link("pages/0_Dashboard.py", label="Dashboard", icon="🏠")
        st.page_link("pages/2_Categorii.py", label="Categorii", icon="🗂️")
        st.page_link("pages/1_Profil.py", label="Mini-CV / Profilare", icon="📝")
        st.page_link("pages/6_Scanner_CV.py", label="Scanner CV (AI)", icon="🤖")

        if st.session_state.get("recommendations"):
            st.page_link("pages/4_Recomandari.py", label="Recomandările mele", icon="🎯")
        if st.session_state.get("selected_job"):
            st.page_link("pages/3_Roadmap.py", label="Roadmap curent", icon="🗺️")


def render_account_sidebar():
    """Randează badge-ul de utilizator în panoul lateral."""
    with st.sidebar:
        st.write("")
        st.markdown(
            f'''<div class="sj-badge">
                <div class="sj-badge-avatar">{(st.session_state.user_name[0]).upper() if st.session_state.user_name else "U"}</div>
                <div>
                    <div class="sj-badge-name">{st.session_state.user_name or "Utilizator"}</div>
                    <div class="sj-badge-role">Candidat</div>
                </div>
            </div>''',
            unsafe_allow_html=True
        )

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()