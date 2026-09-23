import time
from App.db import run_execute
from Scripts.seed import data_ora_rezervare


def apply_indexes():
    print("Applying indexes...")
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_ora_Rezervare ON rezervari(data_ora_rezervare);",
        "CREATE INDEX IF NOT EXISTS idx_nume_client ON clienti(nume_client);",
        "CREATE INDEX IF NOT EXISTS idx_status_rezervare ON rezervari(status);",
        "CREATE INDEX IF NOT EXISTS idx_telefon_client ON clienti(nr_tlf);",
        "CREATE INDEX IF NOT EXISTS idx_status_masa ON mese(status);"
    ]

    for query in index_queries:
        print(f"Executing query: {query}")
        try:
            start_time = time.time()
            run_execute(query)
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            print(f"Succes! (Duration: {duration:.2f} ms)")
        except Exception as e:
            print(f"Error: {e}")
        print("------------------------------------")

    print("Toate indexurile au fost procesate.")



if __name__ == "__main__":
    apply_indexes()