"""
pages/7_CV_Builder.py
----------------------
CV Builder premium, tip SaaS (inspirat de LiveCareer), integrat în SkillJob.

Arhitectură:
  - Wizard cu 11 pași, navigare printr-o bară de progres ORIZONTALĂ (nu meniu
    lateral de pași — sidebar-ul rămâne cel standard SkillJob, din layout.py).
  - Pașii de completare (Antet, Experiență, Educație, Competențe, Profil,
    Limbi, Realizări) sunt randați split-screen: formular în stânga,
    previzualizare A4 live în dreapta (col_form, col_preview = st.columns([1, 1.2])).
  - Toate datele sunt centralizate în st.session_state.cv_data.
  - Legarea inputurilor de stare se face prin callback-uri on_change, nu prin
    citire directă a valorii widget-ului — asta ține sursa de adevăr mereu în
    cv_data, indiferent din ce pas se randează previzualizarea.
  - Integrarea AI (Groq) și salvarea finală sunt funcții MOCK, clar marcate,
    gata de înlocuit cu logica reală de backend.
"""

import html
import streamlit as st

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
import time
from matching import compute_recommendations
from database import DOMAIN_META, JOBS

bootstrap_page("CV Builder", icon="🧩")
require_login()
render_nav_sidebar()
render_account_sidebar()

# ============================================================================
# 1. DEFINIREA PAȘILOR WIZARD-ULUI
# ============================================================================
# `show` decide dacă pasul e activ în wizard-ul curent (pentru pașii condiționați
# de checkbox-urile din "Secțiuni suplimentare").
STEPS = [
    {"key": "model", "label": "Model", "show": lambda d: True},
    {"key": "metoda", "label": "Metodă", "show": lambda d: True},
    {"key": "antet", "label": "Antet", "show": lambda d: True},
    {"key": "experienta", "label": "Experiență", "show": lambda d: True},
    {"key": "educatie", "label": "Educație", "show": lambda d: True},
    {"key": "competente", "label": "Competențe", "show": lambda d: True},
    {"key": "profil", "label": "Profil", "show": lambda d: True},
    {"key": "sectiuni", "label": "Secțiuni", "show": lambda d: True},
    {"key": "limbi", "label": "Limbi", "show": lambda d: d["sectiuni_extra"]["limbi"]},
    {"key": "realizari", "label": "Realizări", "show": lambda d: d["sectiuni_extra"]["realizari"]},
    {"key": "finalizare", "label": "Finalizare", "show": lambda d: True},
]

# Pași randați split-screen (formular + preview). Restul (model, metoda,
# finalizare) sunt randați pe toată lățimea, pentru că sunt ecrane de alegere
# / rezumat, nu formulare de date.
SPLIT_SCREEN_STEPS = {"antet", "experienta", "educatie", "competente", "profil", "sectiuni", "limbi", "realizari"}


# ============================================================================
# 2. STARE INIȚIALĂ
# ============================================================================
def _default_cv_data() -> dict:
    return {
        "model": "classic",
        "metoda": None,
        "antet": {
            "prenume": "", "nume": "", "adresa": "",
            "telefon": "", "email": "",
        },
        "experienta": [
            {
                "post": "", "angajator": "", "oras": "",
                "data_inceput": "", "data_sfarsit": "", "descriere": "",
            }
        ],
        "educatie": [
            {
                "institutie": "", "calificare": "", "domeniu": "", "perioada": "",
            }
        ],
        "competente": {"hard": "", "soft": ""},
        "profil": "",
        "sectiuni_extra": {"limbi": False, "realizari": False, "certificari": False},
        "limbi": [{"limba": "", "nivel": "Începător"}],
        "realizari": "",
    }


if "cv_data" not in st.session_state:
    st.session_state.cv_data = _default_cv_data()
if "cvb_step_idx" not in st.session_state:
    st.session_state.cvb_step_idx = 0  # index în lista de pași ACTIVI (filtrați)

cv_data = st.session_state.cv_data


def _active_steps() -> list:
    """Lista de pași vizibili în wizard-ul curent, ținând cont de checkbox-urile
    din pasul 'Secțiuni suplimentare'."""
    return [s for s in STEPS if s["show"](cv_data)]


def _clamp_step_index():
    active = _active_steps()
    st.session_state.cvb_step_idx = max(0, min(st.session_state.cvb_step_idx, len(active) - 1))


def go_next():
    _clamp_step_index()
    active = _active_steps()
    if st.session_state.cvb_step_idx < len(active) - 1:
        st.session_state.cvb_step_idx += 1


def go_prev():
    _clamp_step_index()
    if st.session_state.cvb_step_idx > 0:
        st.session_state.cvb_step_idx -= 1


def go_to_key(step_key: str):
    active = _active_steps()
    for i, s in enumerate(active):
        if s["key"] == step_key:
            st.session_state.cvb_step_idx = i
            return


# ============================================================================
# 3. HELPER DE LEGARE STARE <-> WIDGET (callback-uri on_change)
# ============================================================================
def _esc(value: str) -> str:
    """Escapare HTML minimă pentru orice text introdus de utilizator, înainte
    de a fi injectat în previzualizarea randată cu unsafe_allow_html=True."""
    return html.escape(value or "")


def bind(section: str, field: str, widget_key: str):
    """Returnează un callback on_change care copiază valoarea widget-ului
    (identificat prin `widget_key`) înapoi în cv_data[section][field].
    Astfel cv_data rămâne mereu sursa unică de adevăr, indiferent ce widget
    Streamlit a declanșat rerun-ul."""

    def _cb():
        st.session_state.cv_data[section][field] = st.session_state[widget_key]

    return _cb


def bind_flat(field: str, widget_key: str):
    """La fel ca `bind`, dar pentru chei de nivel 1 din cv_data (ex: 'profil')."""

    def _cb():
        st.session_state.cv_data[field] = st.session_state[widget_key]

    return _cb


def bind_list_item(section: str, index: int, field: str, widget_key: str):
    """Legare pentru elemente dintr-o listă (ex: cv_data['limbi'][i]['limba'])."""

    def _cb():
        st.session_state.cv_data[section][index][field] = st.session_state[widget_key]

    return _cb


# ============================================================================
# 4. FUNCȚII MOCK — DE ÎNLOCUIT CU BACKEND-UL REAL
# ============================================================================
def mock_ai_extract_cv_data(uploaded_file) -> dict:
    """
    PLACEHOLDER — aici se va conecta scanarea reală cu Groq Vision
    (vezi pages/6_Scanner_CV.py pentru un exemplu funcțional de apel Groq).

    Intrare: un obiect UploadedFile din st.file_uploader.
    Ieșire așteptată: dict compatibil cu structura cv_data, ex:
        {
            "antet": {"prenume": "...", "nume": "...", ...},
            "experienta": {...},
            "educatie": {...},
            "competente": {"hard": "...", "soft": "..."},
            "profil": "...",
        }

    Implementarea de mai jos NU apelează niciun API — doar simulează o
    extragere reușită, ca să poți testa fluxul UI de capăt la capăt.
    """
    return {
        "antet": {
            "prenume": "Andreea", "nume": "Ionescu",
            "adresa": "", "telefon": "", "email": "",
        },
        "profil": "Profil generat automat (mock) — înlocuiește cu output-ul real al AI-ului.",
        "competente": {"hard": "Excel, Analiză date", "soft": "Comunicare, Lucru în echipă"},
    }


def _finalize_and_go(cv_data: dict):
    """
    Salvează datele CV-ului, rulează algoritmul de matching și
    redirecționează utilizatorul spre recomandări.
    """
    if "wizard_data" not in st.session_state:
        st.session_state.wizard_data = {}

    st.session_state.wizard_data["nume"] = f'{cv_data["antet"]["prenume"]} {cv_data["antet"]["nume"]}'.strip()
    st.session_state.wizard_data["hard_skills"] = [s.strip() for s in cv_data["competente"]["hard"].split(",") if
                                                   s.strip()]
    st.session_state.wizard_data["soft_skills"] = [s.strip() for s in cv_data["competente"]["soft"].split(",") if
                                                   s.strip()]

    # Estimăm anii de experiență pe baza numărului de joburi trecute (simplificat)
    exp_valide = [e for e in cv_data["experienta"] if e["post"]]
    st.session_state.wizard_data["experience_years"] = len(exp_valide) * 2  # default 2 ani per job, poți ajusta

    # Păstrăm structura completă a CV-ului pentru a o putea descărca/vizualiza ulterior
    st.session_state.wizard_data["cv_builder_data"] = cv_data

    # Fallback-uri pentru algoritm
    if not st.session_state.wizard_data.get("target_jobs"):
        st.session_state.wizard_data["target_jobs"] = list(JOBS.keys())[:5]
    if not st.session_state.wizard_data.get("domain"):
        st.session_state.wizard_data["domain"] = list(DOMAIN_META.keys())[0]

    # 1. Rulăm matching-ul
    st.session_state.recommendations = compute_recommendations(st.session_state.wizard_data, top_n=3)
    st.session_state.profile_completed = True

    # 2. Afișăm succesul și trecem la pagina următoare
    st.success("Profil salvat cu succes! Generăm recomandările...")
    time.sleep(1)
    st.switch_page("pages/4_Recomandari.py")

# ============================================================================
# 5. CSS
# ============================================================================
st.markdown("""
<style>
.cvb-wrap { max-width: 1180px; margin: 0 auto; padding-bottom: 3rem; }

/* --- Bară de progres orizontală --- */
.cvb-progress { display: flex; align-items: flex-start; justify-content: space-between;
    margin: 0.4rem 0 2.2rem 0; overflow-x: auto; padding-bottom: 0.2rem; }
.cvb-step { display: flex; flex-direction: column; align-items: center; gap: 0.35rem; flex: 1 1 auto; min-width: 64px; }
.cvb-step-circle { width: 32px; height: 32px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; background: #F1F3F6; color: #8A93A3;
    font-weight: 700; font-size: 0.8rem; border: 2px solid #E3E7ED; transition: all .2s ease; }
.cvb-step.active .cvb-step-circle { background: #2F6F5E; border-color: #2F6F5E; color: #fff; box-shadow: 0 0 0 4px rgba(47,111,94,0.15); }
.cvb-step.done .cvb-step-circle { background: #C99A56; border-color: #C99A56; color: #fff; }
.cvb-step-label { font-size: 0.68rem; font-weight: 600; color: #8A93A3; text-align: center; white-space: nowrap; }
.cvb-step.active .cvb-step-label, .cvb-step.done .cvb-step-label { color: #1B2430; }
.cvb-step-line { flex: 1 1 auto; height: 2px; background: #E3E7ED; margin: 15px 4px 0 4px; border-radius: 2px; }
.cvb-step-line.done { background: #C99A56; }

/* --- Carduri & Formulari --- */
.cvb-choice-card { border: 2px solid #ECEFF3; border-radius: 18px; padding: 1.6rem 1.4rem; background: #fff; height: 100%; transition: all .2s ease; cursor: pointer; }
.cvb-choice-card.selected { border-color: #2F6F5E; background: rgba(47,111,94,0.05); box-shadow: 0 8px 20px rgba(47,111,94,0.12); }
.cvb-choice-icon { font-size: 1.8rem; margin-bottom: 0.6rem; }
.cvb-choice-title { font-weight: 700; font-size: 1.05rem; color: #1B2430; margin: 0 0 0.3rem 0; }
.cvb-choice-sub { font-size: 0.85rem; color: #5B6472; margin: 0; }
.cvb-form-card { background: #fff; border: 1px solid #ECEFF3; border-radius: 18px; padding: 1.8rem 2rem; box-shadow: 0 8px 24px rgba(16,24,40,0.05); }
.cvb-form-title { font-size: 1.2rem; font-weight: 700; color: #1B2430; margin: 0 0 0.2rem 0; }
.cvb-form-sub { color: #5B6472; font-size: 0.88rem; margin: 0 0 1.3rem 0; }

/* --- Baza Previzualizare A4 --- */
.cvb-preview-shell { position: sticky; top: 1rem; }
.cvb-preview-caption { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #8A93A3; margin-bottom: 0.6rem; }
.cvb-a4 { background: #fff; border-radius: 4px; box-shadow: 0 12px 34px rgba(16,24,40,0.14); aspect-ratio: 210 / 297; overflow-y: auto; }
.cvb-a4-header { padding: 1.4rem 1.5rem 1.1rem 1.5rem; display: flex; align-items: center; gap: 1rem; }
.cvb-a4-avatar { width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; }
.cvb-a4-name { margin: 0; line-height: 1.15; }
.cvb-a4-contact { font-size: 0.72rem; opacity: 0.92; margin-top: 0.3rem; line-height: 1.5; }
.cvb-a4-body { padding: 1.1rem 1.5rem 1.6rem 1.5rem; }
.cvb-a4-section { margin-bottom: 1rem; }
.cvb-a4-section-title { padding-bottom: 0.25rem; margin-bottom: 0.45rem; }
.cvb-a4-text { font-size: 0.78rem; line-height: 1.5; margin: 0; }
.cvb-a4-subtitle { margin: 0; }
.cvb-a4-meta { font-size: 0.72rem; margin: 0 0 0.25rem 0; }
.cvb-a4-empty { font-size: 0.75rem; color: #C3C9D3; font-style: italic; }
.cvb-a4-pill-row { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.cvb-a4-pill { font-size: 0.68rem; padding: 0.2rem 0.55rem; }

/* === TEMA: CLASIC === */
.theme-classic { font-family: 'Sora', sans-serif; color: #333B45; }
.theme-classic .cvb-a4-header { background: linear-gradient(90deg, #2F6F5E, #24594A); color: #fff; }
.theme-classic .cvb-a4-avatar { border-radius: 50%; background: rgba(255,255,255,0.18); }
.theme-classic .cvb-a4-name { font-size: 1.15rem; font-weight: 800; }
.theme-classic .cvb-a4-section-title { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; color: #2F6F5E; text-transform: uppercase; border-bottom: 2px solid #ECEFF3; }
.theme-classic .cvb-a4-subtitle { font-size: 0.8rem; font-weight: 700; color: #1B2430; }
.theme-classic .cvb-a4-meta { color: #8A93A3; }
.theme-classic .cvb-a4-pill { background: #F1F3F6; color: #1B2430; font-weight: 600; border-radius: 999px; }

/* === TEMA: BOLD === */
.theme-bold { font-family: 'Inter', sans-serif; color: #111827; }
.theme-bold .cvb-a4-header { background: #111827; color: #F9FAFB; border-bottom: 6px solid #8A5CF5; }
.theme-bold .cvb-a4-avatar { border-radius: 8px; background: #8A5CF5; color: #fff; font-weight: 900; }
.theme-bold .cvb-a4-name { font-size: 1.3rem; font-weight: 900; letter-spacing: 1px; color: #8A5CF5; text-transform: uppercase; }
.theme-bold .cvb-a4-section-title { font-size: 0.75rem; font-weight: 900; color: #111827; text-transform: uppercase; border-bottom: 3px solid #111827; }
.theme-bold .cvb-a4-subtitle { font-size: 0.85rem; font-weight: 900; color: #8A5CF5; }
.theme-bold .cvb-a4-meta { color: #4B5563; font-weight: 600; }
.theme-bold .cvb-a4-pill { background: #111827; color: #F9FAFB; font-weight: 700; border-radius: 4px; }

/* === TEMA: MINIMAL === */
.theme-minimal { font-family: 'Georgia', serif; color: #000; }
.theme-minimal .cvb-a4-header { background: #fff; color: #000; border-bottom: 1px solid #000; padding-bottom: 1.5rem; }
.theme-minimal .cvb-a4-avatar { display: none; /* Fără poze inutile în design minimal */ }
.theme-minimal .cvb-a4-name { font-size: 1.4rem; font-weight: 400; letter-spacing: 2px; text-transform: uppercase; }
.theme-minimal .cvb-a4-contact { color: #555; }
.theme-minimal .cvb-a4-section-title { font-size: 0.8rem; font-weight: 600; color: #000; text-transform: capitalize; border-bottom: 1px solid #ddd; }
.theme-minimal .cvb-a4-subtitle { font-size: 0.85rem; font-weight: 600; color: #000; }
.theme-minimal .cvb-a4-meta { color: #666; font-style: italic; }
.theme-minimal .cvb-a4-pill { background: transparent; color: #000; font-weight: 400; border: 1px solid #ccc; border-radius: 2px; }

/* === TEMA: REGULUS (Accent Roșu) === */
.theme-regulus { font-family: 'Inter', sans-serif; color: #111; }
.theme-regulus .cvb-a4-header { background: #FFFFFF; color: #111; border-left: 8px solid #FF4B4B; padding-left: 2rem; margin-bottom: 2rem;}
.theme-regulus .cvb-a4-avatar { border-radius: 50%; background: #FF4B4B; color: #fff; font-weight: bold;}
.theme-regulus .cvb-a4-name { font-size: 1.5rem; font-weight: 800; color: #111; }
.theme-regulus .cvb-a4-section-title { font-size: 0.85rem; font-weight: 800; color: #FF4B4B; text-transform: uppercase; margin-bottom: 1rem; }
.theme-regulus .cvb-a4-pill { background: rgba(255, 75, 75, 0.1); color: #FF4B4B; }

/* === TEMA: POLLUX (Solid Verde Închis) === */
.theme-pollux { font-family: 'Sora', sans-serif; color: #333; }
.theme-pollux .cvb-a4-header { background: #1B3B36; color: #FFFFFF; padding: 2rem; }
.theme-pollux .cvb-a4-avatar { border-radius: 4px; background: #FFFFFF; color: #1B3B36; }
.theme-pollux .cvb-a4-name { font-size: 1.4rem; font-weight: 700; color: #FFFFFF; }
.theme-pollux .cvb-a4-contact { color: #A0B2AF; }
.theme-pollux .cvb-a4-section-title { font-size: 0.75rem; font-weight: 800; color: #1B3B36; border-bottom: 2px solid #1B3B36; }
.theme-pollux .cvb-a4-pill { background: #1B3B36; color: #FFF; }

/* 1. TEMA: CASTOR (Clasic - Echilibrat și sigur) */
.theme-classic { font-family: 'Sora', sans-serif; color: #333B45; }
.theme-classic .cvb-a4-header { background: linear-gradient(90deg, #2F6F5E, #24594A); color: #fff; }
.theme-classic .cvb-a4-avatar { border-radius: 50%; background: rgba(255,255,255,0.18); }
.theme-classic .cvb-a4-name { font-size: 1.25rem; font-weight: 800; text-transform: uppercase; }
.theme-classic .cvb-a4-section-title { font-size: 0.75rem; font-weight: 800; letter-spacing: 0.05em; color: #2F6F5E; text-transform: uppercase; border-bottom: 2px solid #ECEFF3; }
.theme-classic .cvb-a4-pill { background: #F1F3F6; color: #1B2430; font-weight: 600; border-radius: 999px; }

/* 2. TEMA: POLLUX (Solid - Verde închis, impunător) */
.theme-pollux { font-family: 'Inter', sans-serif; color: #2C3E50; }
.theme-pollux .cvb-a4-header { background: #1B3B36; color: #FFFFFF; padding: 2rem 1.5rem; }
.theme-pollux .cvb-a4-avatar { border-radius: 8px; background: #FFFFFF; color: #1B3B36; font-weight: 800; }
.theme-pollux .cvb-a4-name { font-size: 1.4rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; letter-spacing: 1px; }
.theme-pollux .cvb-a4-contact { color: #A0B2AF; }
.theme-pollux .cvb-a4-section-title { font-size: 0.8rem; font-weight: 800; color: #1B3B36; border-bottom: 3px solid #1B3B36; text-transform: uppercase; }
.theme-pollux .cvb-a4-pill { background: #1B3B36; color: #FFF; border-radius: 4px; }

/* 3. TEMA: ALTAIR (Minimal - Alb/Negru, focus pe tipografie) */
.theme-minimal { font-family: 'Georgia', serif; color: #111; }
.theme-minimal .cvb-a4-header { background: #fff; color: #000; border-bottom: 1px solid #000; padding-bottom: 1.5rem; }
.theme-minimal .cvb-a4-avatar { display: none; /* Fără avatar în design minimal */ }
.theme-minimal .cvb-a4-name { font-size: 1.5rem; font-weight: 400; letter-spacing: 2px; text-transform: uppercase; }
.theme-minimal .cvb-a4-contact { color: #555; font-family: 'Inter', sans-serif; }
.theme-minimal .cvb-a4-section-title { font-size: 0.85rem; font-weight: 600; color: #000; text-transform: uppercase; border-bottom: 1px solid #ddd; }
.theme-minimal .cvb-a4-pill { background: transparent; color: #000; font-weight: 400; border: 1px solid #ccc; border-radius: 0; }

/* 4. TEMA: REGULUS (Accent - Modern, bordură roșie stânga) */
.theme-regulus { font-family: 'Inter', sans-serif; color: #111; }
.theme-regulus .cvb-a4-header { background: #FAFAFA; color: #111; border-left: 8px solid #E63946; margin-bottom: 1rem; padding: 1.5rem; }
.theme-regulus .cvb-a4-avatar { border-radius: 50%; background: #E63946; color: #fff; font-weight: bold; }
.theme-regulus .cvb-a4-name { font-size: 1.5rem; font-weight: 900; color: #111; text-transform: uppercase; }
.theme-regulus .cvb-a4-section-title { font-size: 0.85rem; font-weight: 900; color: #E63946; text-transform: uppercase; margin-bottom: 1rem; border-bottom: none; }
.theme-regulus .cvb-a4-pill { background: rgba(230, 57, 70, 0.1); color: #E63946; font-weight: 700; border-radius: 6px; }

/* 5. TEMA: CAPELLA (Elegant - Albastru marin și auriu) */
.theme-capella { font-family: 'Georgia', serif; color: #333; }
.theme-capella .cvb-a4-header { background: #0A192F; color: #E6F1FF; border-bottom: 4px solid #D4AF37; }
.theme-capella .cvb-a4-avatar { border-radius: 50%; border: 2px solid #D4AF37; background: transparent; color: #D4AF37; }
.theme-capella .cvb-a4-name { font-size: 1.4rem; font-weight: 400; color: #D4AF37; letter-spacing: 1px; text-transform: uppercase; }
.theme-capella .cvb-a4-section-title { font-family: 'Inter', sans-serif; font-size: 0.75rem; font-weight: 700; color: #0A192F; text-transform: uppercase; border-bottom: 1px solid #D4AF37; }
.theme-capella .cvb-a4-pill { background: #0A192F; color: #D4AF37; font-family: 'Inter', sans-serif; border-radius: 4px; }

/* 6. TEMA: VEGA (Creativ - Forme rotunde, lila pastel) */
.theme-vega { font-family: 'Sora', sans-serif; color: #4A4A4A; }
.theme-vega .cvb-a4-header { background: #F3E8FF; color: #3B0764; border-radius: 0 0 30px 30px; margin-bottom: 1rem; }
.theme-vega .cvb-a4-avatar { border-radius: 16px; background: #9333EA; color: #fff; }
.theme-vega .cvb-a4-name { font-size: 1.3rem; font-weight: 800; color: #3B0764; }
.theme-vega .cvb-a4-contact { color: #6B21A8; }
.theme-vega .cvb-a4-section-title { font-size: 0.8rem; font-weight: 800; color: #9333EA; border-bottom: 2px dashed #D8B4FE; border-radius: 4px; }
.theme-vega .cvb-a4-pill { background: #F3E8FF; color: #7E22CE; font-weight: 700; border-radius: 20px; }

/* 7. TEMA: SIRIUS (Tehnic - IT/Inginerie, Monospace vibe) */
.theme-sirius { font-family: 'Courier New', Courier, monospace; color: #1F2937; }
.theme-sirius .cvb-a4-header { background: #111827; color: #10B981; border-bottom: 2px solid #10B981; }
.theme-sirius .cvb-a4-avatar { border-radius: 0; background: #10B981; color: #111827; font-weight: bold; }
.theme-sirius .cvb-a4-name { font-size: 1.2rem; font-weight: bold; color: #10B981; text-transform: lowercase; }
.theme-sirius .cvb-a4-name::before { content: "> "; }
.theme-sirius .cvb-a4-contact { color: #9CA3AF; }
.theme-sirius .cvb-a4-section-title { font-size: 0.8rem; font-weight: bold; color: #111827; background: #F3F4F6; padding: 0.2rem 0.5rem; border-left: 4px solid #10B981; }
.theme-sirius .cvb-a4-pill { background: #E5E7EB; color: #111827; font-weight: bold; border-radius: 0; }

/* 8. TEMA: ORION (Executiv - Gri șist, ultra formal) */
.theme-orion { font-family: 'Inter', sans-serif; color: #374151; }
.theme-orion .cvb-a4-header { background: #374151; color: #F9FAFB; }
.theme-orion .cvb-a4-avatar { border-radius: 2px; background: #9CA3AF; color: #111827; }
.theme-orion .cvb-a4-name { font-size: 1.4rem; font-weight: 300; letter-spacing: 2px; text-transform: uppercase; }
.theme-orion .cvb-a4-contact { color: #D1D5DB; }
.theme-orion .cvb-a4-section-title { font-size: 0.75rem; font-weight: 700; color: #374151; text-transform: uppercase; border-bottom: 1px solid #9CA3AF; }
.theme-orion .cvb-a4-pill { background: #F3F4F6; color: #374151; border: 1px solid #D1D5DB; border-radius: 4px; }

/* 9. TEMA: NOVA (Dinamic - High contrast cu Galben/Portocaliu) */
.theme-nova { font-family: 'Inter', sans-serif; color: #171717; }
.theme-nova .cvb-a4-header { background: #171717; color: #FFF; border-bottom: 6px solid #F59E0B; }
.theme-nova .cvb-a4-avatar { border-radius: 50%; background: #F59E0B; color: #171717; font-weight: 900; }
.theme-nova .cvb-a4-name { font-size: 1.5rem; font-weight: 900; color: #F59E0B; text-transform: uppercase; font-style: italic; }
.theme-nova .cvb-a4-section-title { font-size: 0.85rem; font-weight: 900; color: #171717; text-transform: uppercase; border-bottom: 3px solid #F59E0B; }
.theme-nova .cvb-a4-pill { background: #FFFBEB; color: #D97706; border: 1px solid #F59E0B; font-weight: 700; border-radius: 6px; }

/* 10. TEMA: ZENITH (Simplu - Natur / Sage Green) */
.theme-zenith { font-family: 'Sora', sans-serif; color: #4B5563; }
.theme-zenith .cvb-a4-header { background: #F4F5F0; color: #2F3E3B; border-bottom: 1px solid #D5D9D2; }
.theme-zenith .cvb-a4-avatar { border-radius: 50%; background: #8E9F94; color: #fff; }
.theme-zenith .cvb-a4-name { font-size: 1.3rem; font-weight: 600; color: #2F3E3B; }
.theme-zenith .cvb-a4-contact { color: #6B7280; }
.theme-zenith .cvb-a4-section-title { font-size: 0.8rem; font-weight: 700; color: #8E9F94; border-bottom: 2px solid #E5E7EB; text-transform: uppercase; }
.theme-zenith .cvb-a4-pill { background: #F4F5F0; color: #2F3E3B; font-weight: 600; border-radius: 8px; border: 1px solid #D5D9D2; }

.stButton button[kind="primary"] { background: linear-gradient(90deg, #2F6F5E, #24594A); border: none; border-radius: 12px; font-weight: 700; color: white; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# 6. RANDARE — BARĂ DE PROGRES
# ============================================================================
def render_progress_bar():
    active = _active_steps()
    current_idx = st.session_state.cvb_step_idx
    parts = ['<div class="cvb-progress">']
    for i, step in enumerate(active):
        state = "active" if i == current_idx else ("done" if i < current_idx else "")
        parts.append(f'<div class="cvb-step {state}"><div class="cvb-step-circle">{i + 1}</div>'
                     f'<div class="cvb-step-label">{step["label"]}</div></div>')
        if i < len(active) - 1:
            line_state = "done" if i < current_idx else ""
            parts.append(f'<div class="cvb-step-line {line_state}"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


# ============================================================================
# 7. RANDARE — PREVIZUALIZARE A4 LIVE
# ============================================================================
def render_cv_preview(d: dict):
    model_ales = d.get("model", "classic")
    theme_class = f"theme-{model_ales}"

    # Helper: Dacă valoarea e goală, afișează placeholder-ul (mock), altfel afișează valoarea reală
    def val(real, mock):
        return real if real and str(real).strip() else mock

    antet = d["antet"]
    prenume_afisat = val(antet["prenume"], "Alexandru")
    nume_afisat = val(antet["nume"], "Popescu")
    nume_complet = f"{prenume_afisat} {nume_afisat}".strip()
    initiala = (prenume_afisat[:1] or nume_afisat[:1] or "?").upper()

    tel_afisat = val(antet["telefon"], "+40 722 123 456")
    email_afisat = val(antet["email"], "alex.popescu@email.com")
    adresa_afisat = val(antet["adresa"], "București, România")

    contact_bits = [v for v in [tel_afisat, email_afisat, adresa_afisat] if v]
    contact_html = " &nbsp;·&nbsp; ".join(_esc(c) for c in contact_bits)

    html_parts = [
        f'<div class="cvb-a4 {theme_class}">',
        '  <div class="cvb-a4-header">',
        f'    <div class="cvb-a4-avatar">{_esc(initiala)}</div>',
        '    <div>',
        f'      <p class="cvb-a4-name">{_esc(nume_complet)}</p>',
        f'      <div class="cvb-a4-contact">{contact_html}</div>',
        '    </div>',
        '  </div>',
        '  <div class="cvb-a4-body">',
    ]

    # Profil profesional
    txt_profil = val(d["profil"],
                     "Profesionist dedicat, cu o capacitate rapidă de învățare și adaptare. Orientat spre rezultate, cu abilități excelente de comunicare și rezolvare a problemelor. Caut să mă dezvolt într-un mediu dinamic, contribuind activ la succesul echipei.")
    html_parts.append('<div class="cvb-a4-section"><div class="cvb-a4-section-title">Profil profesional</div>')
    html_parts.append(f'<p class="cvb-a4-text">{_esc(txt_profil)}</p>')
    html_parts.append('</div>')

    # Competențe
    txt_hard = val(d["competente"]["hard"], "Management de Proiect, Analiză Date, Python, SQL, Excel")
    txt_soft = val(d["competente"]["soft"], "Comunicare eficientă, Leadership, Rezolvarea problemelor, Lucru în echipă")

    hard = [s.strip() for s in txt_hard.split(",") if s.strip()]
    soft = [s.strip() for s in txt_soft.split(",") if s.strip()]

    if hard or soft:
        html_parts.append('<div class="cvb-a4-section"><div class="cvb-a4-section-title">Competențe</div>')
        html_parts.append('<div class="cvb-a4-pill-row">')
        for s in (hard + soft):
            html_parts.append(f'<span class="cvb-a4-pill">{_esc(s)}</span>')
        html_parts.append('</div></div>')

    # Experiență
    exp_valide = [e for e in d["experienta"] if e["post"] or e["angajator"]]
    if not exp_valide:
        # Date demo dacă utilizatorul nu a adăugat nimic încă
        exp_valide = [
            {"post": "Specialist Marketing", "angajator": "Tech Solutions SRL", "oras": "București",
             "data_inceput": "Ian 2021", "data_sfarsit": "Prezent",
             "descriere": "Am coordonat campanii de promovare digitale care au dus la o creștere cu 25% a vânzărilor. Colaborare inter-departamentală pentru lansarea de noi produse pe piață."},
            {"post": "Asistent Manager", "angajator": "Global Trade", "oras": "Cluj-Napoca", "data_inceput": "Aug 2018",
             "data_sfarsit": "Dec 2020",
             "descriere": "Organizarea agendei zilnice, suport administrativ, și gestionarea relațiilor cu clienții cheie ai companiei."}
        ]

    if exp_valide:
        html_parts.append('<div class="cvb-a4-section"><div class="cvb-a4-section-title">Experiență profesională</div>')
        for exp in exp_valide:
            perioada_str = f'{exp["data_inceput"]} – {exp["data_sfarsit"] or "prezent"}' if exp["data_inceput"] or exp[
                "data_sfarsit"] else ""
            html_parts.append(f'<p class="cvb-a4-subtitle">{_esc(exp["post"] or "Denumire post")}</p>')

            locatie_txt = f', {_esc(exp.get("oras", ""))}' if exp.get("oras") else ""
            perioada_txt = f' · {_esc(perioada_str)}' if perioada_str else ""

            html_parts.append(f'<p class="cvb-a4-meta">{_esc(exp.get("angajator", ""))}{locatie_txt}{perioada_txt}</p>')
            if exp.get("descriere"):
                html_parts.append(f'<p class="cvb-a4-text">{_esc(exp["descriere"])}</p>')
            html_parts.append('<div style="margin-bottom: 12px;"></div>')
        html_parts.append('</div>')

    # Educație
    edu_valide = [ed for ed in d["educatie"] if ed["institutie"] or ed["calificare"]]
    if not edu_valide:
        edu_valide = [
            {"institutie": "Universitatea Babeș-Bolyai", "calificare": "Diplomă de Licență",
             "domeniu": "Științe Economice", "perioada": "2015 – 2018"}
        ]

    if edu_valide:
        html_parts.append('<div class="cvb-a4-section"><div class="cvb-a4-section-title">Educație</div>')
        for edu in edu_valide:
            html_parts.append(f'<p class="cvb-a4-subtitle">{_esc(edu["institutie"] or "Instituție")}</p>')
            detalii = " · ".join(_esc(v) for v in [edu["calificare"], edu.get("domeniu", ""), edu["perioada"]] if v)
            if detalii:
                html_parts.append(f'<p class="cvb-a4-meta">{detalii}</p>')
            html_parts.append('<div style="margin-bottom: 8px;"></div>')
        html_parts.append('</div>')

    # Limbi
    limbi_valide = [l for l in d["limbi"] if l["limba"]]
    if not limbi_valide:
        limbi_valide = [
            {"limba": "Engleză", "nivel": "Avansat"},
            {"limba": "Franceză", "nivel": "Mediu"}
        ]

    if limbi_valide:
        html_parts.append('<div class="cvb-a4-section"><div class="cvb-a4-section-title">Limbi cunoscute</div>')
        for l in limbi_valide:
            html_parts.append(f'<p class="cvb-a4-text"><b>{_esc(l["limba"])}</b> — {_esc(l.get("nivel", ""))}</p>')
        html_parts.append('</div>')

    # Realizări
    txt_realizari = val(d["realizari"],
                        "Premiul 'Angajatul Anului' în 2022. Certificare avansată în Data Analytics (Coursera).")
    if txt_realizari:
        html_parts.append(
            '<div class="cvb-a4-section"><div class="cvb-a4-section-title">Realizări &amp; certificări</div>')
        html_parts.append(f'<p class="cvb-a4-text">{_esc(txt_realizari)}</p>')
        html_parts.append('</div>')

    html_parts.append('</div></div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)

def render_preview_column():
    st.markdown('<div class="cvb-preview-shell">', unsafe_allow_html=True)
    st.markdown('<p class="cvb-preview-caption">📄 Previzualizare live</p>', unsafe_allow_html=True)
    render_cv_preview(cv_data)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# 8. RANDARE — NAVIGARE JOS (Înapoi / Înainte)
# ============================================================================
def render_bottom_nav(next_label="Înainte ➜", on_next_extra=None, next_disabled=False):
    active = _active_steps()
    is_last = st.session_state.cvb_step_idx == len(active) - 1
    is_first = st.session_state.cvb_step_idx == 0

    c1, _, c3 = st.columns([1, 2, 1])
    with c1:
        if not is_first:
            if st.button("⬅ Înapoi", use_container_width=True, key=f"back_{st.session_state.cvb_step_idx}"):
                go_prev()
                st.rerun()
    with c3:
        if not is_last:
            if st.button(next_label, type="primary", use_container_width=True,
                         disabled=next_disabled, key=f"next_{st.session_state.cvb_step_idx}"):
                if on_next_extra:
                    on_next_extra()
                go_next()
                st.rerun()


# ============================================================================
# 9. RANDARE PAȘI INDIVIDUALI
# ============================================================================
def step_model():
    st.markdown("### 🎨 Alege-ți modelul de CV")
    st.caption("Alege din variantele de mai jos. Previzualizarea se actualizează instant în dreapta.")

    col_form, col_preview = st.columns([1, 1.2])

    with col_form:
        # Lista extinsă de 10 modele (folosind denumirile din referința ta)
        templates = [
            {"id": "classic", "title": "Castor (Clasic)", "icon": "📄"},
            {"id": "pollux", "title": "Pollux (Solid)", "icon": "🟩"},
            {"id": "minimal", "title": "Altair (Minimal)", "icon": "✒️"},
            {"id": "regulus", "title": "Regulus (Accent)", "icon": "🔴"},
            {"id": "capella", "title": "Capella (Elegant)", "icon": "💎"},
            {"id": "vega", "title": "Vega (Creativ)", "icon": "🎨"},
            {"id": "sirius", "title": "Sirius (Tehnic)", "icon": "⚙️"},
            {"id": "orion", "title": "Orion (Executiv)", "icon": "👔"},
            {"id": "nova", "title": "Nova (Dinamic)", "icon": "🚀"},
            {"id": "zenith", "title": "Zenith (Simplu)", "icon": "🌿"},
        ]

        # Container cu scroll pentru a menține interfața curată
        with st.container(height=650, border=False):
            # Creăm o grilă pe 2 coloane
            for i in range(0, len(templates), 2):
                c1, c2 = st.columns(2)

                # Prima coloană (Modelul i)
                tpl1 = templates[i]
                with c1:
                    selected1 = cv_data["model"] == tpl1["id"]
                    state_cls1 = "selected" if selected1 else ""
                    st.markdown(
                        f'<div class="cvb-choice-card {state_cls1}" style="padding: 1.2rem 1rem; text-align: center; margin-bottom: 0.5rem;">'
                        f'<div class="cvb-choice-icon" style="font-size: 1.8rem; margin-bottom: 0.2rem;">{tpl1["icon"]}</div>'
                        f'<p class="cvb-choice-title" style="font-size: 0.9rem;">{tpl1["title"]}</p>'
                        f'</div>', unsafe_allow_html=True
                    )
                    if st.button("Selectează" if not selected1 else "✓ Selectat",
                                 key=f"tpl_{tpl1['id']}", use_container_width=True,
                                 type="primary" if selected1 else "secondary"):
                        cv_data["model"] = tpl1["id"]
                        st.rerun()

                # A doua coloană (Modelul i+1)
                if i + 1 < len(templates):
                    tpl2 = templates[i + 1]
                    with c2:
                        selected2 = cv_data["model"] == tpl2["id"]
                        state_cls2 = "selected" if selected2 else ""
                        st.markdown(
                            f'<div class="cvb-choice-card {state_cls2}" style="padding: 1.2rem 1rem; text-align: center; margin-bottom: 0.5rem;">'
                            f'<div class="cvb-choice-icon" style="font-size: 1.8rem; margin-bottom: 0.2rem;">{tpl2["icon"]}</div>'
                            f'<p class="cvb-choice-title" style="font-size: 0.9rem;">{tpl2["title"]}</p>'
                            f'</div>', unsafe_allow_html=True
                        )
                        if st.button("Selectează" if not selected2 else "✓ Selectat",
                                     key=f"tpl_{tpl2['id']}", use_container_width=True,
                                     type="primary" if selected2 else "secondary"):
                            cv_data["model"] = tpl2["id"]
                            st.rerun()

        st.write("---")
        render_bottom_nav()

    with col_preview:
        # Previzualizarea din dreapta va reacționa instant când se apasă un buton!
        render_preview_column()

def step_metoda():
    st.markdown("### 🧭 Cum vrei să-ți creezi CV-ul?")

    c1, c2 = st.columns(2)
    options = [
        {"id": "zero", "icon": "📝", "title": "Creează un CV de la zero",
         "sub": "Vom parcurge fiecare secțiune împreună.", "col": c1},
        {"id": "existing", "icon": "📤", "title": "Am deja un CV",
         "sub": "Îl scanăm cu AI și îți pre-completăm câmpurile.", "col": c2},
    ]
    for opt in options:
        with opt["col"]:
            selected = cv_data["metoda"] == opt["id"]
            st.markdown(
                f'<div class="cvb-choice-card {"selected" if selected else ""}">'
                f'<div class="cvb-choice-icon">{opt["icon"]}</div>'
                f'<p class="cvb-choice-title">{opt["title"]}</p>'
                f'<p class="cvb-choice-sub">{opt["sub"]}</p></div>',
                unsafe_allow_html=True,
            )
            if st.button("Alege" if not selected else "✓ Ales", key=f"metoda_{opt['id']}",
                         use_container_width=True, type="primary" if selected else "secondary"):
                cv_data["metoda"] = opt["id"]
                st.rerun()

    # Sub-flux AI (doar dacă a ales "Am deja un CV") — folosește mock-ul, nu un API real.
    if cv_data["metoda"] == "existing":
        st.write("")
        with st.container(border=True):
            st.markdown("#### 📂 Încarcă imaginea CV-ului existent")
            uploaded = st.file_uploader("PNG / JPG", type=["png", "jpg", "jpeg"], key="cvb_upload")
            if uploaded is not None and st.button("🚀 Extrage datele (mock AI)", type="primary"):
                extracted = mock_ai_extract_cv_data(uploaded)
                for section, values in extracted.items():
                    if isinstance(values, dict):
                        cv_data[section].update(values)
                    else:
                        cv_data[section] = values
                st.success("Date pre-completate (mock). Le poți verifica în pașii următori.")

    st.write("")
    render_bottom_nav(next_disabled=cv_data["metoda"] is None)


def step_antet():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Primul pas: antetul</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="cvb-form-sub">Numele complet și adresa de e-mail sunt esențiale — restul e opțional.</p>',
            unsafe_allow_html=True)

        a = cv_data["antet"]
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Prenume", value=a["prenume"], key="antet_prenume",
                          on_change=bind("antet", "prenume", "antet_prenume"))
        with c2:
            st.text_input("Nume de familie", value=a["nume"], key="antet_nume",
                          on_change=bind("antet", "nume", "antet_nume"))

        st.text_input("Adresă", value=a["adresa"], key="antet_adresa",
                      on_change=bind("antet", "adresa", "antet_adresa"),
                      placeholder="Strada, Orașul, Județul")

        c3, c4 = st.columns(2)
        with c3:
            st.text_input("Număr de telefon", value=a["telefon"], key="antet_telefon",
                          on_change=bind("antet", "telefon", "antet_telefon"))
        with c4:
            st.text_input("E-mail", value=a["email"], key="antet_email",
                          on_change=bind("antet", "email", "antet_email"))

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_experienta():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Adaugă-ți experiența profesională</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Începe cu cel mai recent job. Poți include și stagii sau voluntariat.</p>', unsafe_allow_html=True)

        for i, e in enumerate(cv_data["experienta"]):
            if i > 0:
                st.markdown(f"<hr style='margin: 1.5rem 0; border-color: #ECEFF3;'>", unsafe_allow_html=True)
                st.markdown(f"**Experiența #{i+1}**")

            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Denumirea postului", value=e["post"], key=f"exp_post_{i}",
                              on_change=bind_list_item("experienta", i, "post", f"exp_post_{i}"),
                              placeholder="de ex., asistent contabil")
            with c2:
                st.text_input("Angajator", value=e["angajator"], key=f"exp_angajator_{i}",
                              on_change=bind_list_item("experienta", i, "angajator", f"exp_angajator_{i}"))

            c3, c4, c5 = st.columns(3)
            with c3:
                st.text_input("Orașul", value=e["oras"], key=f"exp_oras_{i}",
                              on_change=bind_list_item("experienta", i, "oras", f"exp_oras_{i}"))
            with c4:
                st.text_input("Data începerii", value=e["data_inceput"], key=f"exp_start_{i}",
                              on_change=bind_list_item("experienta", i, "data_inceput", f"exp_start_{i}"),
                              placeholder="Luna / Anul")
            with c5:
                st.text_input("Data încetării", value=e["data_sfarsit"], key=f"exp_end_{i}",
                              on_change=bind_list_item("experienta", i, "data_sfarsit", f"exp_end_{i}"),
                              placeholder="Luna / Anul sau prezent")

            st.text_area("Descriere activitate", value=e["descriere"], key=f"exp_desc_{i}", height=110,
                         on_change=bind_list_item("experienta", i, "descriere", f"exp_desc_{i}"))

        st.write("")
        if st.button("➕ Adaugă o nouă experiență", use_container_width=True):
            cv_data["experienta"].append({"post": "", "angajator": "", "oras": "", "data_inceput": "", "data_sfarsit": "", "descriere": ""})
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_educatie():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Adaugă-ți parcursul educațional</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Enumeră calificările obținute sau în curs.</p>', unsafe_allow_html=True)

        for i, ed in enumerate(cv_data["educatie"]):
            if i > 0:
                st.markdown(f"<hr style='margin: 1.5rem 0; border-color: #ECEFF3;'>", unsafe_allow_html=True)
                st.markdown(f"**Educația #{i+1}**")

            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Instituția", value=ed["institutie"], key=f"edu_inst_{i}",
                              on_change=bind_list_item("educatie", i, "institutie", f"edu_inst_{i}"))
            with c2:
                st.text_input("Calificarea sau diploma", value=ed["calificare"], key=f"edu_calif_{i}",
                              on_change=bind_list_item("educatie", i, "calificare", f"edu_calif_{i}"))

            c3, c4 = st.columns(2)
            with c3:
                st.text_input("Domeniul de studii", value=ed["domeniu"], key=f"edu_domeniu_{i}",
                              on_change=bind_list_item("educatie", i, "domeniu", f"edu_domeniu_{i}"))
            with c4:
                st.text_input("Perioada", value=ed["perioada"], key=f"edu_perioada_{i}",
                              on_change=bind_list_item("educatie", i, "perioada", f"edu_perioada_{i}"),
                              placeholder="ex: 2021 – 2024")

        st.write("")
        if st.button("➕ Adaugă o nouă educație", use_container_width=True):
            cv_data["educatie"].append({"institutie": "", "calificare": "", "domeniu": "", "perioada": ""})
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()

def step_competente():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Adaugă-ți competențele dobândite</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Separă competențele prin virgulă.</p>', unsafe_allow_html=True)

        c = cv_data["competente"]
        st.text_area("Competențe tehnice (hard skills)", value=c["hard"], key="comp_hard", height=90,
                     on_change=bind("competente", "hard", "comp_hard"),
                     placeholder="ex: Excel, Contabilitate primară, SAP")
        st.text_area("Abilități personale (soft skills)", value=c["soft"], key="comp_soft", height=90,
                     on_change=bind("competente", "soft", "comp_soft"),
                     placeholder="ex: Comunicare, Atenție la detalii")

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_profil():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Creează-ți un profil profesional</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Descrie-ți parcursul sau obiectivele de carieră în câteva propoziții.</p>',
                    unsafe_allow_html=True)

        st.text_area("Profil profesional", value=cv_data["profil"], key="profil_txt", height=160,
                     on_change=bind_flat("profil", "profil_txt"),
                     placeholder="Scrie ceva despre tine, despre ce faci și despre competențele tale unice…")

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_sectiuni():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Adaugă mai multe secțiuni</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Toate secțiunile de mai jos sunt opționale.</p>', unsafe_allow_html=True)

        se = cv_data["sectiuni_extra"]
        se["limbi"] = st.checkbox("🌐 Limbi cunoscute", value=se["limbi"], key="sect_limbi")
        se["realizari"] = st.checkbox("🏆 Realizări și certificări", value=se["realizari"], key="sect_realizari")

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_limbi():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Adaugă limbile pe care le cunoști</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Introdu fiecare limbă și nivelul de competență.</p>',
                    unsafe_allow_html=True)

        nivele = ["Începător", "Mediu", "Avansat", "Fluent", "Limbă maternă"]
        for i, entry in enumerate(cv_data["limbi"]):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.text_input(f"Limba #{i + 1}", value=entry["limba"], key=f"limba_{i}",
                              on_change=bind_list_item("limbi", i, "limba", f"limba_{i}"))
            with c2:
                st.selectbox(f"Nivel #{i + 1}", nivele,
                             index=nivele.index(entry["nivel"]) if entry["nivel"] in nivele else 0,
                             key=f"nivel_{i}", on_change=bind_list_item("limbi", i, "nivel", f"nivel_{i}"))

        if st.button("➕ Adaugă o altă limbă", use_container_width=True):
            cv_data["limbi"].append({"limba": "", "nivel": "Începător"})
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_realizari():
    col_form, col_preview = st.columns([1, 1.2])
    with col_form:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Realizări și certificări</p>', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-sub">Menționează premii, certificări sau realizări notabile.</p>',
                    unsafe_allow_html=True)

        st.text_area("Realizări & certificări", value=cv_data["realizari"], key="realizari_txt", height=150,
                     on_change=bind_flat("realizari", "realizari_txt"))

        st.markdown('</div>', unsafe_allow_html=True)
        render_bottom_nav()

    with col_preview:
        render_preview_column()


def step_finalizare():
    st.markdown("### 🎉 CV-ul tău e gata de revizuit")
    st.caption("Verifică previzualizarea de mai jos, apoi salvează profilul pentru a genera recomandările.")

    col_settings, col_preview = st.columns([1, 1.2])
    with col_settings:
        st.markdown('<div class="cvb-form-card">', unsafe_allow_html=True)
        st.markdown('<p class="cvb-form-title">Setări finale</p>', unsafe_allow_html=True)
        st.caption(f"Model selectat: **{cv_data['model']}**")
        st.caption("Culorile și fonturile vor fi configurabile aici (placeholder pentru viitoarele opțiuni de temă).")

        for i, s in enumerate(_active_steps()[:-1]):
            if st.button(f"✏️ Editează: {s['label']}", key=f"jump_{s['key']}", use_container_width=True):
                go_to_key(s["key"])
                st.rerun()

        st.write("")
        if st.button("💾 Salvează și generează recomandările", type="primary", use_container_width=True):
            _finalize_and_go(cv_data)

        st.markdown('</div>', unsafe_allow_html=True)

        c1, _ = st.columns([1, 2])
        with c1:
            if st.button("⬅ Înapoi", key="back_final"):
                go_prev()
                st.rerun()

    with col_preview:
        render_preview_column()


STEP_RENDERERS = {
    "model": step_model,
    "metoda": step_metoda,
    "antet": step_antet,
    "experienta": step_experienta,
    "educatie": step_educatie,
    "competente": step_competente,
    "profil": step_profil,
    "sectiuni": step_sectiuni,
    "limbi": step_limbi,
    "realizari": step_realizari,
    "finalizare": step_finalizare,
}

# ============================================================================
# 10. RANDARE PRINCIPALĂ
# ============================================================================
st.markdown('<div class="cvb-wrap">', unsafe_allow_html=True)
st.markdown("## 🧩 CV Builder")
st.caption("Construiește-ți CV-ul pas cu pas, cu previzualizare live.")

_clamp_step_index()
render_progress_bar()

active_steps = _active_steps()
current_step = active_steps[st.session_state.cvb_step_idx]
STEP_RENDERERS[current_step["key"]]()

st.markdown('</div>', unsafe_allow_html=True)
