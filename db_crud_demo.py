"""
SQLite CRUD CLI Demo
--------------------
Simple command-line script for testing SQLite connection and CRUD functions.
"""

import sqlite3


def get_connection():
    """Open a database connection using a local SQLite file."""
    # SQLite stores data in a single file (like a lightweight local DB).
    # The file will be created automatically if it does not exist.
    return sqlite3.connect("system_db.sqlite")


def create_table_if_missing(conn):
    """Create the users table when it is not present."""
    # Cursor executes SQL for this active connection.
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.commit()
    cursor.close()


def create_user(conn, name, email):
    """Insert one user record."""
    cursor = conn.cursor()
    # ? are SQLite parameter placeholders (not Python string formatting).
    # This is the CREATE in CRUD.
    query = "INSERT INTO users (username, email) VALUES (?, ?)"
    # Values are passed separately so user input is treated as data, not SQL code.
    cursor.execute(query, (name, email))
    # commit() makes INSERT/UPDATE/DELETE changes permanent.
    conn.commit()
    print(f"[CREATE] Added user: {name} | {email}")
    cursor.close()


def read_users(conn):
    """Read and print all users."""
    # The row factory lets us access columns by name (row["email"]).
    # This is the READ in CRUD.
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM users ORDER BY id ASC"
    cursor.execute(query)
    rows = cursor.fetchall()  # Collect all result rows into a Python list.
    print("[READ] Current users:")
    if not rows:
        print("  (no rows yet)")
    for row in rows:
        print(f"  ID={row['id']} | username={row['username']} | email={row['email']}")
    cursor.close()


def update_email(conn, user_id, new_email):
    """Update one user email by ID."""
    cursor = conn.cursor()
    # WHERE limits update to one target row.
    # This is the UPDATE in CRUD.
    query = "UPDATE users SET email = ? WHERE id = ?"
    cursor.execute(query, (new_email, user_id))
    conn.commit()
    if cursor.rowcount == 0:  # rowcount shows how many rows were actually changed.
        print(f"[UPDATE] No user found for ID={user_id}.")
    else:
        print(f"[UPDATE] Updated user ID={user_id} with new email={new_email}")
    cursor.close()


def delete_user(conn, user_id):
    """Delete one user by ID."""
    cursor = conn.cursor()
    # Keep WHERE in DELETE to avoid removing every row.
    # This is the DELETE in CRUD.
    query = "DELETE FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    conn.commit()
    if cursor.rowcount == 0:  # rowcount == 0 usually means ID was not found.
        print(f"[DELETE] No user found for ID={user_id}.")
    else:
        print(f"[DELETE] Deleted user with ID={user_id}")
    cursor.close()


def print_menu():
    """Display the main CLI actions."""
    print("\n=== User CRUD Menu ===")
    print("1) Create user")
    print("2) Read users")
    print("3) Update user email")
    print("4) Delete user")
    print("5) Exit")


def prompt_int(prompt_text):
    """Read an integer from input with retry on invalid input."""
    while True:
        raw_value = input(prompt_text).strip()
        if raw_value.isdigit():
            return int(raw_value)
        print("Invalid number. Please enter a valid numeric ID.")


def prompt_text_or_cancel(prompt_text):
    """Read text input and allow cancel using C."""
    value = input(prompt_text).strip()
    if value.lower() == "c":
        return None
    return value


def prompt_int_or_cancel(prompt_text):
    """Read integer input and allow cancel using C."""
    while True:
        raw_value = input(prompt_text).strip()
        if raw_value.lower() == "c":
            return None
        if raw_value.isdigit():
            return int(raw_value)
        print("Invalid number. Please enter a valid numeric ID or C to cancel.")


def prompt_confirm_or_cancel(prompt_text):
    """Read yes/no confirmation and allow cancel using C."""
    while True:
        value = input(prompt_text).strip().lower()
        if value in {"y", "n", "c"}:
            return value
        print("Please enter Y, N, or C.")


def run_app():
    """Run an interactive CRUD terminal session."""
    conn = None  # Start with no connection yet.
    try:
        conn = get_connection()  # Create one reusable connection for this session.
        create_table_if_missing(conn)
        print("Connected to SQLite. Table is ready.")

        while True:  # Keep session running until user chooses Exit.
            print_menu()
            choice = input("Select an option (1-5): ").strip()

            if choice == "1":
                print("Create user (type C anytime to cancel).")
                name = prompt_text_or_cancel("Enter username: ")
                if name is None:
                    print("Create cancelled.")
                    continue
                email = prompt_text_or_cancel("Enter email: ")
                if email is None:
                    print("Create cancelled.")
                    continue
                if not name or not email:
                    print("Username and email are required.")
                    continue
                create_user(conn, name, email)

            elif choice == "2":
                read_users(conn)
                input("Press Enter to return to menu...")

            elif choice == "3":
                # Auto-show current rows so user can choose ID immediately.
                read_users(conn)
                print("Update user (type C anytime to cancel).")
                user_id = prompt_int_or_cancel("Enter user ID to update: ")
                if user_id is None:
                    print("Update cancelled.")
                    continue
                new_email = prompt_text_or_cancel("Enter new email: ")
                if new_email is None:
                    print("Update cancelled.")
                    continue
                if not new_email:
                    print("Email cannot be empty.")
                    continue
                confirm = prompt_confirm_or_cancel(f"Confirm update for ID {user_id}? (Y/N/C): ")
                if confirm == "c":
                    print("Update cancelled.")
                    continue
                if confirm == "y":
                    update_email(conn, user_id, new_email)
                else:
                    print("Update cancelled.")

            elif choice == "4":
                # Auto-show current rows so user can choose ID immediately.
                read_users(conn)
                print("Delete user (type C anytime to cancel).")
                user_id = prompt_int_or_cancel("Enter user ID to delete: ")
                if user_id is None:
                    print("Delete cancelled.")
                    continue
                confirm = prompt_confirm_or_cancel(f"Confirm delete for ID {user_id}? (Y/N/C): ")
                if confirm == "c":
                    print("Delete cancelled.")
                    continue
                if confirm == "y":
                    delete_user(conn, user_id)
                else:
                    print("Delete cancelled.")

            elif choice == "5":
                print("Exiting session. Goodbye.")
                break

            else:
                print("Invalid option. Choose 1, 2, 3, 4, or 5.")
    except sqlite3.IntegrityError as db_error:
        # Example: UNIQUE constraint failed when inserting a duplicate email.
        print(f"Integrity error (constraint violation): {db_error}")
        print("Check: duplicate email, missing required data, or invalid ID.")
    except sqlite3.OperationalError as db_error:
        # Example: wrong SQL, missing table, or locked database file.
        print(f"Operational error (SQL/DB state): {db_error}")
        print("Check: SQL syntax, table exists, or file permissions.")
    except sqlite3.Error as db_error:
        # Catch-all for any other SQLite-related errors.
        print(f"Database error: {db_error}")
        print("Check: SQLite file path and database accessibility.")
    finally:
        if conn:
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":  # __name__ == "__main__" means this file is run directly, not imported.
    run_app()
