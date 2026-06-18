from unittest.mock import patch

import pytest

from event_generator import (
    ERROR_CODES,
    LECTURE_IDS,
    PAGE_URLS,
    USER_IDS,
    generate_events,
    save_events,
)


def test_generate_events_returns_requested_count():
    assert len(generate_events(100)) == 100


def test_generate_events_default_count():
    assert len(generate_events()) == 1000


def test_event_has_required_fields():
    required = {
        "event_type", "user_id", "session_id",
        "lecture_id", "page_url", "amount", "error_code", "created_at",
    }
    for event in generate_events(10):
        assert set(event.keys()) == required


def test_user_id_is_valid():
    for event in generate_events(50):
        assert event["user_id"] in USER_IDS


@pytest.mark.parametrize("event_type", ["page_view", "lecture_play", "purchase", "error"])
def test_event_type_fields(event_type):
    with patch("event_generator.random.choices", return_value=[event_type]):
        event = generate_events(1)[0]

    assert event["event_type"] == event_type

    if event_type == "page_view":
        assert event["page_url"] in PAGE_URLS
        assert event["lecture_id"] is None
        assert event["amount"] is None
        assert event["error_code"] is None
    elif event_type == "lecture_play":
        assert event["lecture_id"] in LECTURE_IDS
        assert event["page_url"] is None
        assert event["amount"] is None
        assert event["error_code"] is None
    elif event_type == "purchase":
        assert event["lecture_id"] in LECTURE_IDS
        assert 10000 <= event["amount"] <= 99000
        assert event["page_url"] is None
        assert event["error_code"] is None
    elif event_type == "error":
        assert event["error_code"] in ERROR_CODES
        assert event["lecture_id"] is None
        assert event["amount"] is None
        assert event["page_url"] is None


def test_save_events_calls_executemany():
    events = generate_events(5)

    with patch("event_generator.get_connection") as mock_get_conn:
        mock_conn = mock_get_conn.return_value
        mock_cur = mock_conn.cursor.return_value.__enter__.return_value

        save_events(events)

        mock_cur.executemany.assert_called_once()
        _, rows = mock_cur.executemany.call_args[0]
        assert len(rows) == 5
