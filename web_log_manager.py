"""
Web Log Manager (Flask)
-----------------------
CRUD web interface for managing records in the logs table.
"""

from flask import Flask, redirect, render_template_string, request, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)


def get_connection():
    """Open a database connection using local XAMPP defaults."""
    # Comparable to opening a PDO/MySQLi connection in PHP.
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="system_db",
    )


def ensure_logs_table(conn):
    """Create logs table if it does not exist."""
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message VARCHAR(255) NOT NULL,
            source VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.close()


def fetch_logs():
    """Fetch all rows for table rendering."""
    conn = None
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        # dictionary=True returns associative-style rows (like PDO::FETCH_ASSOC).
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, message, source, created_at FROM logs ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        if conn and conn.is_connected():
            conn.close()


PAGE_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Web Log Manager (Flask)</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --border: #e5e7eb;
      --primary: #2563eb;
      --danger: #dc2626;
      --success: #166534;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 28px;
    }
    .container {
      max-width: 1120px;
      margin: 0 auto;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
      padding: 22px;
    }
    h2 {
      margin: 0 0 4px;
      font-size: 28px;
    }
    .subtitle {
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 14px;
    }
    .create-form {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 6px;
    }
    .inline { display: inline-flex; gap: 8px; align-items: center; }
    input[type=text] {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 12px;
      width: 100%;
      max-width: 440px;
      font-size: 14px;
      background: #fff;
    }
    .cell-input {
      min-width: 280px;
      max-width: 100%;
    }
    button {
      border: 0;
      border-radius: 10px;
      padding: 9px 13px;
      color: white;
      font-size: 13px;
      cursor: pointer;
      background: var(--primary);
    }
    .btn-danger { background: var(--danger); }
    .status { margin: 10px 0 2px; font-weight: 600; color: var(--success); }
    .error { margin: 10px 0 2px; font-weight: 600; color: var(--danger); }
    .table-wrap {
      margin-top: 14px;
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      background: #fff;
    }
    table { border-collapse: collapse; width: 100%; }
    th, td {
      border-bottom: 1px solid var(--border);
      padding: 10px 12px;
      text-align: left;
      vertical-align: middle;
    }
    th {
      background: #f8fafc;
      font-size: 13px;
      letter-spacing: 0.2px;
    }
    tr:last-child td { border-bottom: 0; }
    .source-pill {
      display: inline-block;
      padding: 4px 9px;
      border-radius: 999px;
      background: #e5edff;
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
  <h2>Web Log Manager (Flask)</h2>
  

  <form class="create-form" method="post" action="/create">
    <label><strong>New Message</strong></label>
    <input type="text" name="message" required>
    <button type="submit">Create</button>
  </form>

  {% if status %}
    <p class="status">{{ status }}</p>
  {% endif %}
  {% if error %}
    <p class="error">{{ error }}</p>
  {% endif %}

  <div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Message</th>
        <th>Source</th>
        <th>Created At</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for row in rows %}
      <tr>
        <td>{{ row.id }}</td>
        <td>
          <form class="inline" method="post" action="/update/{{ row.id }}">
            <input class="cell-input" type="text" name="message" value="{{ row.message }}" required>
            <button type="submit">Update</button>
          </form>
        </td>
        <td><span class="source-pill">{{ row.source }}</span></td>
        <td>{{ row.created_at }}</td>
        <td>
          <form method="post" action="/delete/{{ row.id }}" onsubmit="return confirm('Delete record ID {{ row.id }}?');">
            <button class="btn-danger" type="submit">Delete</button>
          </form>
        </td>
      </tr>
      {% else %}
      <tr>
        <td colspan="5">No rows yet. Create your first record above.</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  </div>
  </div>
</body>
</html>
"""


def render_page(status="", error=""):
    """Render page with table data and optional messages."""
    rows = fetch_logs()
    return render_template_string(PAGE_TEMPLATE, rows=rows, status=status, error=error)


@app.route("/", methods=["GET"])
def index():
    status = request.args.get("status", "")
    return render_page(status=status)


@app.route("/create", methods=["POST"])
def create_record():
    """Create a new log record."""
    # Flask request.form is comparable to PHP $_POST.
    message = request.form.get("message", "").strip()
    if not message:
        return render_page(error="Please enter a message first.")

    conn = None
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        cursor = conn.cursor()
        # %s placeholders are prepared-statement style parameter slots.
        cursor.execute(
            "INSERT INTO logs (message, source) VALUES (%s, %s)",
            (message, "Web (Flask)"),
        )
        # commit() persists the write operation.
        conn.commit()
        cursor.close()
        return redirect(url_for("index", status="Record created successfully."))
    except Error as db_error:
        return render_page(error=f"Database Error: {db_error}")
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route("/update/<int:record_id>", methods=["POST"])
def update_record(record_id):
    """Update one record by ID."""
    # Similar to reading $_POST['message'] in PHP, but with .get() safety default.
    message = request.form.get("message", "").strip()
    if not message:
        return render_page(error="Updated message cannot be empty.")

    conn = None
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        cursor = conn.cursor()
        # WHERE clause restricts update to one ID.
        cursor.execute("UPDATE logs SET message = %s WHERE id = %s", (message, record_id))
        conn.commit()
        cursor.close()
        return redirect(url_for("index", status=f"Record ID {record_id} updated."))
    except Error as db_error:
        return render_page(error=f"Database Error: {db_error}")
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    """Delete one record by ID."""
    conn = None
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        cursor = conn.cursor()
        # Parameterized DELETE avoids SQL injection.
        cursor.execute("DELETE FROM logs WHERE id = %s", (record_id,))
        conn.commit()
        cursor.close()
        return redirect(url_for("index", status=f"Record ID {record_id} deleted."))
    except Error as db_error:
        return render_page(error=f"Database Error: {db_error}")
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
