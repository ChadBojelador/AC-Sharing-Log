"""Update helper for Activity 5."""

from data_module import DataModule


def update_session(data_module, session_id, name, date, duration):
    """Mutate an existing session via UPDATE using positional parameters."""
    conn = data_module.connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET name = ?, date = ?, duration = ? WHERE id = ?",
        (name, date, duration, session_id)
    )
    conn.commit()
    return cursor.rowcount
