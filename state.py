"""
state.py
--------
Centralizează toată gestiunea `st.session_state`, pentru a păstra codul curat
și a evita împrăștierea variabilelor globale prin fiecare pagină. Orice pagină nouă
adăugată în viitor va folosi aceste helper-e.
"""

import streamlit as st

WIZARD_STEPS = ["Domeniu", "Sub-categorie", "Ocupație", "Competențe", "Preferințe", "Sumar"]

# Am extras structura de date standard pentru a nu o duplica în cod
DEFAULT_WIZARD_DATA = {
    "domain": None,
    "hard_skills": [],
    "soft_skills": [],
    "experience_years": 0,
    "education": None,
    "work_mode": None,
    "contract_type": None,
    "salary_expectation": 5000,
    "team_size": None,
    "travel_willingness": None,
    "preferred_domains": [],
}

def init_session_state():
    """Inițializează variabilele de sesiune dacă nu există deja."""
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user_name", "")
    st.session_state.setdefault("page", "dashboard")

    # Variabile pentru navigare și selecții curente
    st.session_state.setdefault("selected_category", None)
    st.session_state.setdefault("selected_job", None)
    st.session_state.setdefault("recommendations", None)

    # Starea completă a wizard-ului de profilare — persistă între rerun-uri
    st.session_state.setdefault("wizard_step", 1)
    st.session_state.setdefault("wizard_data", DEFAULT_WIZARD_DATA.copy())

def go(page: str, **kwargs):
    """Actualizează variabile de stare și forțează o reîncărcare. Util pentru fluxuri complexe."""
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

def reset_wizard():
    """Resetează formularul de profilare la starea inițială (curată)."""
    st.session_state.wizard_step = 1
    # .copy() asigură că o luăm de la zero cu un obiect complet nou în memorie
    st.session_state.wizard_data = DEFAULT_WIZARD_DATA.copy()

def wizard_next():
    """Trece la pasul următor din formularul de profilare."""
    st.session_state.wizard_step = min(st.session_state.wizard_step + 1, len(WIZARD_STEPS))

def wizard_back():
    """Se întoarce la pasul anterior din formularul de profilare."""
    st.session_state.wizard_step = max(st.session_state.wizard_step - 1, 1)

def logout():
    """Deconectează utilizatorul și curăță datele sensibile din sesiune."""
    st.session_state.update(
        logged_in=False,
        user_name="",
        page="dashboard",
        recommendations=None,
        selected_category=None,
        selected_job=None,
    )
    reset_wizard()