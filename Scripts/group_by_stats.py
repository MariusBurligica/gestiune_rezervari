import json
from pathlib import Path
from App.db import run_select


sql = """
SELECT 
    c.nume_client,
    m.cod_masa,
    r.data_ora_rezervare,
    r.numar_persoane,
    r.status
FROM rezervari r
JOIN clienti c ON r.id_client = c.id_client
JOIN mese m ON r.id_masa = m.id_masa
ORDER BY r.data_ora_rezervare DESC;
"""


rows = run_select(sql)

data = []
for r in rows:
    data.append({
        "client": r[0],
        "masa": r[1],
        "data_ora": str(r[2]),
        "persoane": int(r[3]),
        "status": r[4]
    })


out_path = Path("outputs") / "raport_rezervari.json"

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat cu succes: {out_path}")