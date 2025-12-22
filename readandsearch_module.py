"""Read + search helpers for Activity 5."""

from data_module import DataModule


def fetch_all_sessions(data_module):
    """Return every persisted session ordered by descending identifier."""
    conn = data_module.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, date, duration FROM sessions ORDER BY id DESC")
    return cursor.fetchall()


def search_sessions_by_name(data_module, keyword):
    """Perform a LIKE-based lookup constrained to the name column."""
    conn = data_module.connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, date, duration FROM sessions WHERE LOWER(name) LIKE ? ORDER BY id DESC",
        (f"%{keyword.lower()}%",)
    )
    return cursor.fetchall()
