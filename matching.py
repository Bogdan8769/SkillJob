"""
matching.py
-----------
Motorul de recomandare al SkillJob. Separat strict de UI: primește un profil
(dict rezultat din wizard) și returnează o listă ordonată de recomandări.
"""

from database import JOBS

WEIGHT_HARD_SKILL = 3
WEIGHT_SOFT_SKILL = 1
# Am eliminat DOMAIN_MATCH_BONUS deoarece algoritmul deja filtrează strict pe bază de domeniu.

def compute_recommendations(user_data, top_n=3):
    recommendations = []

    # 1. Transformăm selecția text în valoare numerică pentru calcul
    exp_input = user_data.get("experience_years", 0)
    if isinstance(exp_input, str):
        if "Entry" in exp_input:
            exp_val = 1
        elif "Mid" in exp_input:
            exp_val = 4
        elif "Senior" in exp_input:
            exp_val = 6
        else:
            exp_val = 0
    else:
        exp_val = exp_input

    user_hard = set(user_data.get("hard_skills", []))
    user_soft = set(user_data.get("soft_skills", []))

    for job_name, info in JOBS.items():
        # Filtru 1: Domeniu
        if user_data.get("domain") and info.get("domain") != user_data["domain"]:
            continue

        # Filtru 2: Experiență
        if exp_val < info.get("experience_min", 0):
            continue

        # Seturi de skill-uri necesare pentru job-ul curent
        job_hard = set(info.get("hard_skills", []))
        job_soft = set(info.get("soft_skills", []))

        matched_hard = user_hard.intersection(job_hard)
        matched_soft = user_soft.intersection(job_soft)

        # Calculăm scorul maxim posibil pentru acest job pe baza ponderilor
        max_possible_score = (len(job_hard) * WEIGHT_HARD_SKILL) + (len(job_soft) * WEIGHT_SOFT_SKILL)

        if max_possible_score == 0:
            continue

        # Calculăm scorul real obținut de utilizator
        actual_score = (len(matched_hard) * WEIGHT_HARD_SKILL) + (len(matched_soft) * WEIGHT_SOFT_SKILL)
        match_score = actual_score / max_possible_score

        if match_score > 0:
            recommendations.append({
                "job": job_name,
                "domain": info.get("domain"),
                "description": info.get("description"),
                "match_pct": int(match_score * 100),
                "matched_hard": list(matched_hard),
                "matched_soft": list(matched_soft)
            })

    # Sortare descrescătoare după procentul de potrivire
    recommendations.sort(key=lambda x: x["match_pct"], reverse=True)
    return recommendations[:top_n]