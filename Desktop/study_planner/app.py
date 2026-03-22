from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# -------------------------------
# 📌 Database Connection
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# 📌 Initialize Database
# -------------------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            deadline TEXT,
            priority TEXT,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


# -------------------------------
# 🏠 Dashboard Route
# -------------------------------
@app.route("/")
def index():
    conn = get_db_connection()

    tasks = conn.execute("""
        SELECT * FROM tasks
        ORDER BY completed ASC, created_at DESC
    """).fetchall()

    # 📊 Stats
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    pending = total - completed

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending
    )


# -------------------------------
# ➕ Add Task
# -------------------------------
@app.route("/add", methods=["POST"])
def add_task():
    content = request.form.get("content")
    deadline = request.form.get("deadline")
    priority = request.form.get("priority")

    if content:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tasks (content, deadline, priority) VALUES (?, ?, ?)",
            (content, deadline, priority)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("index"))


# -------------------------------
# ❌ Delete Task
# -------------------------------
@app.route("/delete/<int:id>")
def delete_task(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# -------------------------------
# ✅ Toggle Complete
# -------------------------------
@app.route("/toggle/<int:id>")
def toggle_task(id):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT completed FROM tasks WHERE id = ?", (id,)
    ).fetchone()

    new_status = 0 if task["completed"] else 1

    conn.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (new_status, id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("index"))


# -------------------------------
# 🚀 Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)