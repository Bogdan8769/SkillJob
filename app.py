import streamlit as st
import requests
import bcrypt

st.set_page_config(page_title="SkillJob", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("user_name", "")

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

.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    border-radius: 10px;
    border: 1px solid var(--line);
    padding: 0.55rem 1rem;
    transition: all 0.15s ease;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.stButton > button:hover {
    border-color: var(--moss);
    color: var(--moss);
    box-shadow: 0 4px 14px rgba(47, 111, 94, 0.18);
    transform: translateY(-1px);
}

[data-testid="stFormSubmitButton"] button, [data-testid="stSidebar"] .stButton > button {
    background: var(--moss);
    color: #FFFFFF !important;
    border: none;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: #275c4e;
    box-shadow: 0 6px 18px rgba(47, 111, 94, 0.30);
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(201, 154, 86, 0.12);
    color: #E7ECF3 !important;
    border: 1px solid rgba(201, 154, 86, 0.35);
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201, 154, 86, 0.22);
    color: var(--brass) !important;
    transform: none;
    box-shadow: none;
}

[data-testid="stTextInput"] input, [data-testid="stTextInput"] input:focus {
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
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def login_page():
    st.write("\n\n")
    _, col, _ = st.columns([1.2, 1, 1.2])
    with col:
        st.markdown(
            "<p style='text-align:center; font-size:2.2rem; margin-bottom:0.2rem;'>🧭</p><h1 style='text-align:center; margin-bottom:0.2rem;'>SkillJob</h1><p style='text-align:center; color:#5B6472; margin-bottom:1.6rem;'>Autentifică-te pentru a continua</p>",
            unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown(
                "<p style='font-family:Sora, sans-serif; font-weight:600; font-size:1.05rem; margin-bottom:0.6rem;'>Login</p>",
                unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="nume@exemplu.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            if st.form_submit_button("Log In", use_container_width=True):
                try:
                    db = requests.get(
                        "https://raw.githubusercontent.com/Bogdan8769/SkillJob/refs/heads/main/login_details_app.json").json()
                    if email in db:
                        if bcrypt.checkpw(password.encode('utf-8'), db[email]["hash"].encode('utf-8')):
                            st.session_state.update(logged_in=True, user_name=db[email]["name"])
                            st.rerun()
                        else:
                            st.error("Parolă incorectă.")
                    else:
                        st.error("Email-ul nu a fost găsit.")
                except Exception as e:
                    st.error(f"Eroare la conectarea cu baza de date: {e}")
        st.markdown(
            "<p style='text-align:center; color:#5B6472; font-size:0.8rem; margin-top:1.2rem;'>Nu ai cont? Contactează administratorul platformei.</p>",
            unsafe_allow_html=True)


def main_page():
    with st.sidebar:
        st.title("🧭 SkillJob")
        st.markdown("---")
        with st.expander("💼 Ocupații"): st.write("Opțiuni în curând...")
        with st.expander("🎯 Skill-uri"): st.write("Opțiuni în curând...")
        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)

        initials = "".join([p[0].upper() for p in st.session_state.user_name.split()][:2]) or "U"
        st.markdown(
            f'<div class="sj-badge"><div class="sj-badge-avatar">{initials}</div><div><div class="sj-badge-name">{st.session_state.user_name}</div><div class="sj-badge-role">Cont conectat</div></div></div>',
            unsafe_allow_html=True)

        if st.button("Log Out", key="logout_btn", use_container_width=True):
            st.session_state.update(logged_in=False, user_name="")
            st.rerun()

    fname = st.session_state.user_name.split()[0] if st.session_state.user_name else ""
    st.markdown(
        f'<div class="sj-topbar"><div><p class="sj-eyebrow">Dashboard</p><h2 class="sj-title">Salut, {fname} 👋</h2><p class="sj-subtitle">Iată o privire de ansamblu asupra platformei SkillJob.</p></div></div>',
        unsafe_allow_html=True)

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="sj-search">', unsafe_allow_html=True)
        search_query = st.text_input("Search", placeholder="Caută ocupații, skill-uri sau job-uri...",
                                     label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    stats = [("💼", "128", "Ocupații listate"), ("🎯", "342", "Skill-uri catalogate"), ("📌", "27", "Job-uri active azi")]
    for col, (icon, num, lbl) in zip(st.columns(3), stats):
        col.markdown(
            f'<div class="sj-stat"><div class="sj-stat-icon">{icon}</div><div><div class="sj-stat-number">{num}</div><div class="sj-stat-label">{lbl}</div></div></div>',
            unsafe_allow_html=True)

    st.write("")

    if search_query:
        st.info(f"Rezultatele căutării pentru: **{search_query}** vor fi afișate aici.")
    else:
        tags_html = "".join([f'<span class="sj-tag">{t}</span>' for t in
                             ["Programare", "Design UI/UX", "Marketing", "Vânzări", "Contabilitate", "Resurse Umane"]])
        st.markdown('<p class="sj-section-title">Categorii populare</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sj-card"><div>{tags_html}</div><p style="color:#5B6472; margin-top:1rem; margin-bottom:0;">Selectează o categorie sau folosește bara de căutare de mai sus pentru a găsi ocupații, skill-uri sau job-uri relevante pentru tine.</p></div>',
            unsafe_allow_html=True)


if st.session_state.logged_in:
    main_page()
else:
    login_page()
