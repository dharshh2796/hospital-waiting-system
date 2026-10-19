# CareQueue — Hospital Patient Waiting System

A beginner-friendly full-stack DSA project demonstrating the **Queue (FIFO)** data structure.

## Features
- Register patients with token numbers
- View the waiting list and patient status
- Call the next waiting patient in FIFO order
- Mark a consultation as completed
- Cancel a patient who is still waiting
- Store patient records in SQLite

## Technology stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python + Flask
- Database: SQLite
- DSA: Queue (First In, First Out)

## Run the project

1. Install Python 3.10 or newer.
2. Extract this ZIP and open a terminal in the `hospital_patient_waiting_system` folder.
3. Create and activate a virtual environment (recommended):

   **Windows**
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the application:
   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database (`patients.db`) is created automatically the first time the app starts.

## How the DSA works
1. A new patient receives the next token number and joins the end of the waiting line.
2. The backend collects patients whose status is `Waiting`, ordered by token.
3. `PatientQueue` uses Python's `collections.deque`; `popleft()` removes the first patient from the in-memory queue.
4. The selected patient is marked `In Consultation` in SQLite.
5. After the visit, the staff member marks the patient `Completed`.

Queue operations such as enqueue and dequeue are typically **O(1)**. Fetching and ordering the persistent waiting list depends on the database query and indexes.

## Suggested project presentation
- **Problem statement:** Hospitals need a clear, fair way to manage the order of patients waiting for consultation.
- **Objective:** Build a web-based patient queue dashboard using FIFO.
- **Input:** Patient name, age, department, and reason for visit.
- **Output:** Token number, waiting list, current status, and next patient.
- **Future enhancements:** Staff login, department-wise queues, estimated waiting time, priority handling for emergencies, printable tokens, and deployment.

## Important
This is an educational demo, not a clinical system. Use fictional data only. It does not provide medical triage or emergency prioritization. A real hospital system would need authentication, authorization, privacy/security controls, audit logging, backups, and a clinically approved process for urgent patients.
