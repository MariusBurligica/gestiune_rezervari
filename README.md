# Sistem de Gestiune "Săli de Evenimente & Rezervări"

Aplicație informatică dezvoltată pentru administrarea completă a rezervărilor dintr-un restaurant sau sală de evenimente, bazată pe o arhitectură de tip Monolit Modular. Sistemul integrează o bază de date relațională robustă, o interfață web dinamică și scripturi utilitare avansate pentru automatizare, securitate și Business Intelligence[cite: 10].

## 🚀 Funcționalități Principale

* **Gestiune CRUD Dinamică (Single Source of Truth):** Generarea automată a interfețelor (formulare, liste de vizualizare) pentru clienți, mese, rezervări și meniuri pe baza unui dicționar centralizat de configurare (`APP_CRUD_CONFIG`), eliminând necesitatea definirii manuale a rutelor pentru fiecare entitate[cite: 10].
* **Automatizări direct în Baza de Date:** Implementarea procedurilor stocate pentru gestionarea tranzacțiilor compuse (ex: crearea rezervării și asocierea meniurilor simultan)[cite: 10]. Utilizarea triggerelor SQL pentru blocarea rezervărilor retroactive și actualizarea statusului meselor, alături de evenimente planificate (Events) pentru eliberarea automată a meselor la 2 ore după confirmare[cite: 10].
* **Securitate Avansată (Defense in Depth):** Aplicarea *Principiului celui mai mic privilegiu* prin crearea de roluri cu acces restrâns în baza de date[cite: 10]. Protejarea identităților prin hashing cu `bcrypt` pentru parole, criptarea datelor sensibile ale clienților (email, telefon) folosind `Fernet` și prevenirea atacurilor de tip SQL Injection prin interogări exclusiv parametrizate[cite: 10].
* **Rapoarte & Business Intelligence:** Modul automatizat (`reports.py`) capabil să extragă statistici (ex: Top Meniuri Comandate, Top Clienți Activi) și să le exporte în formate CSV, JSON și PDF[cite: 10]. Rapoartele PDF includ tabele formatate cu `reportlab` și grafice statistice generate via `matplotlib`[cite: 10].
* **Performanță și Audit:** Sistem de indexare SQL testat prin scripturi de benchmarking (`perf_bench.py`) pentru reducerea timpilor de interogare[cite: 10]. Monitorizarea riguroasă a acțiunilor prin tabela `user_log` și trasabilitatea rulărilor automate în fișiere `audit.log`[cite: 10].

## 🛠️ Tehnologii Utilizate

* **Backend:** Python 3, micro-framework-ul Flask[cite: 10].
* **Bază de Date:** MariaDB (gestionată prin DataGrip)[cite: 10].
* **Infrastructură:** Docker & Docker Compose pentru containerizarea bazei de date[cite: 10].
* **Frontend:** Motor de randare Jinja2, HTML5 și CSS cu interfață Dark Mode bazată pe design Glassmorphism[cite: 10].

## 📁 Structura Proiectului

```text
gestiune_rezervari/
├── App/
│   └── db.py                    # Stratul de acces securizat la baza de date[cite: 10]
├── flask_app/
│   ├── static/style.css         # Foaia de stil (Dark Mode / Glassmorphism)[cite: 10]
│   ├── templates/               # Șabloane Jinja2 (base, crud_form, crud_list, index etc.)[cite: 10]
│   └── web.py                   # Punctul principal de intrare pentru aplicația Flask[cite: 10]
├── Scripts/
│   ├── create_tables.py         # Parsează și execută fișierele SQL de inițializare[cite: 10]
│   ├── seed.py                  # Generează date sintetice (Faker) pentru testare[cite: 10]
│   ├── security_setup.py        # Configurează rolurile DB, hashing-ul și criptarea[cite: 10]
│   ├── reports.py               # Generare rapoarte BI (CSV, JSON, PDF)[cite: 10]
│   ├── auto_report.py           # Orchestrator automat cu audit logging[cite: 10]
│   ├── export_csv.py / import_csv.py # Utilitare I/O securizate[cite: 10]
│   └── ... (alte utilitare de testare, benchmarking și indecși)
├── sql/
│   ├── schema.sql               # Definirea tabelelor cu IF NOT EXISTS[cite: 10]
│   ├── procedures.sql           # Proceduri stocate delimitate prin --PROC_END[cite: 10]
│   └── triggers.sql             # Triggere și evenimente delimitate prin --TRIGGER_END[cite: 10]
├── docker-compose.yml           # Configurația containerului MariaDB (port 3307:3306)[cite: 10]
└── .env                         # Stocarea credențialelor și cheilor de criptare[cite: 10]
