from App.db import run_execute, run_select

try:
    id_masa_test = run_select("SELECT id_masa FROM mese WHERE status IN ('Libera', 'liber') LIMIT 1;")[0][0]
    print(f"--> Folosim masa cu ID-ul {id_masa_test} pentru teste.")
except IndexError:
    print("EROARE SETUP: Nu ai nicio masă liberă în baza de date. Adaugă una!")
    exit()

try:

    id_client_test = run_select("SELECT id_client FROM clienti LIMIT 1;")[0][0]
    print(f"--> Folosim clientul cu ID-ul {id_client_test} pentru teste.\n")
except IndexError:
    print(
        "EROARE SETUP: Nu ai niciun client în baza de date! Trebuie să adaugi cel puțin un client în tabela 'clienti' înainte de a rula testul.")
    print(
        "Exemplu SQL: INSERT INTO clienti (nume_client, nr_tlf, email) VALUES ('Client Test', '0700000000', 'test@test.ro');")
    exit()

print("TEST 1: TRIGGER BEFORE INSERT (Data în trecut)")
print("Încercăm inserarea unei rezervări cu data de ieri...")
try:

    run_execute(
        sql="INSERT INTO rezervari (id_client, id_masa, numar_persoane, data_ora_rezervare, status) VALUES (%s, %s, %s, DATE_SUB(NOW(), INTERVAL 1 DAY), %s);",
        params=(id_client_test, id_masa_test, 2, 'Confirmata')  # 2 persoane
    )
    print("EROARE: Inserarea a mers! Triggerul NU funcționează sau data nu a fost considerată în trecut.")
except Exception as e:
    print("OK: Inserarea a fost respinsă de trigger.")
    print("Mesaj DB:", e)

print("-" * 50)


print("TEST 2: TRIGGER AFTER INSERT (Schimbare status masă)")
print("Inserăm o rezervare validă (data în viitor, status 'Confirmata')...")
try:

    run_execute(
        sql="INSERT INTO rezervari (id_client, id_masa, numar_persoane, data_ora_rezervare, status) VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL 1 HOUR), %s);",
        params=(id_client_test, id_masa_test, 4, 'Confirmata')  # 4 persoane
    )
    print("OK: Inserare validă reușită.")

    status_masa = run_select("SELECT status FROM mese WHERE id_masa = %s;", (id_masa_test,))[0][0]
    if status_masa == 'Rezervata':
        print(f"OK: Triggerul a funcționat. Masa {id_masa_test} este acum 'Rezervata'.")
    else:
        print(f"EROARE: Triggerul NU a funcționat. Status masă rămas: {status_masa}")

except Exception as e:
    print("EROARE neașteptată la Testul 2:", e)

print("-" * 50)


print("TEST 3: EVENT (Eliberare masă expirată)")
print("Simulăm trecerea timpului mutând rezervarea de la Testul 2 cu 3 ore în trecut...")
try:
    id_rezervare = \
    run_select("SELECT id_rezervare FROM rezervari WHERE id_masa = %s ORDER BY id_rezervare DESC LIMIT 1;",
               (id_masa_test,))[0][0]

    run_execute(
        sql="UPDATE rezervari SET data_ora_rezervare = DATE_SUB(NOW(), INTERVAL 3 HOUR) WHERE id_rezervare = %s;",
        params=(id_rezervare,)
    )
    print("OK: Am modificat data rezervării (timpul a expirat).")


    run_execute(
        sql="""
            UPDATE mese m
            JOIN rezervari r ON m.id_masa = r.id_masa
            SET m.status = 'Libera' 
            WHERE r.status = 'Confirmata' 
              AND ADDTIME(r.data_ora_rezervare, '02:00:00') <= CURRENT_TIMESTAMP;
        """
    )

    status_masa_final = run_select("SELECT status FROM mese WHERE id_masa = %s;", (id_masa_test,))[0][0]
    if status_masa_final in ('Libera', 'liber'):
        print(f"OK: Logica EVENT-ului a funcționat impecabil! Masa {id_masa_test} este din nou liberă.")
    else:
        print(f"EROARE: Eventul nu a eliberat masa. Status rămas: {status_masa_final}")

except Exception as e:
    print("EROARE neașteptată la Testul 3:", e)

print("\n=== TESTE FINALIZATE ===")