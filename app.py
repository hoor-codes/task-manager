from flask import Flask, jsonify, request, send_from_directory
import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return jsonify({
        "message": "Task Manager API is running"
    })


@app.route("/app")
def frontend():
    return send_from_directory(".", "index.html")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()

    tasks = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    return jsonify([dict(task) for task in tasks])


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()

    title = data.get("title")

    if not title:
        return jsonify({
            "error": "Title is required"
        }), 400

    conn = get_db()

    cursor = conn.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,)
    )

    conn.commit()

    task_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "message": "Task added",
        "id": task_id,
        "title": title
    }), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    if task is None:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    title = data.get("title")
    completed = data.get("completed")

    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()

        return jsonify({
            "error": "Task not found"
        }), 404

    conn.execute(
        "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
        (title, completed, task_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task updated"
    })


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()

        return jsonify({
            "error": "Task not found"
        }), 404

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task deleted"
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)