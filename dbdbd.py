import sqlite3

DB_PATH = "practice_db.sqlite"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS t")
    cursor.execute("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, val TEXT)")
    
    cursor.execute("INSERT INTO t (val) VALUES (?)", ("Apple",))
    conn.commit()

except sqlite3.Error as err:
    print(f"Database error: {err}")
finally:
    if conn:
        conn.close()