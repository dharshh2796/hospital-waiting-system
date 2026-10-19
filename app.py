from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
from collections import deque

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("patients.db")


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                department TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Waiting',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


class PatientQueue:
    """FIFO queue: patients are served in the order they joined."""
    def __init__(self, patients):
        self._items = deque(patients)

    def next_patient(self):
        return self._items.popleft() if self._items else None


def get_patients():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM patients ORDER BY token ASC"
        ).fetchall()
    return [dict(row) for row in rows]


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/patients")
def list_patients():
    return jsonify(get_patients())


@app.post("/api/patients")
def add_patient():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    department = str(data.get("department", "")).strip()
    reason = str(data.get("reason", "")).strip()
    try:
        age = int(data.get("age", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Enter a valid age."}), 400

    if not name or not department or not reason:
        return jsonify({"error": "Please complete all fields."}), 400
    if age < 1 or age > 120:
        return jsonify({"error": "Age must be between 1 and 120."}), 400

    with connect_db() as conn:
        row = conn.execute("SELECT COALESCE(MAX(token), 0) + 1 AS next_token FROM patients").fetchone()
        token = row["next_token"]
        conn.execute(
            "INSERT INTO patients (token, name, age, department, reason) VALUES (?, ?, ?, ?, ?)",
            (token, name, age, department, reason)
        )
    return jsonify({"message": "Patient added to queue.", "token": token}), 201


@app.post("/api/next")
def call_next():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT id, token, name FROM patients WHERE status = 'Waiting' ORDER BY token ASC"
        ).fetchall()
        queue = PatientQueue([dict(row) for row in rows])
        patient = queue.next_patient()

        if patient is None:
            return jsonify({"error": "There are no patients waiting."}), 404

        conn.execute(
            "UPDATE patients SET status = 'In Consultation' WHERE id = ?",
            (patient["id"],)
        )
    return jsonify({"message": "Next patient called.", "patient": patient})


@app.post("/api/patients/<int:patient_id>/complete")
def complete_patient(patient_id):
    with connect_db() as conn:
        row = conn.execute(
            "SELECT id, status FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Patient not found."}), 404
        if row["status"] != "In Consultation":
            return jsonify({"error": "Only a patient in consultation can be completed."}), 400
        conn.execute(
            "UPDATE patients SET status = 'Completed' WHERE id = ?", (patient_id,)
        )
    return jsonify({"message": "Visit marked as completed."})


@app.post("/api/patients/<int:patient_id>/remove")
def remove_patient(patient_id):
    # Demo-only cancellation: only waiting patients can be removed.
    with connect_db() as conn:
        row = conn.execute(
            "SELECT status FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "Patient not found."}), 404
        if row["status"] != "Waiting":
            return jsonify({"error": "Only waiting patients can be removed."}), 400
        conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    return jsonify({"message": "Patient removed from the waiting queue."})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
