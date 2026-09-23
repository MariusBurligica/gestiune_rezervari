from Scripts.create_tables import create_tables

def init_db():
    print("Initializing Database")
    create_tables()
    print("Database Initialized")

if __name__ == "__main__":
    init_db()