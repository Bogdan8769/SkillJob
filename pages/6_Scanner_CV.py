"""
pages/6_Scanner_CV.py
---------------------
Pagină de onboarding a CV-ului, cu două fluxuri:
  - "Da, am un CV" -> upload imagine + extragere și expansiune semantică cu Groq Vision (AI)
  - "Nu, îl creez acum" -> formular structurat, completat manual
"""

import os
import json
import time
import base64

import streamlit as st
from groq import Groq
from dotenv import load_dotenv

from layout import bootstrap_page, require_login, render_nav_sidebar, render_account_sidebar
from database import DOMAIN_META, JOBS, HARD_SKILLS_BY_DOMAIN
from matching import compute_recommendations

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_VISION_MODEL = "qwen/qwen3.6-27b"

bootstrap_page("Scanner CV", icon="🤖")
require_login()
render_nav_sidebar()
render_account_sidebar()

# ---------------------------------------------------------------------------
# STIL
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.sj-scanner-wrap { max-width: 820px; margin: 0 auto; padding-bottom: 3rem; }

[data-testid="stSegmentedControl"] label { font-weight: 600; }

[data-testid="stFileUploader"] section {
    background-color: #F8F9FA !important;
    border: 2px dashed #C99A56 !important;
}
[data-testid="stFileUploader"] section > div > span,
[data-testid="stFileUploader"] section > div > small {
    color: #1B2430 !important;
}
[data-testid="stFileUploader"] button {
    background-color: #2F6F5E !important;
    color: #FFFFFF !important;
    border: none !important;
}
[data-testid="stUploadedFile"] {
    background-color: #E9ECEF !important;
    border-radius: 8px !important;
}
[data-testid="stUploadedFile"] div,
[data-testid="stUploadedFile"] span,
[data-testid="stUploadedFile"] button,
[data-testid="stUploadedFile"] p {
    color: #1B2430 !important;
}

.stButton button[kind="primary"] {
    background: linear-gradient(90deg, #2F6F5E, #24594A);
    border: none; border-radius: 12px; font-weight: 700; color: white;
}

.sj-flow-card { background: #FFFFFF; border: 1px solid #ECEFF3; border-radius: 18px;
    padding: 1.8rem 2rem; box-shadow: 0 8px 24px rgba(16,24,40,0.05); margin-bottom: 1.2rem; }
.sj-flow-heading { font-size: 1.15rem; font-weight: 700; color: #1B2430; margin: 0 0 0.9rem 0; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# GROQ VISION & AI SEMANTIC PARSING
# ---------------------------------------------------------------------------
def encode_image_to_base64(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def analyze_cv_with_groq(uploaded_file) -> dict:
    client = Groq(api_key=GROQ_API_KEY)
    base64_image = encode_image_to_base64(uploaded_file)

    prompt = """Return ONLY a valid JSON object with no extra text, markdown blocks, or explanations. 
    Format required:
    {
        "nume": "string",
        "experienta_ani": 0,
        "hard_skills": ["skill1", "skill2"],
        "soft_skills": ["skill1", "skill2"]
    }
    Analyze the uploaded resume image, extract the candidate's full name, estimate total years of experience as an integer, extract technical skills (expanding tools like IntelliJ to Java, React to JavaScript, etc.), and extract soft skills."""

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        model=GROQ_VISION_MODEL,
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)


# ---------------------------------------------------------------------------
# STARE
# ---------------------------------------------------------------------------
if "ai_parsed_data" not in st.session_state:
    st.session_state.ai_parsed_data = None
if "cv_flow_choice" not in st.session_state:
    st.session_state.cv_flow_choice = None


def _finalize_and_go(nume, hard_skills, soft_skills, extra=None):
    """Salvează în wizard_data, rulează motorul de matching și redirecționează."""
    if "wizard_data" not in st.session_state:
        st.session_state.wizard_data = {}

    st.session_state.wizard_data["nume"] = nume
    st.session_state.wizard_data["hard_skills"] = hard_skills
    st.session_state.wizard_data["soft_skills"] = soft_skills
    if extra:
        st.session_state.wizard_data.update(extra)

    if not st.session_state.wizard_data.get("target_jobs"):
        st.session_state.wizard_data["target_jobs"] = list(JOBS.keys())[:5]
    if not st.session_state.wizard_data.get("domain"):
        st.session_state.wizard_data["domain"] = list(DOMAIN_META.keys())[0]

    # Salvăm explicit atât recomandările, cât și un flag de status
    st.session_state.recommendations = compute_recommendations(st.session_state.wizard_data, top_n=3)
    st.session_state.profile_completed = True

    st.success("Profil analizat și salvat! Se generează recomandările...")
    time.sleep(0.5)
    st.switch_page("pages/4_Recomandari.py")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.markdown('<div class="sj-scanner-wrap">', unsafe_allow_html=True)
st.markdown("<h2>📋 Hai să pornim de la CV-ul tău</h2>", unsafe_allow_html=True)
st.markdown(
    "<p style='color: var(--text-soft); margin-bottom: 1.6rem;'>"
    "Alege cum vrei să începi — încarci un CV și AI-ul va extrage și extinde inteligent competențele, "
    "sau îl construiești manual pas cu pas.</p>",
    unsafe_allow_html=True,
)

choice = st.segmented_control(
    "Ai deja un CV?",
    options=["📷 Da, am un CV (poză)", "✍️ Nu, vreau să-l creez acum"],
    default=st.session_state.cv_flow_choice,
    label_visibility="visible",
)
if choice:
    st.session_state.cv_flow_choice = choice

st.write("")

# =====================================================================
# FLUX A — AM UN CV (AI VISION CU EXPANSIUNE SEMANTICĂ)
# =====================================================================
if choice == "📷 Da, am un CV (poză)":

    with st.container(border=True):
        st.markdown("#### 📂 1. Încarcă imaginea CV-ului")
        uploaded_cv = st.file_uploader(
            "Formate acceptate: PNG, JPG, JPEG", type=["png", "jpg", "jpeg"], key="scanner_file_up"
        )

        if uploaded_cv is not None:
            if not GROQ_API_KEY:
                st.error("Lipsește GROQ_API_KEY din configurație (.env). Scanarea AI nu poate porni.")
            elif st.button("🚀 Scanează inteligent cu AI", type="primary", use_container_width=True):
                with st.spinner("AI-ul citește documentul și deduce conexiunile tehnice..."):
                    try:
                        parsed = analyze_cv_with_groq(uploaded_cv)
                        st.session_state.ai_parsed_data = parsed
                        st.success("Analiză și expansiune semantică finalizate!")
                    except Exception as e:
                        st.error(f"Eroare la procesarea AI: {e}")

    st.write("")

    if st.session_state.ai_parsed_data is not None:
        parsed = st.session_state.ai_parsed_data

        with st.container(border=True):
            st.markdown("#### ✏️ 2. Verifică datele extrase și deduse de AI")
            st.info("AI-ul a adăugat automat și competențele conexe (ex: IntelliJ ➜ Java). Poți edita oricare dintre câmpuri.")

            edit_nume = st.text_input("Nume complet", value=parsed.get("nume", ""), key="ai_nume")
            edit_exp = st.number_input("Ani de experiență estimați de AI", min_value=0, max_value=50, value=int(parsed.get("experienta_ani", 0)), key="ai_exp")

            default_hard = ", ".join(parsed.get("hard_skills", []))
            edit_hard = st.text_area(
                "Competențe Tehnice (Hard Skills) — separate prin virgulă",
                value=default_hard, height=120, key="ai_hard",
            )

            default_soft = ", ".join(parsed.get("soft_skills", []))
            edit_soft = st.text_area(
                "Abilități Personale (Soft Skills) — separate prin virgulă",
                value=default_soft, height=90, key="ai_soft",
            )

            st.write("")
            if st.button("💾 Salvează Profilul și Generează Recomandările", type="primary",
                         use_container_width=True, key="ai_save"):
                final_hard = [s.strip() for s in edit_hard.split(",") if s.strip()]
                final_soft = [s.strip() for s in edit_soft.split(",") if s.strip()]
                _finalize_and_go(
                    edit_nume,
                    final_hard,
                    final_soft,
                    extra={"experience_years": int(edit_exp)}
                )

# =====================================================================
# FLUX B — NU AM UN CV (FORMULAR MANUAL)
# =====================================================================
elif choice == "✍️ Nu, vreau să-l creez acum":

    with st.container(border=True):
        st.markdown('<p class="sj-flow-heading">👤 Date personale</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            m_nume = st.text_input("Nume complet", key="manual_nume", placeholder="Popescu Ion")
        with c2:
            m_experienta = st.number_input(
                "Ani de experiență", min_value=0, max_value=50, step=1, key="manual_experienta"
            )

        m_educatie = st.text_input(
            "Educație", key="manual_educatie",
            placeholder="ex: Licență Inginerie, Universitatea Tehnică"
        )

    with st.container(border=True):
        st.markdown('<p class="sj-flow-heading">🛠️ Competențe</p>', unsafe_allow_html=True)

        toate_hard_skills = sorted({s for lst in HARD_SKILLS_BY_DOMAIN.values() for s in lst})
        m_hard_selectate = st.multiselect(
            "Competențe tehnice (Hard Skills) — alege din listă",
            options=toate_hard_skills, key="manual_hard_select",
        )
        m_hard_manual = st.text_input(
            "Alte competențe tehnice (separate prin virgulă)",
            key="manual_hard_extra", placeholder="ex: IntelliJ, Docker, React"
        )

        m_soft = st.text_area(
            "Abilități personale (Soft Skills) — separate prin virgulă",
            key="manual_soft", height=90,
            placeholder="ex: comunicare, lucru în echipă",
        )

    st.write("")
    if st.button("💾 Salvează Profilul și Generează Recomandările", type="primary",
                 use_container_width=True, key="manual_save"):
        if not m_nume.strip():
            st.error("Te rugăm să completezi cel puțin numele complet.")
        else:
            extra_hard = [s.strip() for s in m_hard_manual.split(",") if s.strip()]
            final_hard = list(dict.fromkeys(list(m_hard_selectate) + extra_hard))
            final_soft = [s.strip() for s in m_soft.split(",") if s.strip()]

            _finalize_and_go(
                m_nume,
                final_hard,
                final_soft,
                extra={"education": m_educatie, "experience_years": int(m_experienta)},
            )

else:
    st.info("👆 Alege o opțiune mai sus pentru a continua.")

st.markdown("</div>", unsafe_allow_html=True)