from App.db import run_execute
from Scripts.create_tables import create_tables

print("Stergem toate tabelele existente...")


run_execute("DROP TABLE IF EXISTS rezervari_meniuri;") # Depinde de rezervari si meniuri
run_execute("DROP TABLE IF EXISTS user_log;")          # Depinde de users
run_execute("DROP TABLE IF EXISTS rezervari;")         # Depinde de clienti si mese


run_execute("DROP TABLE IF EXISTS mese;")
run_execute("DROP TABLE IF EXISTS clienti;")
run_execute("DROP TABLE IF EXISTS users;")
run_execute("DROP TABLE IF EXISTS meniuri;")

print("Creez tabelele din schema sql...")
create_tables()
print("Rebuilt gata!")