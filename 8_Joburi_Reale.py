"""
pages/8_Joburi_Reale.py
-----------------------
Afișează ofertele de muncă reale din baza de date locală (SQLite)
"""
import streamlit as st
import sqlite3
import os
from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar

bootstrap_page("Joburi Reale", icon="💼")
require_login()
render_nav_sidebar()
render_account_sidebar()

if "selected_job" not in st.session_state or not st.session_state.selected_job:
    st.warning("Te rugăm să selectezi o ocupație din Dashboard sau Categorii mai întâi.")
    if st.button("🏠 Înapoi la Dashboard"):
        st.switch_page("pages/0_Dashboard.py")
    st.stop()

ocupatie = st.session_state.selected_job

st.markdown(
    f'<div class="sj-topbar"><div><p class="sj-eyebrow">Oferte de pe PeViitor.ro</p>'
    f'<h2 class="sj-title">Joburi active pentru: {ocupatie}</h2></div></div>',
    unsafe_allow_html=True
)

if st.button("⬅️ Înapoi la detaliile ocupației"):
    st.switch_page("pages/5_Detalii_Job.py")

st.write("")

termen_cautare = st.text_input("🔍 Ajustează termenul de căutare:", value=ocupatie)

# --- CONECTARE LA DB ȘI CĂUTARE ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'jobs.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    search_pattern = f"%{termen_cautare}%"
    cursor.execute("SELECT title, company, city, link FROM jobs WHERE title LIKE ? LIMIT 50", (search_pattern,))
    rezultate = cursor.fetchall()
    conn.close()

    if rezultate:
        st.success(f"Am găsit {len(rezultate)} oferte active care se potrivesc!")
        cols = st.columns(2)
        for i, (title, company, city, link) in enumerate(rezultate):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"<h4 style='color: #1B2430; margin-bottom: 0.5rem;'>{title}</h4>", unsafe_allow_html=True)
                    st.markdown(f"**🏢 Companie:** {company}<br>**📍 Oraș:** {city}", unsafe_allow_html=True)
                    st.link_button("Aplică acum 🔗", link, use_container_width=True)
    else:
        st.info("Nicio ofertă exactă găsită. Încearcă să folosești un singur cuvânt cheie (ex: 'Inginer', 'Python').")

except Exception as e:
    st.error(f"Eroare conexiune DB: {e}")