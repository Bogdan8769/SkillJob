"""
init_db.py
----------
Importă TOATE meseriile și skill-urile din ESCO.
Le grupează în cele 10 Mari Domenii oficiale ISCO-08.
"""

import sqlite3
import csv
import os

DB_NAME = "skilljob.db"
DATA_DIR = "data"

OCCUPATIONS_CSV = os.path.join(DATA_DIR, "occupations_ro.csv")
SKILLS_CSV = os.path.join(DATA_DIR, "skills_ro.csv")
RELATIONS_CSV = os.path.join(DATA_DIR, "occupationSkillRelations.csv")

# Cele 10 mari grupe oficiale internaționale (ISCO-08)
ISCO_MAP = {
    "1": "Manageri și Directori",
    "2": "Specialiști și Profesioniști",
    "3": "Tehnicieni și Maiștri",
    "4": "Funcționari Administrativi",
    "5": "Servicii și Comerț",
    "6": "Agricultură și Silvicultură",
    "7": "Muncitori Calificați și Artizani",
    "8": "Operatori Mașini și Asamblori",
    "9": "Muncitori Necalificați",
    "0": "Forțele Armate"
}

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Curățăm baza de date...")
    cursor.executescript('''
        DROP TABLE IF EXISTS occupation_skills;
        DROP TABLE IF EXISTS occupations;
        DROP TABLE IF EXISTS skills;
    ''')

    cursor.executescript('''
        CREATE TABLE occupations (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            domain TEXT
        );
        CREATE TABLE skills (
            id TEXT PRIMARY KEY,
            title TEXT,
            skill_type TEXT
        );
        CREATE TABLE occupation_skills (
            occupation_id TEXT,
            skill_id TEXT,
            relation_type TEXT,
            FOREIGN KEY (occupation_id) REFERENCES occupations (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        );
    ''')

    print("1. Importăm TOATE Ocupațiile...")
    try:
        with open(OCCUPATIONS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            inserted_occs = 0
            for row in reader:
                # Extragem prima cifră din codul ISCO pentru a afla domeniul mare
                isco_code = row.get('iscoGroup', '9')
                prima_cifra = str(isco_code)[0] if isco_code else '9'
                domain = ISCO_MAP.get(prima_cifra, "Diverse")

                cursor.execute('''
                    INSERT OR IGNORE INTO occupations (id, title, description, domain)
                    VALUES (?, ?, ?, ?)
                ''', (row['conceptUri'], row['preferredLabel'], row['description'], domain))
                inserted_occs += 1
            print(f"-> S-au importat {inserted_occs} ocupații.")
    except FileNotFoundError:
        print(f"EROARE: Nu s-a găsit {OCCUPATIONS_CSV}.")

    print("2. Importăm TOATE Skill-urile...")
    try:
        with open(SKILLS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            inserted_skills = 0
            for row in reader:
                cursor.execute('''
                    INSERT OR IGNORE INTO skills (id, title, skill_type)
                    VALUES (?, ?, ?)
                ''', (row['conceptUri'], row['preferredLabel'], row['skillType']))
                inserted_skills += 1
            print(f"-> S-au importat {inserted_skills} skill-uri.")
    except FileNotFoundError:
        print(f"EROARE: Nu s-a găsit {SKILLS_CSV}.")

    print("3. Importăm Relațiile...")
    try:
        with open(RELATIONS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            inserted_rels = 0
            for row in reader:
                cursor.execute('''
                    INSERT INTO occupation_skills (occupation_id, skill_id, relation_type)
                    VALUES (?, ?, ?)
                ''', (row['occupationUri'], row['skillUri'], row['relationType']))
                inserted_rels += 1
            print(f"-> S-au importat {inserted_rels} legături job-skill.")
    except FileNotFoundError:
        print(f"EROARE: Nu s-a găsit {RELATIONS_CSV}.")

    conn.commit()
    conn.close()
    print(f"\nGATA! Baza de date conține tot sistemul ESCO.")

if __name__ == "__main__":
    setup_database()