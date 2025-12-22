"""SQLite connectivity utilities for Activity 5."""

import sqlite3

DB_NAME = "fairairDB.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    duration INTEGER NOT NULL
);
"""


class DataModule:
    """Maintains a single SQLite connection and ensures schema availability."""

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """Initialize the connection and execute schema migrations if required."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.execute(SCHEMA_SQL)
            self.connection.commit()
        return self.connection

    def close(self):
        """Dispose of the connection handle to flush pending operations."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
