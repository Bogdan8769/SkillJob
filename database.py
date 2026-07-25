"""
database.py
-----------
Extrage TOATE datele din baza SQLite (ESCO) și le mapează pentru UI.
"""

import sqlite3
import streamlit as st

DB_NAME = "skilljob.db"

# Mapăm vizual cele 10 domenii majore
DOMAIN_META = {
    "Manageri și Directori": {"icon": "👔", "image": "https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=900", "description": "Conducere, strategie și afaceri"},
    "Specialiști și Profesioniști": {"icon": "🎓", "image": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=900", "description": "Educație superioară, IT, Sănătate, Științe"},
    "Tehnicieni și Maiștri": {"icon": "⚙️", "image": "https://images.unsplash.com/photo-1581092160562-40aa08e78837?q=80&w=900", "description": "Suport tehnic, asistență medicală, IT suport"},
    "Funcționari Administrativi": {"icon": "📁", "image": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=900", "description": "Secretariat, contabilitate, administrație"},
    "Servicii și Comerț": {"icon": "🛍️", "image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=900", "description": "Vânzări, HoReCa, îngrijire personală"},
    "Agricultură și Silvicultură": {"icon": "🌱", "image": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=900", "description": "Ferme, agricultură, păduri, pescuit"},
    "Muncitori Calificați și Artizani": {"icon": "🔨", "image": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?q=80&w=900", "description": "Construcții, mecanică, electricitate"},
    "Operatori Mașini și Asamblori": {"icon": "🏭", "image": "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?q=80&w=900", "description": "Linii de producție, fabrici, transport rutier"},
    "Muncitori Necalificați": {"icon": "🧹", "image": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=900", "description": "Munci elementare, curățenie, manipulare marfă"},
    "Forțele Armate": {"icon": "🛡️", "image": "https://images.unsplash.com/photo-1518544866330-8041539bd4cc?q=80&w=900", "description": "Apărare și siguranță națională"}
}

DOMAINS = list(DOMAIN_META.keys())
WORK_MODE_OPTIONS = ["Remote", "Hibrid", "La birou", "Pe teren"]
CONTRACT_TYPE_OPTIONS = ["Full-time", "Part-time", "Proiect", "Internship"]
TEAM_SIZE_OPTIONS = ["Solo", "Echipă mică", "Echipă medie", "Echipă mare"]
TRAVEL_OPTIONS = ["Deloc", "Ocazional", "Frecvent", "Constant"]


@st.cache_data
def load_data_from_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT o.title, o.domain, o.description, s.title, os.relation_type, s.skill_type
                       FROM occupations o
                                JOIN occupation_skills os ON o.id = os.occupation_id
                                JOIN skills s ON os.skill_id = s.id
                       ''')
        # (.... codul tău existent cu SQL ....)
        rows = cursor.fetchall()
        conn.close()

        jobs_dict = {}
        hard_skills_domain = {d: set() for d in DOMAINS}
        soft_skills_set = set()

        # NOU: Grile salariale estimative pe domenii (în RON)
        DOMAIN_SALARIES = {
            "Specialiști și Profesioniști": (5000, 15000),
            "Manageri și Directori": (8000, 25000),
            "Tehnicieni și Maiștri": (4000, 9000),
            "Funcționari Administrativi": (3500, 6000),
            "Servicii și Comerț": (3000, 6000),
            "Agricultură și Silvicultură": (3000, 7000),
            "Muncitori Calificați și Artizani": (4000, 10000),
            "Operatori Mașini și Asamblori": (3500, 7000),
            "Muncitori Necalificați": (2500, 4000),
            "Forțele Armate": (4000, 10000)
        }

        for occ_title, domain, occ_desc, skill_title, rel_type, s_type in rows:
            if occ_title not in jobs_dict:
                # Extragem estimarea sau punem un default
                sal_lo, sal_hi = DOMAIN_SALARIES.get(domain, (3000, 8000))

                jobs_dict[occ_title] = {
                    "domain": domain,
                    "description": occ_desc,
                    "salary_range": (sal_lo, sal_hi),  # Gata, acum avem salarii!
                    "experience_min": 0,
                    "hard_skills": [],
                    "soft_skills": [],
                    "skill_relations": {}
                }
            # Salvăm relația pentru fiecare skill
            jobs_dict[occ_title]["skill_relations"][skill_title] = rel_type

            # NOU: Verificare inteligentă soft skills (Prioritate ESCO s_type, fallback keywords)
            is_soft = False
            if s_type and ('attitude' in s_type.lower() or 'transversal' in s_type.lower()):
                is_soft = True
            else:
                soft_keywords = [
                    "comunicare", "echipă", "timp", "lider", "conflict", "stres", "adaptabil",
                    "planific", "organiz", "colabor", "analiz", "decizi", "limb", "scrier",
                    "clienț", "management", "negocier", "creativ", "prezentar", "gândire",
                    "empat", "relați", "motiva", "coordon", "autonom"
                ]
                is_soft = any(kw in skill_title.lower() for kw in soft_keywords)

            if is_soft:
                jobs_dict[occ_title]["soft_skills"].append(skill_title)
                soft_skills_set.add(skill_title)
            else:
                jobs_dict[occ_title]["hard_skills"].append(skill_title)
                if domain in hard_skills_domain:
                    hard_skills_domain[domain].add(skill_title)

        hard_skills = {k: sorted(list(v)) for k, v in hard_skills_domain.items()}
        soft_skills = sorted(list(soft_skills_set))

        if not soft_skills:
            soft_skills = ["Comunicare", "Lucru în echipă", "Rezolvarea problemelor"]

        return jobs_dict, hard_skills, soft_skills

    except sqlite3.OperationalError:
        print(f"Baza de date {DB_NAME} lipsește! Rulează init_db.py")
        return {}, {}, []


JOBS, HARD_SKILLS_BY_DOMAIN, SOFT_SKILLS = load_data_from_db()

# Actualizare ROADMAPS legacy să folosească relation_type
ROADMAPS = {}
for job, info in JOBS.items():
    h_skills = info["hard_skills"]
    rels = info.get("skill_relations", {})

    essentials = [s for s in h_skills if rels.get(s) == 'essential']
    optionals = [s for s in h_skills if rels.get(s) == 'optional']

    if not essentials and not optionals:
        essentials = h_skills[:len(h_skills)//2]
        optionals = h_skills[len(h_skills)//2:]

    ROADMAPS[job] = {
        "Baze": [{"title": s, "type": "required"} for s in essentials[:4]],
        "Intermediar": [{"title": s, "type": "required"} for s in essentials[4:8]],
        "Avansat": [{"title": s, "type": "optional"} for s in optionals[:4]]
    }