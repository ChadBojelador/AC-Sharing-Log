# AC-Sharing-Log

Fair Air – AC Sharing Log is a small desktop application (Tkinter) that demonstrates a simple CRUD-backed activity logger for tracking AC/fan usage sessions. It is implemented in Python, uses SQLite for persistent storage, and is intended as an instructional example (Activity 5) showing how a GUI can drive database operations.

## About

This repository provides:
- A Tkinter-based GUI that allows users to create, read, update, search, and delete "usage session" records.
- A small modular codebase that separates storage (DataModule) from CRUD helpers and the UI.
- A single-file SQLite schema automatically created on first run.

The project was authored as an instructional exercise and branded as "Fair Air – AC Sharing Log" in support of energy-awareness use cases (SDG 7).

## Quick start

Prerequisites
- Python 3.8+ (tested with standard library modules)
- No third-party packages are required (uses builtin `sqlite3` and `tkinter`)

Run
1. Clone the repository
   git clone https://github.com/ChadBojelador/AC-Sharing-Log.git
   cd AC-Sharing-Log
2. Start the app:
   python main.py

On first run the SQLite database file (`fairairDB.db`) will be created in the working directory and the sessions table will be initialized.

## Project layout

- main.py — Tkinter GUI application (entry point). Builds the window, controls, table view, and orchestrates CRUD operations via the helper modules. Window title: "Fair Air – AC Sharing Log (Activity 5)".  
- data_module.py — Database connectivity and schema management. Exposes `DataModule` which manages a single SQLite connection and ensures the schema exists. Default DB filename: `fairairDB.db`.  
- create_module.py — create helper: create_session(data_module, name, date, duration) -&gt; lastrowid.  
- readandsearch_module.py — read/search helpers: fetch_all_sessions(data_module) and search_sessions_by_name(data_module, keyword), both return rows as tuples.  
- update_module.py — update helper: update_session(data_module, session_id, name, date, duration) -&gt; number of affected rows.  
- delete_module.py — delete helper (used by main UI) to remove sessions (imported by main.py).

## Design

### Architecture
- Single-process desktop app composed of:
  - UI layer (main.py) — event-driven Tkinter application. Handles user input, validation, and table rendering.
  - Storage layer (data_module.DataModule) — a thin wrapper around sqlite3 that ensures the schema is created and exposes a connection.
  - CRUD helpers (create_module, readandsearch_module, update_module, delete_module) — small functions that accept a DataModule instance and execute parameterized SQL queries.

The UI calls the CRUD helpers directly and refreshes the view after each operation.

### Data model / schema
The database contains one table `sessions`:

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  date TEXT NOT NULL,
  duration INTEGER NOT NULL
);

- id: integer primary key (autoincrement)
- name: text, event/session owner or label
- date: text, stored as a string (ISO or the format the UI uses)
- duration: integer, session length (units are defined by the UI/owner, e.g., minutes)

The schema is created automatically by DataModule on connect.

### Key functions &amp; interfaces
- DataModule(db_name=DB_NAME)
  - connect() -&gt; sqlite3.Connection (creates DB file and schema on first connect)
  - close()

- create_session(data_module, name, date, duration) -&gt; int
  - INSERT INTO sessions (name, date, duration) VALUES (?, ?, ?)
  - Returns last inserted row id

- fetch_all_sessions(data_module) -&gt; list[tuple]
  - SELECT id, name, date, duration FROM sessions ORDER BY id DESC

- search_sessions_by_name(data_module, keyword) -&gt; list[tuple]
  - Case-insensitive LIKE on name: WHERE LOWER(name) LIKE ?

- update_session(data_module, session_id, name, date, duration) -&gt; int
  - UPDATE sessions SET name = ?, date = ?, duration = ? WHERE id = ?
  - Returns affected rowcount

- delete_session(data_module, session_id) -&gt; int
  - (Exists in repository; deletes a session by id and returns affected rows)

### Control flow examples
- Create:
  - UI collects name, date, duration → calls create_session(...) → commit → UI reloads table (fetch_all_sessions).
- Read / Search:
  - UI calls fetch_all_sessions to populate the table.
  - When the search box is used, UI calls search_sessions_by_name with the entered keyword and updates the table.
- Update:
  - UI populates edit fields from the selected table row → user edits → UI calls update_session and reloads table.
- Delete:
  - UI confirms deletion, calls delete_session, and reloads table.

### Error handling &amp; validation
- The modules use parameterized SQL (question marks) to prevent SQL injection.
- DataModule ensures schema availability; sqlite3 exceptions will propagate to the caller (main.py) unless caught.
- The GUI contains basic validation and ensures the database connection is closed on window close.
- For production or extended use, add:
  - explicit input validation (date format, duration numeric range)
  - try/except blocks around DB operations with user-facing error messages
  - migrations or a schema-versioning approach for schema changes

### Extensibility
- Adding fields: update SCHEMA_SQL in data_module.py and migration logic. Update CRUD helper SQL statements and UI fields.
- Changing backend: replace DataModule with an implementation that exposes the same connect/close surface and update helpers to use a different DB library or remote API.
- Expose a CLI or REST API by factoring the CRUD helpers into a service layer.

## Usage examples (programmatic)

As a quick example (Python REPL or script), you can import helpers and use them:

```python
from data_module import DataModule
from create_module import create_session
from readandsearch_module import fetch_all_sessions

dm = DataModule()
dm.connect()
new_id = create_session(dm, "Bedroom AC", "2025-12-14", 45)
rows = fetch_all_sessions(dm)
print(rows)
dm.close()
```

## UI notes

- The GUI is designed and branded in main.py with a fixed color palette and a large window by default (geometry 1920x1080 and attempts to maximize). Title text and subtitle indicate the SDG/energy-awareness context.
- The UI supports:
  - Input fields for name, date, and duration
  - Action buttons for Create, Update, Delete
  - A searchable table view showing sessions (id, name, date, duration)
  - Graceful DB close on window exit

## Development

- No tests are included; add unit tests for the CRUD helpers and integration tests that use a temporary SQLite file for isolation.
- Recommended tooling:
  - Python formatting: black
  - Linting: flake8 or pylint
- Suggested branches:
  - main — stable
  - feature/* — new features and improvements

## Contributing

- Fork the repo and open a pull request with your changes.
- If you add/modify the database schema, include migration steps or a script to recreate/migrate data.

## Troubleshooting

- If the app fails to start, confirm:
  - Python version is compatible and tkinter is available in your environment.
  - The working directory is writable to allow creating `fairairDB.db`.
- If schema changes are made, you may need to delete the DB file and re-run to recreate the schema (or implement migrations).

## License

No license file is included in the repository. Add a LICENSE (for example MIT) to clarify permissions.

## Contact

Repository owner: ChadBojelador
Co-Developer: Czantelle Villena
(You can add contact details or project maintainers here.)

---

Files referenced:
- https://github.com/ChadBojelador/AC-Sharing-Log/blob/main/main.py
- https://github.com/ChadBojelador/AC-Sharing-Log/blob/main/data_module.py
- https://github.com/ChadBojelador/AC-Sharing-Log/blob/main/create_module.py
- https://github.com/ChadBojelador/AC-Sharing-Log/blob/main/readandsearch_module.py
- https://github.com/ChadBojelador/AC-Sharing-Log/blob/main/update_module.py
- https://github.com/ChadBojelador/AC-Sharing-Log/blob/main/delete_module.py
