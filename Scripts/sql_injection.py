from App.db import get_connection

def run_query(search_term, is_safe=True):
    conn = get_connection()
    cur = conn.cursor()

    try:
        if is_safe:

            sql = "SELECT id_client, nume_client, telefon FROM clienti WHERE nume_client = %s"
            cur.execute(sql, (search_term,))
            print(f"[SAFE] SQL Generat: {sql} | Parametru: {search_term}")
        else:

            sql = f"SELECT id_client, nume_client, telefon FROM clienti WHERE nume_client = '{search_term}'"
            cur.execute(sql)
            print(f"[UNSAFE] SQL Generat (Concatenat): {sql}")

        rows = cur.fetchall()
        print(f"-> Rânduri returnate: {len(rows)}")
        for r in rows:
            print(f"   {r}")
        print("-" * 50)

    except Exception as e:
        print(f"-> EROARE: {e}\n" + "-" * 50)
    finally:
        cur.close()
        conn.close()


def main():
    print("=== SCENARIUL 1: Interogare Legitimă ===")
    nume_legitim = "Popescu Ion"  # Înlocuiește cu un nume real din baza ta
    run_query(nume_legitim, is_safe=False)
    run_query(nume_legitim, is_safe=True)

    print("\n=== SCENARIUL 2: Tentativă de Bypass (OR 1=1) ===")
    bypass_payload = "' OR '1'='1"
    run_query(bypass_payload, is_safe=False)
    run_query(bypass_payload, is_safe=True)

    print("\n=== SCENARIUL 3: Comentariu SQL (--) ===")
    comment_payload = "Admin' -- "
    run_query(comment_payload, is_safe=False)
    run_query(comment_payload, is_safe=True)


if __name__ == "__main__":
    main()