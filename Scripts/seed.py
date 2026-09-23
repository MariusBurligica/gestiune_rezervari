import random
from faker import Faker
from App.db import run_execute # Asigură-te că importul corespunde cu proiectul tău

fake = Faker('ro_RO')

NUM_USERS = 500
NUM_CLIENTI = 1000
NUM_MESE = 500
NUM_REZERVARI = 1000
NUM_LOGS = 2000
NUM_MENIURI = 10
NUM_REZERVARI_MENIURI = 1500

print("1. Cream user admin...")
run_execute(
    "INSERT INTO users (username, password_hash) VALUES (%s, %s);",
    ("admin", "admin123")
)

print(f"2. Generam {NUM_USERS} de utilizatori random...")
simple_passwords = [
    "ananas", "parola123", "qwerty", "qwerty2024",
    "student123", "password", "abc123", "test123",
    "letmein", "maria2024"
]

for i in range(1, NUM_USERS + 1):
    username = f"{fake.user_name()}_{i}"
    password = random.choice(simple_passwords)

    run_execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s);",
        (username, password)
    )
    if i % 100 == 0: print(f"   ... {i}/{NUM_USERS} de utilizatori generati")

print(f"3. Generam {NUM_CLIENTI} de clienti...")
for i in range(1, NUM_CLIENTI + 1):
    nume_client = fake.name()
    nr_tlf = fake.phone_number().replace(" ", "").replace("-", "").replace(".", "")[:15]
    email = fake.email()

    run_execute(
        "INSERT INTO clienti (nume_client, nr_tlf, email) VALUES (%s, %s, %s);",
        (nume_client, nr_tlf, email)
    )
    if i % 200 == 0: print(f"   ... {i}/{NUM_CLIENTI} de clienti generati")

print(f"4. Generam {NUM_MESE} de mese...")
status_mese = ["Libera", "Ocupata", "Rezervata", "Indisponibila"]
for i in range(1, NUM_MESE + 1):
    cod_masa = f"M-{i:04d}"
    status = random.choice(status_mese)

    run_execute(
        "INSERT INTO mese (cod_masa, status) VALUES (%s, %s);",
        (cod_masa, status)
    )
    if i % 100 == 0: print(f"   ... {i}/{NUM_MESE} de mese generate")

print(f"5. Generam {NUM_REZERVARI} de rezervari...")
status_rezervari = ["In asteptare", "Confirmata", "Anulata", "Finalizata"]
for i in range(1, NUM_REZERVARI + 1):
    id_client = random.randint(1, NUM_CLIENTI)
    id_masa = random.randint(1, NUM_MESE)
    data_ora_rezervare = fake.future_datetime().strftime('%Y-%m-%d %H:%M:%S')
    numar_persoane = random.randint(1, 12)
    status = random.choice(status_rezervari)

    run_execute(
        "INSERT INTO rezervari (id_client, id_masa, data_ora_rezervare, numar_persoane, status) VALUES (%s, %s, %s, %s, %s);",
        (id_client, id_masa, data_ora_rezervare, numar_persoane, status)
    )
    if i % 200 == 0: print(f"   ... {i}/{NUM_REZERVARI} de rezervari generate")

print(f"6. Generam {NUM_LOGS} de loguri de activitate...")
actiuni = ["Login", "Logout", "Vizualizare Meniu", "Creare Rezervare", "Anulare Rezervare", "Actualizare Date"]
total_users = NUM_USERS + 1

for i in range(1, NUM_LOGS + 1):
    id_user = random.randint(1, total_users)
    action = random.choice(actiuni)

    run_execute(
        "INSERT INTO user_log (id_user, action) VALUES (%s, %s);",
        (id_user, action)
    )
    if i % 500 == 0: print(f"   ... {i}/{NUM_LOGS} de loguri generate")

print(f"7. Generam {NUM_MENIURI} de meniuri...")
nume_meniuri = [
    "Meniu Traditional Romanesc", "Meniu Premium Vita", "Meniu Vegetarian",
    "Meniu Vegan", "Meniu Copii", "Meniu Mediteranean",
    "Meniu Asiatic", "Meniu Nunta Clasic", "Meniu Botez", "Candy Bar Extra"
]

for i in range(1, NUM_MENIURI + 1):
    cod_meniu = f"MN-{i:03d}"
    nume_meniu = nume_meniuri[i-1]
    pret = round(random.uniform(50.0, 400.0), 2)

    run_execute(
        "INSERT INTO meniuri (cod_meniu, nume_meniu, pret) VALUES (%s, %s, %s);",
        (cod_meniu, nume_meniu, pret)
    )

print(f"8. Generam {NUM_REZERVARI_MENIURI} de asocieri rezervari-meniuri...")
for i in range(1, NUM_REZERVARI_MENIURI + 1):
    id_rezervare = random.randint(1, NUM_REZERVARI)
    id_meniu = random.randint(1, NUM_MENIURI)
    cantitate = random.randint(1, 50)

    run_execute(
        "INSERT INTO rezervari_meniuri (id_rezervare, id_meniu, cantitate) VALUES (%s, %s, %s);",
        (id_rezervare, id_meniu, cantitate)
    )
    if i % 300 == 0: print(f"   ... {i}/{NUM_REZERVARI_MENIURI} de asocieri generate")

print("Gata! Toate datele au fost introduse in baza de date.")