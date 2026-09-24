# Sistem de Gestiune "Săli de Evenimente & Rezervări"

Aplicație informatică dezvoltată pentru administrarea completă a rezervărilor dintr-un restaurant sau sală de evenimente, bazată pe o arhitectură de tip Monolit Modular. Sistemul integrează o bază de date relațională robustă, o interfață web dinamică și scripturi utilitare avansate pentru automatizare, securitate și Business Intelligence.

## 🚀 Funcționalități Principale

* **Gestiune CRUD Dinamică (Single Source of Truth):** Generarea automată a interfețelor (formulare, liste de vizualizare) pentru clienți, mese, rezervări și meniuri pe baza unui dicționar centralizat de configurare (`APP_CRUD_CONFIG`), eliminând necesitatea definirii manuale a rutelor pentru fiecare entitate.
* **Automatizări direct în Baza de Date:** Implementarea procedurilor stocate pentru gestionarea tranzacțiilor compuse (ex: crearea rezervării și asocierea meniurilor simultan). Utilizarea triggerelor SQL pentru blocarea rezervărilor retroactive și actualizarea statusului meselor, alături de evenimente planificate (Events) pentru eliberarea automată a meselor la 2 ore după confirmare.
* **Securitate Avansată (Defense in Depth):** Aplicarea *Principiului celui mai mic privilegiu* prin crearea de roluri cu acces restrâns în baza de date. Protejarea identităților prin hashing cu `bcrypt` pentru parole, criptarea datelor sensibile ale clienților (email, telefon) folosind `Fernet` și prevenirea atacurilor de tip SQL Injection prin interogări exclusiv parametrizate.
* **Rapoarte & Business Intelligence:** Modul automatizat (`reports.py`) capabil să extragă statistici (ex: Top Meniuri Comandate, Top Clienți Activi) și să le exporte în formate CSV, JSON și PDF. Rapoartele PDF includ tabele formatate cu `reportlab` și grafice statistice generate via `matplotlib`.
* **Performanță și Audit:** Sistem de indexare SQL testat prin scripturi de benchmarking (`perf_bench.py`) pentru reducerea timpilor de interogare. Monitorizarea riguroasă a acțiunilor prin tabela `user_log` și trasabilitatea rulărilor automate în fișiere `audit.log`.

## 🛠️ Tehnologii Utilizate

* **Backend:** Python 3, micro-framework-ul Flask.
* **Bază de Date:** MariaDB (gestionată prin DataGrip).
* **Infrastructură:** Docker & Docker Compose pentru containerizarea bazei de date.
* **Frontend:** Motor de randare Jinja2, HTML5 și CSS cu interfață Dark Mode bazată pe design Glassmorphism.

## 📁 Structura Proiectului

```text
gestiune_rezervari/
├── App/
│   └── db.py                    # Stratul de acces securizat la baza de date
├── flask_app/
│   ├── static/style.css         # Foaia de stil (Dark Mode / Glassmorphism)
│   ├── templates/               # Șabloane Jinja2 (base, crud_form, crud_list, index etc.)
│   └── web.py                   # Punctul principal de intrare pentru aplicația Flask
├── Scripts/
│   ├── create_tables.py         # Parsează și execută fișierele SQL de inițializare
│   ├── seed.py                  # Generează date sintetice (Faker) pentru testare
│   ├── security_setup.py        # Configurează rolurile DB, hashing-ul și criptarea
│   ├── reports.py               # Generare rapoarte BI (CSV, JSON, PDF)
│   ├── auto_report.py           # Orchestrator automat cu audit logging
│   ├── export_csv.py / import_csv.py # Utilitare I/O securizate
│   └── ... (alte utilitare de testare, benchmarking și indecși)
├── sql/
│   ├── schema.sql               # Definirea tabelelor cu IF NOT EXISTS
│   ├── procedures.sql           # Proceduri stocate delimitate prin --PROC_END
│   └── triggers.sql             # Triggere și evenimente delimitate prin --TRIGGER_END
├── docker-compose.yml           # Configurația containerului MariaDB (port 3307:3306)
└── .env                         # Stocarea credențialelor și cheilor de criptare
