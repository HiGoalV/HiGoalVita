# create_sqlite_schema.py

import sqlite3

DB_PATH = "appdata/database/sqlite/example_sqlite.db"
SCHEMA_PATH = "appdata/database/sqlite/schema.sql"

def create_sqlite_schema_from_file():
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("[SUCCESS] Schema applied from external file.")

if __name__ == "__main__":
    create_sqlite_schema_from_file()