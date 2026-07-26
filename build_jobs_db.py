import sqlite3
import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'jobs.db')

# Câte cereri să facă în paralel (nu pune mai mult de 30-50, ca să nu ne blocheze API-ul)
MAX_WORKERS = 40
BATCH_SIZE = 1000  # Salvăm în DB din 500 în 500 ca să fie ultra-rapid

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL;") # Pentru scrieri/citiri sigure
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            city TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def fetch_single_job():
    """Funcția executată de fiecare 'muncitor' (thread) în paralel."""
    try:
        response = requests.get("https://api.peviitor.ro/v1/random/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            job = data.get('job', data) if isinstance(data, dict) else data[0]

            job_title = job.get('job_title', '').strip()
            company = job.get('company', '').strip()
            locations = job.get('location', [])
            city = locations[0].strip() if locations else "Nespecificat"
            job_url = job.get('job_link', job.get('url', '')).strip()

            if job_title and company and job_url:
                return (job_title, company, city, job_url)
    except Exception:
        pass # Ignorăm erorile de rețea sau timeout-urile individuale
    return None

def populate_database_fast(target_unique_jobs=50000):
    conn = setup_database()
    cursor = conn.cursor()

    # Aflăm câte avem deja
    cursor.execute("SELECT COUNT(*) FROM jobs")
    initial_count = cursor.fetchone()[0]

    print(f"🚀 Pornim motorul de scraping (Multithreading cu {MAX_WORKERS} workers).")
    print(f"📊 Joburi curente în DB: {initial_count}. Țintă: {target_unique_jobs}")

    jobs_buffer = []
    total_added_now = 0
    start_time = time.time()

    # Folosim ThreadPoolExecutor pentru a lansa zeci de cereri simultan
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Lansăm un prim val de cereri
        futures = {executor.submit(fetch_single_job) for _ in range(MAX_WORKERS * 2)}

        while futures and (initial_count + total_added_now) < target_unique_jobs:
            # Așteptăm să se termine oricare dintre ele
            done, futures = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

            for future in done:
                result = future.result()
                if result:
                    jobs_buffer.append(result)

                # Când s-au strâns 500 de oferte, le aruncăm în baza de date dintr-un foc
                if len(jobs_buffer) >= BATCH_SIZE:
                    cursor.executemany('''
                        INSERT OR IGNORE INTO jobs (title, company, city, url)
                        VALUES (?, ?, ?, ?)
                    ''', jobs_buffer)
                    conn.commit()

                    # Verificăm câte au fost de fapt inserate (fără duplicate)
                    added_this_batch = cursor.rowcount if cursor.rowcount > 0 else 0
                    total_added_now += added_this_batch

                    print(f"⚡ Progres: Salvat un batch. Total joburi unice adăugate acum: {total_added_now}")
                    jobs_buffer.clear() # Golim bufferul pentru următorul lot

            # Adăugăm mereu noi cereri în locul celor care s-au terminat, ca să ținem toți workerii ocupați
            while len(futures) < (MAX_WORKERS * 2) and (initial_count + total_added_now) < target_unique_jobs:
                futures.add(executor.submit(fetch_single_job))

    # Salvăm ce a mai rămas în buffer la final
    if jobs_buffer:
        cursor.executemany('''
            INSERT OR IGNORE INTO jobs (title, company, city, url)
            VALUES (?, ?, ?, ?)
        ''', jobs_buffer)
        conn.commit()

    conn.close()
    duration = round(time.time() - start_time, 2)
    print(f"\n🎉 GATA! Descărcare încheiată în {duration} secunde.")

if __name__ == "__main__":
    # Schimbă numărul de aici dacă vrei mai multe. Recomand maxim 50000.
    populate_database_fast(target_unique_jobs=70000)