import sqlite3

DB_PATH = "practice_db.sqlite"  # File-backed database persists between runs.

conn = None
try:
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()

	# SCHEMA setup: create table if it does not exist yet.
	cursor.execute("CREATE TABLE IF NOT EXISTS t (id INT, val TEXT)")

	# CREATE: insert a row with parameter placeholders (safe vs string formatting).
	cursor.execute("INSERT INTO t VALUES (?, ?)", (1, "Apple"))
	conn.commit()  # Commit after INSERT/UPDATE/DELETE to persist changes.
	print("Created:", cursor.execute("SELECT * FROM t").fetchall())  # READ

	# UPDATE: change the value in the row.
	cursor.execute("UPDATE t SET val = ? WHERE id = ?", ("Banana", 1))
	conn.commit()
	print("Updated:", cursor.execute("SELECT * FROM t").fetchall())  # READ

	# DELETE: remove the row.
	# cursor.execute("DELETE FROM t WHERE id = ?", (1,))
	# conn.commit()
	# print("Deleted:", cursor.execute("SELECT * FROM t").fetchall())  # READ

except sqlite3.IntegrityError as err:
	# Example: constraint failures (e.g., UNIQUE, NOT NULL).
	print(f"Integrity error: {err}")
except sqlite3.OperationalError as err:
	# Example: SQL syntax errors, missing tables, or locked database file.
	print(f"Operational error: {err}")
except sqlite3.Error as err:
	# Catch-all for any other SQLite errors.
	print(f"Database error: {err}")
finally:
	if conn:
		conn.close()  # Always close connections to release the file lock.

