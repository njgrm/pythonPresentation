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
    # cursor() is the query runner for one DB session.
    # PHP equivalent: $stmt = $pdo->prepare("SQL...");
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
    # %s placeholders are parameter slots, not Python string formatting.
    # They work like ? placeholders in PDO prepared statements.
    query = "INSERT INTO users (username, email) VALUES (%s, %s)"
    # Second argument is a tuple of values bound safely to placeholders.
    # PHP equivalent: $stmt->execute([$name, $email]);
    cursor.execute(query, (name, email))
    # commit() makes the write permanent (similar to successful transaction commit in SQL/PHP).
    conn.commit()
    print(f"[CREATE] Added user: {name} | {email}")
    cursor.close()


def read_users(conn):
    """Read and print all users."""
    # dictionary=True returns rows as dicts:
    # {"id": 1, "username": "...", "email": "..."}
    # Similar to PDO::FETCH_ASSOC in PHP.
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users ORDER BY id ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    print("[READ] Current users:")
    if not rows:
        print("  (no rows yet)")
    for row in rows:
        print(f"  ID={row['id']} | username={row['username']} | email={row['email']}")
    cursor.close()


def update_email(conn, user_id, new_email):
    """Update one user email by ID."""
    cursor = conn.cursor()
    # WHERE limits update to a single target row.
    query = "UPDATE users SET email = %s WHERE id = %s"
    cursor.execute(query, (new_email, user_id))
    conn.commit()
    print(f"[UPDATE] Updated user ID={user_id} with new email={new_email}")
    cursor.close()


def delete_user(conn, user_id):
    """Delete one user by ID."""
    cursor = conn.cursor()
    # Keep WHERE in DELETE to avoid removing every row.
    query = "DELETE FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    conn.commit()
    print(f"[DELETE] Deleted user with ID={user_id}")
    cursor.close()


def run_demo():
    """Run a short demo flow."""
    conn = None
    try:
        conn = get_connection()
        create_table_if_missing(conn)

        create_user(conn, "Alice", "alice@example.com")
        read_users(conn)

        # update_email(conn, 1, "alice_new@example.com")
        # read_users(conn)

        # delete_user(conn, 1)
        # read_users(conn)

        print("\nCRUD demo completed successfully.")
    except Error as db_error:
        print(f"Database error: {db_error}")
        print("Check: XAMPP MySQL is running, system_db exists, and connector is installed.")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Connection closed.")


if __name__ == "__main__":
    run_demo()
