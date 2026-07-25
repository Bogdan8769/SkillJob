"""
styles.py
---------
Toată logica de stilizare a aplicației, separată de UI și de date.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
    --ink: #131A24;
    --ink-2: #1E2A3C;
    --paper: #F3F5F8;
    --card: #FFFFFF;
    --line: #E4E8EE;
    --moss: #2F6F5E;
    --moss-soft: #E4F0EC;
    --brass: #C99A56;
    --text: #1B2430;
    --text-soft: #5B6472;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--paper);
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text);
    letter-spacing: -0.01em;
}

[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 2.6rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

#MainMenu, footer, header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--ink) 0%, var(--ink-2) 100%);
    border-right: none;
}

[data-testid="stSidebar"] * {
    color: #E7ECF3 !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

[data-testid="stSidebar"] h1 {
    font-family: 'Sora', sans-serif !important;
    font-weight: 700;
    font-size: 1.5rem;
    letter-spacing: 0.02em;
}

[data-testid="stSidebar"] hr {
    border: none;
    border-top: 1px solid rgba(231, 236, 243, 0.12);
    margin: 1rem 0;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(231, 236, 243, 0.10);
    border-left: 3px solid var(--brass);
    border-radius: 10px;
    margin-bottom: 0.6rem;
    overflow: hidden;
    transition: background 0.15s ease;
}

[data-testid="stSidebar"] [data-testid="stExpander"]:hover {
    background: rgba(255, 255, 255, 0.07);
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0.4rem 0.2rem;
}

.sidebar-spacer { flex-grow: 1; }

/* ASCUNDE MENIUL DEFAULT AL STREAMLIT (Rezolvare poza 4) */
[data-testid="stSidebarNav"] {
    display: none !important;
}

.sj-badge {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(201, 154, 86, 0.35);
    border-radius: 12px;
    padding: 0.65rem 0.8rem;
    margin-bottom: 0.7rem;
}

.sj-badge-avatar {
    flex-shrink: 0;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--brass), #a9793c);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--ink) !important;
}

.sj-badge-name {
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    line-height: 1.1;
}

.sj-badge-role {
    font-size: 0.72rem;
    color: rgba(231, 236, 243, 0.6) !important;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

/* REPARARE BUTOANE (Contrast + Vizibilitate text) */
.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    border-radius: 10px;
    border: 1px solid var(--line);
    padding: 0.55rem 1rem;
    background-color: var(--card) !important; /* Forțează fundal alb/luminos */
    color: var(--text) !important; /* Forțează text închis la culoare */
    transition: all 0.15s ease;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.stButton > button:hover {
    border-color: var(--moss) !important;
    color: var(--moss) !important;
    box-shadow: 0 4px 14px rgba(47, 111, 94, 0.18);
    transform: translateY(-1px);
}

[data-testid="stFormSubmitButton"] button, [data-testid="stSidebar"] .stButton > button {
    background: var(--moss) !important;
    color: #FFFFFF !important;
    border: none;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: #275c4e !important;
    box-shadow: 0 6px 18px rgba(47, 111, 94, 0.30);
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(201, 154, 86, 0.12) !important;
    color: #E7ECF3 !important;
    border: 1px solid rgba(201, 154, 86, 0.35) !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201, 154, 86, 0.22) !important;
    color: var(--brass) !important;
    transform: none;
    box-shadow: none;
}

[data-testid="stTextInput"] input, [data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea, [data-testid="stTextArea"] textarea:focus {
    border-radius: 10px;
    border: 1px solid var(--line);
    padding: 0.6rem 0.9rem;
    font-family: 'Inter', sans-serif;
    background: var(--card) !important;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    caret-color: var(--text) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.stButton button[kind="primary"] {
    background: var(--moss) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: var(--text-soft) !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: var(--moss);
    box-shadow: 0 0 0 3px var(--moss-soft);
}

input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus {
    -webkit-text-fill-color: var(--text) !important;
    -webkit-box-shadow: 0 0 0px 1000px #FFFFFF inset !important;
    transition: background-color 5000s ease-in-out 0s;
}

[data-testid="stForm"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 2.2rem 2.2rem 1.6rem 2.2rem;
    box-shadow: 0 12px 32px rgba(16, 24, 40, 0.08);
}

.sj-search [data-testid="stTextInput"] input {
    border-radius: 999px;
    padding: 0.8rem 1.5rem 0.8rem 3rem;
    font-size: 1rem;
    box-shadow: 0 6px 20px rgba(16, 24, 40, 0.06);
}

.sj-search {
    position: relative;
}

.sj-search::before {
    content: "🔍";
    position: absolute;
    left: 1.1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.95rem;
    z-index: 2;
    opacity: 0.55;
}

[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid var(--line);
}

.sj-topbar {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 1.6rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.sj-eyebrow {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--moss);
    margin: 0 0 0.2rem 0;
}

.sj-title {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.7rem;
    margin: 0;
}

.sj-subtitle {
    color: var(--text-soft);
    font-size: 0.95rem;
    margin: 0.15rem 0 0 0;
}

.sj-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.6rem;
    box-shadow: 0 4px 16px rgba(16, 24, 40, 0.05);
}

.sj-stat {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 4px 14px rgba(16, 24, 40, 0.04);
    display: flex;
    align-items: center;
    gap: 0.9rem;
    transition: transform 0.15s ease;
}

.sj-stat:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(16, 24, 40, 0.09);
}

.sj-stat-icon {
    flex-shrink: 0;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    background: var(--moss-soft);
}

.sj-stat-number {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    line-height: 1.1;
    color: var(--text);
}

.sj-stat-label {
    font-size: 0.78rem;
    color: var(--text-soft);
    letter-spacing: 0.02em;
}

.sj-section-title {
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    margin: 2rem 0 0.8rem 0;
    color: var(--text);
}

.sj-tag {
    display: inline-block;
    background: var(--moss-soft);
    color: var(--moss);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    margin: 0 0.4rem 0.4rem 0;
}
/* REPARARE VIZIBILITATE ETICHETE (Labels) PENTRU INPUT-URI ȘI SLIDERE */
[data-testid="stWidgetLabel"] p, 
[data-testid="stWidgetLabel"] span {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    visibility: visible !important;
}

/* Stil extra pentru a face textele explicite la slidere să iasă în evidență */
.stSlider [data-testid="stTickBar"] {
    color: var(--text-soft) !important;
}
/* =========================================================
   OVERHAUL DESIGN: MULTISELECT & RADIO (Tip SaaS Premium)
   ========================================================= */

/* 1. Caseta principală de input (Multiselect & Selectbox) */
[data-testid="stMultiSelect"] > div > div, 
[data-testid="stSelectbox"] > div > div {
    background-color: var(--card) !important;
    border: 2px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 0.3rem 0.6rem !important;
    box-shadow: 0 4px 10px rgba(16, 24, 40, 0.02) !important;
    transition: all 0.3s ease !important;
}

/* Efectul de Focus/Hover (Inel de selecție verde) */
[data-testid="stMultiSelect"] > div > div:hover,
[data-testid="stSelectbox"] > div > div:hover,
[data-testid="stMultiSelect"] > div > div:focus-within,
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--moss) !important;
    box-shadow: 0 0 0 4px var(--moss-soft) !important;
}

/* 2. Etichetele (Tags / Chips) din interiorul Multiselect-ului */
/* Scăpăm de roșul default și punem culoarea brandului */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: var(--moss) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border: none !important;
}

/* Butonul de "X" de pe tag */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {
    fill: #FFFFFF !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"]:hover {
    background-color: #275c4e !important;
}

/* 3. Transformăm Radio Butoanele în "Pastile" (Segmented Control) */
[data-testid="stRadio"] > div {
    gap: 0.6rem !important;
    flex-wrap: wrap !important;
}

[data-testid="stRadio"] label {
    background-color: var(--card) !important;
    border: 2px solid var(--line) !important;
    border-radius: 999px !important; /* Le facem perfect rotunde la capete */
    padding: 0.6rem 1.4rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(16, 24, 40, 0.02) !important;
}

/* Ascundem bulina nativă (cercul) de radio */
[data-testid="stRadio"] label [data-baseweb="radio"] > div:first-child {
    display: none !important; 
}

/* Stilul textului din noul buton */
[data-testid="stRadio"] label div {
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: var(--text-soft) !important;
}

/* Hover pe pastilă */
[data-testid="stRadio"] label:hover {
    border-color: var(--brass) !important;
    background-color: rgba(201,154,86, 0.05) !important;
    transform: translateY(-1px);
}

/* Când Pastila este SELECTATĂ */
[data-testid="stRadio"] label:has(input:checked) {
    background-color: var(--moss) !important;
    border-color: var(--moss) !important;
    box-shadow: 0 6px 14px rgba(47, 111, 94, 0.25) !important;
}
[data-testid="stRadio"] label:has(input:checked) div {
    color: #FFFFFF !important;
}

/* 4. Meniul Dropdown (Lista cu opțiuni) */
ul[data-baseweb="menu"] {
    border-radius: 12px !important;
    border: 1px solid var(--line) !important;
    box-shadow: 0 10px 30px rgba(16, 24, 40, 0.1) !important;
    overflow: hidden !important;
}
ul[data-baseweb="menu"] li {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 1.2rem !important;
}
ul[data-baseweb="menu"] li:hover {
    background-color: var(--moss-soft) !important;
    color: var(--moss) !important;
    font-weight: 600 !important;
}
</style>
"""

EXTRA_CSS = """
<style>
/* ---------- Step indicator (wizard) ---------- */
.sj-steps {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
    gap: 0;
}
.sj-step {
    display: flex;
    align-items: center;
    flex: 1;
}
.sj-step-circle {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
    border: 2px solid var(--line);
    background: var(--card);
    color: var(--text-soft);
    transition: all 0.2s ease;
}
.sj-step.done .sj-step-circle { 
    background: var(--moss); 
    border-color: var(--moss); 
    color: #fff; 
}
.sj-step.active .sj-step-circle { 
    background: var(--brass); 
    border-color: var(--brass); 
    color: var(--ink);
    box-shadow: 0 0 0 4px rgba(201,154,86,0.22); 
}
.sj-step-label {
    margin-left: 0.55rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-soft);
    white-space: nowrap;
}
.sj-step.active .sj-step-label, .sj-step.done .sj-step-label { 
    color: var(--text); 
}
.sj-step-line { flex: 1; height: 2px; background: var(--line); margin: 0 0.7rem; }
.sj-step-line.done { background: var(--moss); }

/* ---------- Wizard shell ---------- */
.sj-wizard-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 2rem 2.2rem;
    box-shadow: 0 12px 32px rgba(16,24,40,0.08);
    margin-bottom: 1.2rem;
}
.sj-wizard-heading {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    margin: 0 0 0.2rem 0;
}
.sj-wizard-sub { color: var(--text-soft); font-size: 0.88rem; margin: 0 0 1.3rem 0; }

.sj-domain-pill {
    display:inline-block;
    background: var(--moss-soft);
    color: var(--moss);
    font-weight: 700;
    font-size: 0.78rem;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 0.9rem;
}

/* ---------- Domain choice cards (step 1) ---------- */
.sj-domaingrid { display:grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
@media (max-width: 1000px) { .sj-domaingrid { grid-template-columns: repeat(2, 1fr); } }
.sj-domaincard {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    height: 140px;
    background-size: cover;
    background-position: center;
    border: 2px solid transparent;
    cursor: pointer;
    box-shadow: 0 8px 22px rgba(16,24,40,0.12);
}
.sj-domaincard.selected { border-color: var(--brass); }
.sj-domaincard-overlay {
    position:absolute; inset:0;
    background: linear-gradient(180deg, rgba(19,26,36,0.15) 0%, rgba(19,26,36,0.88) 100%);
    display:flex; flex-direction:column; justify-content:flex-end;
    padding: 0.85rem 1rem;
}
.sj-domaincard-title { font-family:'Sora',sans-serif; font-weight:700; color:#fff; font-size:1.05rem; margin:0; }
.sj-domaincard-sub { color: rgba(255,255,255,0.7); font-size:0.72rem; margin-top:0.1rem; }

/* ---------- Category explore cards (reuse domain images) ---------- */
.sj-catgrid { display:grid; grid-template-columns: repeat(2, 1fr); gap: 1.3rem; margin-top: 0.6rem; }
@media (max-width: 900px) { .sj-catgrid { grid-template-columns: 1fr; } }
.sj-catcard {
    position: relative; border-radius: 18px; overflow: hidden; height: 190px;
    background-size: cover; background-position: center;
    box-shadow: 0 10px 28px rgba(16,24,40,0.14);
    border: 1px solid var(--line);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.sj-catcard:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(16,24,40,0.20); }
.sj-catcard-overlay {
    position:absolute; inset:0;
    background: linear-gradient(180deg, rgba(19,26,36,0.10) 0%, rgba(19,26,36,0.85) 100%);
    display:flex; flex-direction:column; justify-content:flex-end;
    padding: 1.1rem 1.2rem;
}
.sj-catcard-eyebrow { color: var(--brass); font-size:0.68rem; font-weight:700; letter-spacing:0.09em; text-transform:uppercase; margin-bottom:0.2rem; }
.sj-catcard-title { font-family:'Sora', sans-serif; font-weight:700; font-size:1.3rem; color:#FFFFFF; margin:0; }
.sj-catcard-count { color: rgba(255,255,255,0.75); font-size:0.78rem; margin-top:0.15rem; }

.sj-joblist-card {
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 1.2rem 1.3rem 1.4rem 1.3rem; box-shadow: 0 4px 16px rgba(16,24,40,0.05); margin-top: 0.7rem;
}
.sj-joblist-title { font-family:'Sora', sans-serif; font-weight:700; font-size:1.05rem; margin-bottom:0.9rem; display:flex; align-items:center; gap:0.5rem; }

/* ---------- Recommendation cards ---------- */
.sj-reccard {
    background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--moss);
    border-radius: 14px; padding: 1.3rem 1.5rem; box-shadow: 0 4px 16px rgba(16,24,40,0.05); margin-bottom: 1rem;
}
.sj-reccard-top { display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap; }
.sj-reccard-title { font-family:'Sora', sans-serif; font-weight:700; font-size:1.15rem; margin:0; }
.sj-reccard-cat { color: var(--text-soft); font-size:0.8rem; margin:0.1rem 0 0.7rem 0; }
.sj-matchpill {
    background: var(--moss-soft); color: var(--moss); font-family:'Sora', sans-serif; font-weight:700;
    font-size:0.85rem; padding: 0.32rem 0.85rem; border-radius: 999px; white-space:nowrap;
}
.sj-reccard-metabar { display:flex; gap:1.4rem; margin: 0.6rem 0 0.8rem 0; flex-wrap: wrap; }
.sj-reccard-meta { font-size:0.78rem; color: var(--text-soft); }
.sj-reccard-meta b { color: var(--text); font-family:'Sora', sans-serif; }
.sj-skillgroup-label { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color: var(--text-soft); margin: 0.5rem 0 0.3rem 0; }
.sj-tag.matched { background: var(--moss); color:#fff; }
.sj-tag.soft { background: rgba(201,154,86,0.16); color: #B37D2A; }

/* ---------- Roadmap component host ---------- */
.sj-roadmap-shell {
    border: 1px solid var(--line);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(16,24,40,0.08);
    background: var(--card);
}
.sj-roadmap-header {
    background: linear-gradient(135deg, var(--ink) 0%, var(--ink-2) 100%);
    border-radius: 16px; padding: 1.6rem 1.8rem; margin-bottom: 1.4rem; color: #FFFFFF;
}
.sj-roadmap-header .sj-eyebrow2 { color: var(--brass); font-size:0.72rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; }
.sj-roadmap-header h2 { color:#FFFFFF !important; margin: 0.2rem 0 0.3rem 0; }
.sj-roadmap-header p { color: rgba(255,255,255,0.72); margin:0; font-size:0.92rem; }
</style>
"""