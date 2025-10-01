# database_setup.py
import sqlite3

DB_NAME = "habits.db"

def get_connection():
    # Svaki put vraćamo novu konekciju ka lokalnoj .db bazi
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Tabela za navike
    c.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        frequency INTEGER NOT NULL
    )
    """)

    # Tabela za evidenciju odrađenog po datumima (YYYY-MM-DD)
    c.execute("""
    CREATE TABLE IF NOT EXISTS done (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(habit_id) REFERENCES habits(id)
    )
    """)

    # Indeksi (brže) + unique da ne dupliraš isti dan za istu naviku
    c.execute("CREATE INDEX IF NOT EXISTS idx_done_habit ON done(habit_id)")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_done_unique ON done(habit_id, date)")

    conn.commit()
    conn.close()
    print("Baza 'habits.db' je spremna ✅")

if __name__ == "__main__":
    init_db()
