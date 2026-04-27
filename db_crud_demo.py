"""
MySQL CRUD CLI Demo
-------------------
Simple command-line script for testing MySQL connection and CRUD functions.
"""

import mysql.connector
from mysql.connector import Error


def get_connection():
    """Open a database connection using local XAMPP defaults."""
    # Similar to creating a PDO/MySQLi connection in PHP:
    # $pdo = new PDO("mysql:host=localhost;dbname=system_db", "root", "");
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="system_db",
    )


def create_table_if_missing(conn):
    """Create the users table when it is not present."""
    # Cursor executes SQL for this active connection.
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE
        )
        """
    )
    conn.commit()
    cursor.close()


def create_user(conn, name, email):
    """Insert one user record."""
    cursor = conn.cursor()
    # %s are SQL parameter placeholders (not Python string formatting).
    query = "INSERT INTO users (username, email) VALUES (%s, %s)"
    # Values are passed separately so user input is treated as data, not SQL code.
    cursor.execute(query, (name, email))
    # commit() makes INSERT/UPDATE/DELETE changes permanent.
    conn.commit()
    print(f"[CREATE] Added user: {name} | {email}")
    cursor.close()


def read_users(conn):
    """Read and print all users."""
    # dictionary=True lets us access columns by name (row["email"]) instead of indexes.
    cursor = conn.cursor(dictionary=True)
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
    query = "UPDATE users SET email = %s WHERE id = %s"
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
    query = "DELETE FROM users WHERE id = %s"
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
        print("Connected to MySQL. Table is ready.")

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
    except Error as db_error:
        print(f"Database error: {db_error}")
        print("Check: XAMPP MySQL is running, system_db exists, and connector is installed.")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":  # __name__ == "__main__" means this file is run directly, not imported.
    run_app()
