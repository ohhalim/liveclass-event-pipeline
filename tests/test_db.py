from db import setup_database


def test_get_connection(db_conn):
    assert db_conn.closed == 0


def test_setup_database_creates_events_table(db_conn):
    cur = db_conn.cursor()
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'events'
        ORDER BY ordinal_position
    """)
    columns = {row[0] for row in cur.fetchall()}
    cur.close()

    expected = {
        "id", "event_type", "user_id", "session_id",
        "lecture_id", "page_url", "amount", "error_code", "created_at",
    }
    assert expected == columns


def test_setup_database_is_idempotent():
    setup_database()
    setup_database()
