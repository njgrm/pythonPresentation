"""
Desktop Log Manager (Tkinter)
-----------------------------
CRUD desktop interface for managing records in the logs table.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import mysql.connector
from mysql.connector import Error


def get_connection():
    """Open a database connection using local XAMPP defaults."""
    # Comparable to creating a PDO/MySQLi connection in PHP.
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="system_db",
    )


def ensure_logs_table(conn):
    """Create logs table if it does not exist."""
    # conn is the active DB connection passed into this function.
    # cursor is the object that sends SQL commands through that connection.
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


def clear_form():
    """Reset selected record and message input."""
    selected_id_var.set("")  # Tkinter StringVar: set displayed value in bound input.
    message_entry.delete(0, tk.END)  # Tkinter Entry: delete text from index 0 to END.


def refresh_table():
    """Load rows from database and redraw the table."""
    # First clear old UI rows so we repaint from fresh DB data.
    for item in logs_table.get_children():
        logs_table.delete(item)  # Treeview API: remove one row by item id.

    conn = None  # Start with no connection; set it in try.
    try:
        conn = get_connection()  # Open DB connection for this action.
        ensure_logs_table(conn)
        # dictionary=True returns named columns (row["message"]) instead of index positions.
        cursor = conn.cursor(dictionary=True)
        # ORDER BY id DESC shows newest entries first.
        cursor.execute("SELECT id, message, source, created_at FROM logs ORDER BY id DESC")
        rows = cursor.fetchall()  # Get all query results into a Python list.
        cursor.close()

        for row in rows:
            logs_table.insert(
                "",
                tk.END,
                values=(row["id"], row["message"], row["source"], row["created_at"]),
            )  # Treeview insert: values must match declared column order.
    except Error as db_error:
        messagebox.showerror("Database Error", str(db_error))
    finally:
        if conn and conn.is_connected():
            conn.close()


def create_log():
    """Insert a new row from the message input."""
    message = message_entry.get().strip()  # Entry.get() reads current text; strip() removes extra spaces.
    if not message:
        messagebox.showwarning("Input Needed", "Please type a message first.")
        return

    conn = None  # Start with no connection; set it in try.
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        cursor = conn.cursor()  # New cursor for this write operation.
        # %s are SQL placeholders; values are passed separately for safety.
        cursor.execute(
            "INSERT INTO logs (message, source) VALUES (%s, %s)",
            (message, "Desktop (Tkinter)"),
        )
        conn.commit()  # Save change permanently.
        cursor.close()
        clear_form()
        refresh_table()
        messagebox.showinfo("Created", "Record inserted successfully.")
    except Error as db_error:
        messagebox.showerror("Database Error", str(db_error))
    finally:
        if conn and conn.is_connected():
            conn.close()


def update_log():
    """Update the selected row message."""
    record_id = selected_id_var.get().strip()  # StringVar.get() reads value from bound "Selected ID" field.
    message = message_entry.get().strip()

    if not record_id:
        messagebox.showwarning("No Selection", "Select a row from the table first.")
        return
    if not message:
        messagebox.showwarning("Input Needed", "Please type an updated message.")
        return

    conn = None  # Start with no connection; set it in try.
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        cursor = conn.cursor()
        # WHERE id = %s means update only one selected record.
        cursor.execute("UPDATE logs SET message = %s WHERE id = %s", (message, int(record_id)))
        # int(record_id) converts UI text into numeric ID expected by SQL.
        conn.commit()  # Save change permanently.
        cursor.close()
        clear_form()
        refresh_table()
        messagebox.showinfo("Updated", f"Record ID {record_id} updated.")
    except Error as db_error:
        messagebox.showerror("Database Error", str(db_error))
    finally:
        if conn and conn.is_connected():
            conn.close()


def delete_log():
    """Delete the selected row."""
    record_id = selected_id_var.get().strip()  # Read selected row ID from bound StringVar.
    if not record_id:
        messagebox.showwarning("No Selection", "Select a row from the table first.")
        return

    if not messagebox.askyesno("Confirm Delete", f"Delete record ID {record_id}?"):
        return

    conn = None  # Start with no connection; set it in try.
    try:
        conn = get_connection()
        ensure_logs_table(conn)
        cursor = conn.cursor()
        # Single-value tuple needs a trailing comma: (int(record_id),)
        cursor.execute("DELETE FROM logs WHERE id = %s", (int(record_id),))
        conn.commit()  # Save delete permanently.
        cursor.close()
        clear_form()
        refresh_table()
        messagebox.showinfo("Deleted", f"Record ID {record_id} deleted.")
    except Error as db_error:
        messagebox.showerror("Database Error", str(db_error))
    finally:
        if conn and conn.is_connected():
            conn.close()


def on_row_select(_event):
    """Copy selected row values into the form."""
    selection = logs_table.selection()  # Returns selected Treeview item id(s), not row data yet.
    if not selection:
        return
    selected_values = logs_table.item(selection[0], "values")  # item(..., "values") gets displayed row tuple.
    if not selected_values:
        return

    selected_id_var.set(str(selected_values[0]))  # Keep ID as string for Entry/StringVar compatibility.
    message_entry.delete(0, tk.END)
    message_entry.insert(0, str(selected_values[1]))  # Entry.insert(index, text): index 0 means beginning.


# This file is intended to run directly as a desktop app.
# If imported elsewhere, this block still runs because it is top-level UI setup.
app = tk.Tk()
app.title("Desktop Log Manager (Tkinter)")
app.geometry("980x560")
app.minsize(900, 520)
app.configure(bg="#f4f7fb")

style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure("Root.TFrame", background="#f4f7fb")
style.configure("Card.TFrame", background="#ffffff")
style.configure("Title.TLabel", background="#ffffff", foreground="#1f2937", font=("Segoe UI", 16, "bold"))
style.configure("Subtitle.TLabel", background="#ffffff", foreground="#6b7280", font=("Segoe UI", 10))
style.configure("Field.TLabel", background="#ffffff", foreground="#374151", font=("Segoe UI", 10, "bold"))
style.configure("TEntry", padding=6)
style.configure("TButton", padding=(12, 7), font=("Segoe UI", 10))
style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

root_frame = ttk.Frame(app, style="Root.TFrame", padding=18)
root_frame.pack(fill="both", expand=True)

card_frame = ttk.Frame(root_frame, style="Card.TFrame", padding=16)
card_frame.pack(fill="both", expand=True)

header_frame = ttk.Frame(card_frame, style="Card.TFrame")
header_frame.pack(fill="x", pady=(0, 12))
ttk.Label(header_frame, text="Desktop Log Manager (Tkinter)", style="Title.TLabel").pack(anchor="w")
ttk.Label(
    header_frame,
    style="Subtitle.TLabel",
).pack(anchor="w", pady=(2, 0))

form_frame = ttk.Frame(card_frame, style="Card.TFrame")
form_frame.pack(fill="x", pady=(0, 8))

ttk.Label(form_frame, text="Selected ID", style="Field.TLabel").grid(row=0, column=0, sticky="w")
selected_id_var = tk.StringVar()
selected_id_entry = ttk.Entry(form_frame, textvariable=selected_id_var, width=12, state="readonly")
selected_id_entry.grid(row=1, column=0, padx=(0, 18), pady=(4, 0), sticky="w")

ttk.Label(form_frame, text="Message", style="Field.TLabel").grid(row=0, column=1, sticky="w")
message_entry = ttk.Entry(form_frame, width=70)
message_entry.grid(row=1, column=1, padx=(0, 8), pady=(4, 0), sticky="ew")
form_frame.columnconfigure(1, weight=1)

button_frame = ttk.Frame(card_frame, style="Card.TFrame")
button_frame.pack(fill="x", pady=(6, 12))

ttk.Button(button_frame, text="Create", command=create_log).pack(side="left", padx=(0, 8))
ttk.Button(button_frame, text="Update", command=update_log).pack(side="left", padx=(0, 8))
ttk.Button(button_frame, text="Delete", command=delete_log).pack(side="left", padx=(0, 8))
ttk.Button(button_frame, text="Refresh", command=refresh_table).pack(side="left", padx=(0, 8))
ttk.Button(button_frame, text="Clear", command=clear_form).pack(side="left")

table_frame = ttk.Frame(card_frame, style="Card.TFrame")
table_frame.pack(fill="both", expand=True)

columns = ("id", "message", "source", "created_at")
logs_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
logs_table.heading("id", text="ID")
logs_table.heading("message", text="Message")
logs_table.heading("source", text="Source")
logs_table.heading("created_at", text="Created At")

logs_table.column("id", width=80, anchor="center")
logs_table.column("message", width=460, anchor="w")
logs_table.column("source", width=180, anchor="center")
logs_table.column("created_at", width=220, anchor="center")

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=logs_table.yview)
logs_table.configure(yscrollcommand=scrollbar.set)

logs_table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

logs_table.bind("<<TreeviewSelect>>", on_row_select)
refresh_table()

app.mainloop()
