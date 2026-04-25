# MySQL CRUD Demo Setup Guide (XAMPP + Python)

Practical setup guide for a working MySQL CRUD presentation using:
- `db_crud_demo.py` (CLI demo)
- `desktop_log_manager.py` (Tkinter desktop app)
- `web_log_manager.py` (Flask web app)

---

## 1) Install Requirements

1. Install **XAMPP**  
   [https://www.apachefriends.org/download.html](https://www.apachefriends.org/download.html)
2. Install **Python 3.x**  
   [https://www.python.org/downloads/](https://www.python.org/downloads/)
3. Install Python packages:

```powershell
py -m pip install mysql-connector-python flask
```

---

## 2) Configure Database in phpMyAdmin

1. Open XAMPP Control Panel
2. Start `Apache` and `MySQL`
3. Open [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
4. Create database: `system_db`
5. Run this SQL in the SQL tab:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    source VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3) Run the Apps

### CLI CRUD demo

```powershell
python .\db_crud_demo.py
```

### Desktop CRUD app (Tkinter)

```powershell
python .\desktop_log_manager.py
```

### Web CRUD app (Flask)

```powershell
python .\web_log_manager.py
```

Then open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 4) Quick Demo Flow (2 minutes)

1. Start MySQL in XAMPP
2. Open desktop or web app
3. Create a row
4. Show row appears in the table
5. Update same row
6. Delete row
7. Verify changes in phpMyAdmin `logs` table

---

## 5) Troubleshooting

- `Unknown database 'system_db'`
  - Create `system_db` in phpMyAdmin
- `No module named mysql`
  - Run `py -m pip install mysql-connector-python`
- `No module named flask`
  - Run `py -m pip install flask`
- `Access denied for user 'root'`
  - Check credentials in the scripts and XAMPP config
