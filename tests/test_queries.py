"""집계 분석 계층(queries.sql) 검증.

각 테스트는 db_conn 롤백 픽스처 안에서 TRUNCATE 후 알려진 데이터를 넣어
쿼리 결과가 기대값과 일치하는지 본다. (save_events round-trip만 실제 커밋 후 정리)
"""

from datetime import datetime, timedelta

from db import get_connection
from event_generator import save_events
from queries import QUERIES

INSERT_SQL = """
    INSERT INTO events (event_type, user_id, session_id, created_at)
    VALUES (%s, %s, %s, %s)
"""


def _insert(cur, rows):
    """rows: list of (event_type, user_id, created_at)"""
    cur.executemany(INSERT_SQL, [(et, uid, "sess", ts) for et, uid, ts in rows])


def test_event_type_counts(db_conn):
    cur = db_conn.cursor()
    cur.execute("TRUNCATE events")
    now = datetime.now()
    _insert(cur, [
        ("page_view", "U1", now),
        ("page_view", "U1", now),
        ("page_view", "U2", now),
        ("error", "U1", now),
    ])

    cur.execute(QUERIES["event_type_counts"])
    result = dict(cur.fetchall())

    assert result == {"page_view": 3, "error": 1}


def test_top10_users_by_activity(db_conn):
    cur = db_conn.cursor()
    cur.execute("TRUNCATE events")
    now = datetime.now()
    rows = (
        [("page_view", "U1", now)] * 5
        + [("page_view", "U2", now)] * 3
        + [("page_view", "U3", now)] * 1
    )
    _insert(cur, rows)

    cur.execute(QUERIES["top10_users_by_activity"])
    result = cur.fetchall()

    assert result[0] == ("U1", 5)
    assert len(result) == 3
    counts = [count for _, count in result]
    assert counts == sorted(counts, reverse=True)


def test_event_type_ratio(db_conn):
    cur = db_conn.cursor()
    cur.execute("TRUNCATE events")
    now = datetime.now()
    _insert(cur, [("page_view", "U1", now)] * 3 + [("error", "U1", now)] * 1)

    cur.execute(QUERIES["event_type_ratio"])
    rows = cur.fetchall()  # (event_type, count, percentage)

    counts = {event_type: count for event_type, count, _ in rows}
    assert counts == {"page_view": 3, "error": 1}

    total_pct = sum(percentage for _, _, percentage in rows)
    assert round(total_pct) == 100


def test_date_trend_excludes_events_older_than_7_days(db_conn):
    cur = db_conn.cursor()
    cur.execute("TRUNCATE events")
    now = datetime.now()
    old = now - timedelta(days=10)
    _insert(cur, [
        ("page_view", "U1", now),
        ("page_view", "U1", now),
        ("page_view", "U1", old),  # 7일 밖 → 집계 제외
    ])

    cur.execute(QUERIES["date_trend_7days"])
    rows = cur.fetchall()  # (date, count)

    assert sum(count for _, count in rows) == 2


def test_save_events_round_trip():
    """save_events가 타입 전용 필드까지 실제로 저장하는지 확인."""
    marker = "rt-roundtrip-session"
    event = {
        "event_type": "purchase",
        "user_id": "U-RT",
        "session_id": marker,
        "lecture_id": "LEC-001",
        "page_url": None,
        "amount": 50000.0,
        "error_code": None,
        "created_at": datetime.now(),
    }

    save_events([event])

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT event_type, lecture_id, amount, error_code "
            "FROM events WHERE session_id = %s",
            (marker,),
        )
        row = cur.fetchone()

        assert row is not None
        assert row[0] == "purchase"
        assert row[1] == "LEC-001"
        assert float(row[2]) == 50000.0
        assert row[3] is None
    finally:
        cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE session_id = %s", (marker,))
        conn.commit()
        conn.close()
