"""Delete helper for Activity 5."""

from data_module import DataModule


def delete_session(data_module, session_id):
    """Issue a single-row DELETE operation keyed by the primary identifier."""
    conn = data_module.connect()
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
