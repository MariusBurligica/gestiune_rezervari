import os
import mariadb
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()

DB_HOST = "127.0.0.1"
DB_PORT = 3307
DB_NAME = "Reservation_system"
ROOT_USER = "root"
ROOT_PASS = os.getenv("DB_PASSWORD")

ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def get_root_connection():
    return mariadb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=ROOT_USER,
        password=ROOT_PASS,
        database=DB_NAME
    )

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode(),
        bcrypt.gensalt()
    ).decode()

def create_db_users():
    conn = get_root_connection()
    cur = conn.cursor()

    db_users = [
        ("manager", "manager123", "ALL PRIVILEGES"),
        ("insert_user", "insert123", "SELECT, INSERT"),
        ("update_user", "update123", "SELECT, INSERT, UPDATE"),
        ("delete_user", "delete123", "SELECT, DELETE")
    ]

    for username, password, privileges in db_users:
        try:
            cur.execute(f"DROP USER IF EXISTS '{username}'@'%'")
            cur.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            cur.execute(f"GRANT {privileges} ON {DB_NAME}.* TO '{username}'@'%'")
            print(f"[OK] Created DB user: {username}")
        except Exception as e:
            print("Error:", e)

    cur.execute("FLUSH PRIVILEGES")
    conn.commit()
    conn.close()

def encrypt_app_users():
    conn = get_root_connection()
    cur = conn.cursor()


    cur.execute("SELECT id_user, password_hash FROM users")
    rows = cur.fetchall()

    for user_id, pwd in rows:
        if not str(pwd).startswith("$2b$"):
            hashed = hash_password(pwd)
            cur.execute(
                "UPDATE users SET password_hash=? WHERE id_user=?",
                (hashed, user_id)
            )
            print(f"[UPDATED] User ID {user_id} password encrypted")

    conn.commit()
    conn.close()

def encrypt_client_data():
    conn = get_root_connection()
    cur = conn.cursor()

    cur.execute("ALTER TABLE clienti MODIFY email VARCHAR(255) NOT NULL;")
    cur.execute("ALTER TABLE clienti MODIFY nr_tlf VARCHAR(255) NOT NULL;")

    cur.execute("SELECT id_client, email, nr_tlf FROM clienti")
    rows = cur.fetchall()

    for client_id, email, nr_tlf in rows:
        update_needed = False
        new_email = email
        new_nr_tlf = nr_tlf

        if email and not str(email).startswith("gAAAAA"):
            new_email = cipher_suite.encrypt(str(email).encode()).decode()
            update_needed = True

        if nr_tlf and not str(nr_tlf).startswith("gAAAAA"):
            new_nr_tlf = cipher_suite.encrypt(str(nr_tlf).encode()).decode()
            update_needed = True

        if update_needed:
            cur.execute(
                "UPDATE clienti SET email=?, nr_tlf=? WHERE id_client=?",
                (new_email, new_nr_tlf, client_id)
            )
            print(f"[UPDATED] Client ID {client_id} date sensibile (email & telefon) criptate")

    conn.commit()
    conn.close()

def main():
    print("\n=== CREATE DB USERS + GRANT ===")
    create_db_users()

    print("\n=== ENCRYPT APP USERS PASSWORDS ===")
    encrypt_app_users()

    print("\n=== ENCRYPT SENSITIVE CLIENT DATA ===")
    encrypt_client_data()

    print("\n[V] SECURITY SETUP COMPLETED")
    print(f"[!] IMPORTANT: Salvează această cheie de decriptare în .env: {ENCRYPTION_KEY.decode()}")

if __name__ == "__main__":
    main()