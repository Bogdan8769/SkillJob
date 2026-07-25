"""
components.py
-------------
Componente de UI reutilizabile, separate de logica paginilor. Fiecare
funcție randează direct în Streamlit (prin st.markdown / st.components.v1.html)
și nu conține logică de business — primește date deja calculate.
"""

import streamlit as st
import streamlit.components.v1 as components

from state import WIZARD_STEPS

# ---------------------------------------------------------------------------
# Step indicator pentru wizard-ul de profilare
# ---------------------------------------------------------------------------
def render_step_indicator(current_step: int):
    parts = ['<div class="sj-steps">']
    total = len(WIZARD_STEPS)
    for i, label in enumerate(WIZARD_STEPS, start=1):
        state_cls = "done" if i < current_step else ("active" if i == current_step else "")
        icon_or_num = "✓" if i < current_step else i
        parts.append(
            f'<div class="sj-step {state_cls}">'
            f'<div class="sj-step-circle">{icon_or_num}</div>'
            f'<div class="sj-step-label">{label}</div>'
            f'</div>'
        )
        if i < total:
            line_cls = "done" if i < current_step else ""
            parts.append(f'<div class="sj-step-line {line_cls}"></div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Card mare pentru alegerea domeniului (Pasul 1 al wizard-ului)
# ---------------------------------------------------------------------------
def render_domain_card(domain_name: str, meta: dict, selected: bool):
    sel_cls = "selected" if selected else ""
    # Folosim get() pentru siguranță în cazul în care meta-datele lipsesc
    image_url = meta.get("image", "")
    icon = meta.get("icon", "🔹")
    desc = meta.get("description", "")

    st.markdown(
        f'''<div class="sj-domaincard {sel_cls}" style="background-image:url('{image_url}');">
            <div class="sj-domaincard-overlay">
                <p class="sj-domaincard-title">{icon} {domain_name}</p>
                <p class="sj-domaincard-sub">{desc}</p>
            </div>
        </div>''', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Card pentru explorarea categoriilor (Dashboard / Categorii)
# ---------------------------------------------------------------------------
def render_category_card(domain_name: str, meta: dict, job_count: int):
    image_url = meta.get("image", "")
    icon = meta.get("icon", "🔹")

    st.markdown(
        f'''<div class="sj-catcard" style="background-image:url('{image_url}');">
            <div class="sj-catcard-overlay">
                <div class="sj-catcard-eyebrow">Categorie</div>
                <p class="sj-catcard-title">{icon} {domain_name}</p>
                <p class="sj-catcard-count">{job_count} ocupații disponibile</p>
            </div>
        </div>''', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Card de recomandare (afișat pe pagina de Recomandări)
# ---------------------------------------------------------------------------
def render_recommendation_card(rec: dict):
    hard_html = "".join(f'<span class="sj-tag matched">{s}</span>' for s in rec["matched_hard"]) \
                or '<span class="sj-tag">—</span>'

    soft_skills = rec.get("matched_soft", [])
    if soft_skills:
        soft_html = "".join(f'<span class="sj-tag soft">{s}</span>' for s in soft_skills)
        soft_section = f'<div class="sj-skillgroup-label" style="margin-top: 1rem;">Soft skills potrivite</div><div>{soft_html}</div>'
    else:
        soft_section = ""

    # ATENȚIE: Nu indenta codul HTML de mai jos! Trebuie să stea lipit de marginea stângă
    # pentru ca Streamlit să nu îl transforme într-un bloc de cod Markdown.
    html_content = f"""
<div class="sj-reccard">
    <div class="sj-reccard-top">
        <div>
            <p class="sj-reccard-title">{rec.get("job", "Job")}</p>
            <p class="sj-reccard-cat">{rec.get("domain", "")} &middot; {rec.get("description", "")}</p>
        </div>
        <span class="sj-matchpill">{rec.get("match_pct", 0)}% potrivire</span>
    </div>
    <div class="sj-skillgroup-label" style="margin-top: 1rem;">Hard skills potrivite</div>
    <div>{hard_html}</div>
    {soft_section}
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Roadmap premium, randat izolat printr-un component HTML (iframe).
# Inspirat vizual din roadmap.sh: 3 coloane (Baze / Intermediar / Avansat)
# conectate prin curbe SVG, fiecare coloană cu propriul "spine" vertical.
# ---------------------------------------------------------------------------
def render_roadmap_component(job_name: str, tiers: dict):
    tier_names = list(tiers.keys())  # ["Baze", "Intermediar", "Avansat"]

    col_width = 260
    col_gap = 70
    col_x = [40 + i * (col_width + col_gap) for i in range(len(tier_names))]

    # Evităm IndexError dacă nu există date în 'tiers'
    if not col_x:
        st.info("Nu există date pentru roadmap în acest moment.")
        return

    total_width = col_x[-1] + col_width + 40

    header_h = 56
    header_y = 34
    node_h = 58
    node_gap = 16
    node_start_offset = 34

    max_nodes = max([len(v) for v in tiers.values()] or [0])
    total_height = header_y + header_h + node_start_offset + max_nodes * (node_h + node_gap) + 60

    # --- construim conectorii SVG între headerele coloanelor ---
    connectors = []
    for i in range(len(tier_names) - 1):
        x1 = col_x[i] + col_width
        y1 = header_y + header_h / 2
        x2 = col_x[i + 1]
        y2 = header_y + header_h / 2
        mx = (x1 + x2) / 2
        connectors.append(
            f'<path d="M {x1} {y1} C {mx} {y1}, {mx} {y2}, {x2} {y2}" '
            f'stroke="url(#sj-grad)" stroke-width="3" fill="none" stroke-linecap="round"/>'
        )

    # --- construim coloanele (header + noduri + linie verticală proprie) ---
    columns_html = []
    # Culori Hex extrase din CSS-ul principal (Brass, Moss, Custom Darker Brass)
    tier_colors = ["#C99A56", "#2F6F5E", "#B37D2A"]

    for i, tier_name in enumerate(tier_names):
        x = col_x[i]
        color = tier_colors[i % len(tier_colors)]

        # Header Coloană
        header = (
            f'<rect x="{x}" y="{header_y}" width="{col_width}" height="{header_h}" rx="14" fill="{color}" />'
            f'<text x="{x + col_width/2}" y="{header_y + header_h/2 + 5}" text-anchor="middle" '
            f'font-family="Sora, sans-serif" font-weight="700" font-size="16" fill="#ffffff">{tier_name}</text>'
        )
        columns_html.append(header)

        nodes = tiers[tier_name]
        spine_top = header_y + header_h
        spine_bottom = spine_top + node_start_offset + len(nodes) * (node_h + node_gap) - node_gap

        # Linia punctată verticală (spine)
        if nodes:
            columns_html.append(
                f'<line x1="{x + col_width/2}" y1="{spine_top}" x2="{x + col_width/2}" '
                f'y2="{spine_bottom}" stroke="{color}" stroke-width="2" stroke-dasharray="4,5" opacity="0.5"/>'
            )

        # Randare Noduri
        for j, node in enumerate(nodes):
            ny = spine_top + node_start_offset + j * (node_h + node_gap)
            is_required = node.get("type") == "required"

            fill = "#FFFFFF"
            stroke = color if is_required else "#D8DEE7"
            dash = "" if is_required else 'stroke-dasharray="5,5"'
            badge = "Esențial" if is_required else "Recomandat"
            badge_color = color if is_required else "#5B6472"
            title = node.get("title", "")

            columns_html.append(
                f'<rect x="{x}" y="{ny}" width="{col_width}" height="{node_h}" rx="12" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="2" {dash} '
                f'style="filter:drop-shadow(0 4px 10px rgba(16,24,40,0.10));"/>'
                f'<text x="{x + 16}" y="{ny + 24}" font-family="Inter, sans-serif" font-weight="600" '
                f'font-size="14" fill="#1B2430">{title}</text>'
                f'<text x="{x + 16}" y="{ny + 42}" font-family="Inter, sans-serif" font-weight="700" '
                f'font-size="10" letter-spacing="0.04em" fill="{badge_color}">{badge.upper()}</text>'
            )

    svg_body = "".join(columns_html) + "".join(connectors)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Sora:wght@700&family=Inter:wght@600;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin:0; padding:0; background:transparent; font-family:'Inter', sans-serif; }}
            .sj-roadmap-scroll {{ overflow-x:auto; padding: 10px 0 20px 0; }}
        </style>
    </head>
    <body>
        <div class="sj-roadmap-scroll">
            <svg width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="sj-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#C99A56"/>
                        <stop offset="100%" stop-color="#2F6F5E"/>
                    </linearGradient>
                </defs>
                {svg_body}
            </svg>
        </div>
    </body>
    </html>
    """

    # Folosim height calculat dinamic pentru ca iFrame-ul să nu aibă scroll vertical inutil
    components.html(html, height=int(total_height) + 30, scrolling=True)