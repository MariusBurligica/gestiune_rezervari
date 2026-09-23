import json
from App.db import get_connection, run_select

print("REZERVARE SERVICE")

id_client = run_select("SELECT id_client FROM clienti LIMIT 1;")[0][0]
id_masa = run_select("SELECT id_masa FROM mese LIMIT 1;")[0][0]
data_ora = "2026-10-20 18:00:00"
nr_persoane = 4

meniuri = [
    {"cod": "MN-001", "cantitate": 2},
    {"cod": "MN-002", "cantitate": 1},
    {"cod": "MN-005", "cantitate": 3}
]

meniuri_json = json.dumps(meniuri)

print("Apelam procedura creare_rezervare_completa...")

conn = get_connection()
cur = conn.cursor()

try:
    cur.execute(
        "CALL creare_rezervare_completa(%s, %s, %s, %s, %s);",
        (id_client, id_masa, data_ora, nr_persoane, meniuri_json)
    )

    row = cur.fetchone()
    id_rezervare = row[0]

    while cur.nextset():
        if cur.description is not None:
            cur.fetchall()

    conn.commit()
    print(f"OK: Rezervare creata. id_rezervare = {id_rezervare}")

finally:
    cur.close()
    conn.close()

print("\nVerificare in DB (rezervari_meniuri):")
query = """
SELECT rm.id_rezervare, m.cod_meniu, m.nume_meniu, rm.cantitate
FROM rezervari_meniuri rm
JOIN meniuri m ON m.id_meniu = rm.id_meniu
WHERE rm.id_rezervare = %s
ORDER BY m.cod_meniu;
"""
rows = run_select(query, (id_rezervare,))
for r in rows:
    print(r)