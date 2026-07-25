"""
roadmap_mermaid.py
-------------------
Generează și randează un roadmap interactiv, stil roadmap.sh, pornind de la
lista plată de hard-skills (și opțional soft-skills) primită din baza ESCO.
Include evidențierea competențelor pe care utilizatorul le deține deja (Skill Tree logic)
și ordonarea reală ESCO.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Config vizual (culori de brand, aliniate cu restul aplicației)
# ---------------------------------------------------------------------------
COLOR_MOSS = "#2F6F5E"
COLOR_BRASS = "#C99A56"
COLOR_WHITE = "#FFFFFF"
COLOR_GRAY_BORDER = "#D8DEE7"
COLOR_TEXT = "#1B2430"
COLOR_SOFT_BORDER = "#93691E"
COLOR_OWNED = "#E8F5E9"  # NOU: Verde deschis pentru skill-urile deținute
COLOR_OWNED_BORDER = "#2E7D32"

TIER_LABELS = ["Fundamente", "Intermediar", "Avansat", "Specializări"]
TIER_ICONS = ["🧱", "⚙️", "🚀", "🎯"]
TIER_COLORS = [COLOR_MOSS, COLOR_BRASS, COLOR_MOSS, COLOR_BRASS]

MAX_BRANCH_PER_TIER = 6


# ---------------------------------------------------------------------------
# Utilitare interne
# ---------------------------------------------------------------------------
def _sanitize_label(text: str, max_len: int = 42) -> str:
    """Curăță un text pentru a putea fi folosit în siguranță ca label Mermaid."""
    text = str(text).strip().replace("\n", " ")
    text = text.replace('"', "'").replace("`", "'")
    text = text.replace("[", "(").replace("]", ")")
    text = text.replace("{", "(").replace("}", ")")
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def _split_into_tiers(items: List[str], n_tiers: int) -> List[List[str]]:
    if not items:
        return [[] for _ in range(n_tiers)]

    n_tiers = max(1, n_tiers)
    chunk = max(1, -(-len(items) // n_tiers))  # ceil division
    tiers = [items[i:i + chunk] for i in range(0, len(items), chunk)]

    while len(tiers) > n_tiers:
        tail = tiers.pop()
        tiers[-1].extend(tail)

    while len(tiers) < n_tiers:
        tiers.append([])

    return tiers

# NOU: Funcție de tăiere bazată pe datele reale (essential vs optional)
def _split_into_tiers_by_relation(items: List[str], relations: dict, n_tiers: int = 4) -> List[List[str]]:
    if not items: return [[] for _ in range(n_tiers)]

    essentials = [s for s in items if relations.get(s, '').lower() == 'essential']
    optionals = [s for s in items if relations.get(s, '').lower() != 'essential']

    if not essentials:
        essentials = items[:len(items)//2]
        optionals = items[len(items)//2:]

    t_ess = max(1, n_tiers // 2)
    t_opt = n_tiers - t_ess

    return _split_into_tiers(essentials, t_ess) + _split_into_tiers(optionals, t_opt)

# ---------------------------------------------------------------------------
# Generarea sintaxei Mermaid
# ---------------------------------------------------------------------------
def generate_roadmap_mermaid(
    job_title: str,
    hard_skills: Iterable[str],
    soft_skills: Optional[Iterable[str]] = None,
    skill_relations: dict = None,          # NOU
    user_hard_skills: List[str] = None,    # NOU
    user_soft_skills: List[str] = None,    # NOU
    max_tiers: int = 4,
) -> str:

    hard_skills = [s for s in dict.fromkeys(hard_skills or [])]  # dedup, păstrează ordinea
    soft_skills = [s for s in dict.fromkeys(soft_skills or [])]

    skill_relations = skill_relations or {}
    user_hard = user_hard_skills or []
    user_soft = user_soft_skills or []

    n_tiers = min(max_tiers, max(1, len(hard_skills))) if hard_skills else 0
    # Folosim acum împărțirea deșteaptă ESCO
    tiers = _split_into_tiers_by_relation(hard_skills, skill_relations, n_tiers) if n_tiers else []

    lines: List[str] = ["graph TD"]

    root_id = "root"
    root_label = _sanitize_label(job_title, max_len=48)
    lines.append(f'    {root_id}(["🧭 {root_label}"]):::rootNode')

    core_ids: List[str] = []
    node_counter = 0
    prev_core_id = root_id

    for tier_idx, tier_items in enumerate(tiers):
        if not tier_items:
            continue

        tier_name = TIER_LABELS[tier_idx % len(TIER_LABELS)]
        tier_icon = TIER_ICONS[tier_idx % len(TIER_ICONS)]
        core_class = "coreMoss" if tier_idx % 2 == 0 else "coreBrass"

        core_item = tier_items[0]
        branch_items = tier_items[1:1 + MAX_BRANCH_PER_TIER]
        overflow = len(tier_items) - 1 - len(branch_items)

        core_id = f"tier{tier_idx}_core"

        # NOU: Logica de Highlight pentru Nodul Principal (Core)
        if core_item in user_hard:
            core_label = f"✅ {_sanitize_label(core_item)}"
            lines.append(f'    {core_id}["{tier_icon} {tier_name}: {core_label}"]:::ownedNode')
        else:
            core_label = _sanitize_label(core_item)
            lines.append(f'    {core_id}["{tier_icon} {tier_name}: {core_label}"]:::{core_class}')

        lines.append(f"    {prev_core_id} --> {core_id}")
        core_ids.append(core_id)
        prev_core_id = core_id

        for b_item in branch_items:
            node_counter += 1
            b_id = f"tier{tier_idx}_b{node_counter}"

            # NOU: Logica de Highlight pentru Ramificații
            if b_item in user_hard:
                lines.append(f'    {b_id}("✅ {_sanitize_label(b_item)}"):::ownedNode')
            else:
                lines.append(f'    {b_id}("{_sanitize_label(b_item)}"):::branchNode')
            lines.append(f"    {core_id} -.- {b_id}")

        if overflow > 0:
            node_counter += 1
            more_id = f"tier{tier_idx}_more{node_counter}"
            lines.append(f'    {more_id}("+{overflow} alte competențe"):::moreNode')
            lines.append(f"    {core_id} -.- {more_id}")

    # Ramura de Soft Skills, atașată la finalul traseului principal
    if soft_skills:
        soft_root_id = "soft_root"
        lines.append(f'    {soft_root_id}["🤝 Soft Skills"]:::softHeader')
        lines.append(f"    {prev_core_id} --> {soft_root_id}")
        for i, s_item in enumerate(soft_skills[:MAX_BRANCH_PER_TIER]):
            s_id = f"soft_{i}"

            # NOU: Logica de Highlight pentru Soft Skills
            if s_item in user_soft:
                lines.append(f'    {s_id}("✅ {_sanitize_label(s_item)}"):::ownedNode')
            else:
                lines.append(f'    {s_id}("{_sanitize_label(s_item)}"):::softNode')
            lines.append(f"    {soft_root_id} -.- {s_id}")

        remaining_soft = len(soft_skills) - MAX_BRANCH_PER_TIER
        if remaining_soft > 0:
            lines.append(f'    soft_more("+{remaining_soft} alte soft skills"):::softNode')
            lines.append(f"    {soft_root_id} -.- soft_more")

    # --- classDef-uri de stil (culori brand, ca pe roadmap.sh) ---
    lines.append(f"    classDef rootNode fill:{COLOR_TEXT},stroke:{COLOR_TEXT},color:#ffffff,stroke-width:2px,font-weight:700;")
    lines.append(f"    classDef coreMoss fill:{COLOR_MOSS},stroke:{COLOR_MOSS},color:#ffffff,stroke-width:2px,font-weight:700;")
    lines.append(f"    classDef coreBrass fill:{COLOR_BRASS},stroke:{COLOR_BRASS},color:#ffffff,stroke-width:2px,font-weight:700;")
    lines.append(f"    classDef branchNode fill:{COLOR_WHITE},stroke:{COLOR_GRAY_BORDER},color:{COLOR_TEXT},stroke-width:1.5px;")
    lines.append(f"    classDef moreNode fill:#F6F7F9,stroke:{COLOR_GRAY_BORDER},color:#8A93A3,stroke-width:1px,stroke-dasharray: 3 3;")
    lines.append(f"    classDef softHeader fill:#FFF7EA,stroke:{COLOR_BRASS},color:{COLOR_SOFT_BORDER},stroke-width:2px,font-weight:700;")
    lines.append(f"    classDef softNode fill:#FFFDF8,stroke:{COLOR_BRASS},color:{COLOR_SOFT_BORDER},stroke-width:1px,stroke-dasharray: 4 3;")
    # NOU: Clasa pentru progres
    lines.append(f"    classDef ownedNode fill:{COLOR_OWNED},stroke:{COLOR_OWNED_BORDER},color:{COLOR_OWNED_BORDER},stroke-width:2px,font-weight:700;")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Randare în Streamlit (Mermaid.js prin components.html)
# ---------------------------------------------------------------------------
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body { margin:0; padding:0; background:transparent; font-family:'Inter', sans-serif; overflow: hidden; }

  .sj-mermaid-scroll {
    overflow: auto;
    width: 100%;
    height: 100vh;
    padding: 30px 20px 80px 20px;
    cursor: grab;
    box-sizing: border-box;
  }

  .mermaid { 
    display: flex; 
    justify-content: center; 
    margin: 0 auto;
    min-width: 100%;
    width: max-content; 
  }

  .mermaid svg {
    max-width: none !important;
    height: auto !important;
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .zoom-panel {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #ffffff;
    border: 1px solid #ECEFF3;
    border-radius: 10px;
    box-shadow: 0 8px 24px rgba(16,24,40,0.12);
    display: flex;
    padding: 6px;
    gap: 6px;
    z-index: 1000;
  }

  .zoom-panel button {
    background: #F1F3F6; border: none; border-radius: 6px;
    width: 36px; height: 36px; font-size: 18px; cursor: pointer;
    color: #1B2430; font-weight: bold; display: flex; align-items: center; justify-content: center;
    transition: background 0.2s;
  }
  .zoom-panel button:hover { background: #E3E7ED; }
  .zoom-panel span {
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; width: 45px; color: #5B6472;
  }
</style>
</head>
<body>

  <div class="zoom-panel">
    <button onclick="zoom(-0.2)" title="Micșorează">-</button>
    <span id="zoomLabel">100%</span>
    <button onclick="zoom(0.2)" title="Mărește">+</button>
    <button onclick="resetZoom()" title="Resetează" style="font-size:12px; width:auto; padding:0 12px;">Reset</button>
  </div>

  <div class="sj-mermaid-scroll" id="scrollShell">
    <div class="mermaid" id="sjMermaidGraph">__GRAPH_DEFINITION__</div>
  </div>

  <script>
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      securityLevel: 'loose',
      themeVariables: {
        fontFamily: 'Inter, sans-serif',
        primaryColor: '__COLOR_MOSS__',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '__COLOR_MOSS__',
        lineColor: '__COLOR_BRASS__',
        secondaryColor: '#ffffff'
      },
      flowchart: { curve: 'basis', nodeSpacing: 40, rankSpacing: 70 }
    });

    mermaid.run({ querySelector: '#sjMermaidGraph' }).then(() => {
        setTimeout(updateZoomUI, 50);
    });

    let currentScale = 1.0;
    const minScale = 0.4;
    const maxScale = 4.0;
    let baseWidth = 0; 

    function updateZoomUI() {
      document.getElementById('zoomLabel').innerText = Math.round(currentScale * 100) + '%';
      const svg = document.querySelector('.mermaid svg');
      if (svg) {
         svg.style.maxWidth = 'none'; 

         if (baseWidth === 0) {
             const viewBox = svg.getAttribute('viewBox');
             if (viewBox) {
                 const parts = viewBox.split(' '); 
                 baseWidth = Math.max(parseFloat(parts[2]), 1200); 
             } else {
                 baseWidth = 1200;
             }
         }

         svg.style.width = (baseWidth * currentScale) + 'px';
         svg.style.height = 'auto'; 
      }
    }

    window.zoom = function(delta) {
      currentScale += delta;
      if (currentScale < minScale) currentScale = minScale;
      if (currentScale > maxScale) currentScale = maxScale;
      updateZoomUI();
    };

    window.resetZoom = function() {
      currentScale = 1.0;
      updateZoomUI();
    };

    const shell = document.getElementById('scrollShell');
    let isDown = false, startX, scrollLeft, startY, scrollTop;

    shell.addEventListener('mousedown', (e) => {
      isDown = true; shell.style.cursor = 'grabbing';
      startX = e.pageX - shell.offsetLeft; scrollLeft = shell.scrollLeft;
      startY = e.pageY - shell.offsetTop; scrollTop = shell.scrollTop;
    });
    ['mouseleave', 'mouseup'].forEach(evt =>
      shell.addEventListener(evt, () => { isDown = false; shell.style.cursor = 'grab'; })
    );
    shell.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - shell.offsetLeft;
      const y = e.pageY - shell.offsetTop;
      shell.scrollLeft = scrollLeft - (x - startX) * 1.5;
      shell.scrollTop = scrollTop - (y - startY) * 1.5;
    });
  </script>
</body>
</html>
"""


def render_mermaid_roadmap(mermaid_code: str, height: int = 720) -> None:
    """Randează codul Mermaid dat într-un component HTML izolat (iframe)."""
    html = (
        _HTML_TEMPLATE
        .replace("__GRAPH_DEFINITION__", mermaid_code)
        .replace("__COLOR_MOSS__", COLOR_MOSS)
        .replace("__COLOR_BRASS__", COLOR_BRASS)
    )
    components.html(html, height=height, scrolling=True)


def render_roadmap_legend() -> None:
    """Mic legendă sub diagramă, explicând codul de culori (ca pe roadmap.sh)."""
    import streamlit as st

    st.markdown(
        f"""
<div style="display:flex; gap:1.4rem; flex-wrap:wrap; margin-top:0.6rem; font-size:0.82rem; color:{COLOR_TEXT};">
  <div style="display:flex; align-items:center; gap:0.4rem;">
    <span style="width:14px; height:14px; border-radius:4px; background:{COLOR_MOSS}; display:inline-block;"></span>
    Traseu principal — Fundamente / Avansat
  </div>
  <div style="display:flex; align-items:center; gap:0.4rem;">
    <span style="width:14px; height:14px; border-radius:4px; background:{COLOR_BRASS}; display:inline-block;"></span>
    Traseu principal — Intermediar / Specializări
  </div>
  <div style="display:flex; align-items:center; gap:0.4rem;">
    <span style="width:14px; height:14px; border-radius:4px; background:#fff; border:1.5px solid {COLOR_GRAY_BORDER}; display:inline-block;"></span>
    Competențe secundare (ramificații)
  </div>
  <div style="display:flex; align-items:center; gap:0.4rem;">
    <span style="width:14px; height:14px; border-radius:4px; background:#FFFDF8; border:1px dashed {COLOR_BRASS}; display:inline-block;"></span>
    Soft skills
  </div>
  <!-- NOU: Adăugat în legendă -->
  <div style="display:flex; align-items:center; gap:0.4rem;">
    <span style="width:14px; height:14px; border-radius:4px; background:{COLOR_OWNED}; border:1.5px solid {COLOR_OWNED_BORDER}; display:inline-block;"></span>
    ✅ Competențe deținute
  </div>
</div>
""",
        unsafe_allow_html=True,
    )