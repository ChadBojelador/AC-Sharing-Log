"""Create helper for Activity 5."""

from data_module import DataModule


def create_session(data_module, name, date, duration):
    """Persist a new session record via parameterized INSERT."""
    conn = data_module.connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (name, date, duration) VALUES (?, ?, ?)",
        (name, date, duration)
    )
    conn.commit()
    return cursor.lastrowid
