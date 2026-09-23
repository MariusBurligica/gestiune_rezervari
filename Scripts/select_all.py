import json
from pathlib import Path
from App.db import run_select

sql = """
SELECT 
    c.id_client,
    c.nume_client,
    c.email,
    COUNT(r.id_rezervare) AS numar_rezervari
FROM clienti c
LEFT JOIN rezervari r ON r.id_client = c.id_client
GROUP BY c.id_client, c.nume_client, c.email
ORDER BY numar_rezervari DESC;
"""

rows = run_select(sql)

data = []
for r in rows:
    data.append({
        "id_client": r[0],
        "nume_client": r[1],
        "email": r[2],
        "numar_rezervari": int(r[3]) if r[3] is not None else 0
    })

out_path = Path("outputs") / "rezervari_per_client.json"
out_path.parent.mkdir(exist_ok=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat: {out_path}")