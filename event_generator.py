import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import TypedDict

from db import get_connection

logger = logging.getLogger(__name__)


class Event(TypedDict):
    event_type: str
    user_id: str
    session_id: str
    lecture_id: str | None
    page_url: str | None
    amount: float | None
    error_code: str | None
    created_at: datetime


USER_IDS = [f"USER-{i:03d}" for i in range(1, 51)]
LECTURE_IDS = [f"LEC-{i:03d}" for i in range(1, 11)]

PAGE_URLS = [
    "/courses/python-basics",
    "/courses/data-engineering",
    "/courses/sql-fundamentals",
    "/courses/docker-intro",
    "/courses/aws-basics",
]

ERROR_CODES = ["ERR_404", "ERR_500", "ERR_TIMEOUT", "ERR_AUTH"]


def _random_timestamp() -> datetime:
    return datetime.now() - timedelta(
        days=random.randint(0, 6),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


DEFAULT_WEIGHTS = [50, 30, 15, 5]


def _build_event(
    user_id: str,
    session_id: str,
    weights: list[int] | None = None,
) -> Event:
    event_type = random.choices(
        ["page_view", "lecture_play", "purchase", "error"],
        weights=weights or DEFAULT_WEIGHTS,
    )[0]

    event = {
        "event_type": event_type,
        "user_id": user_id,
        "session_id": session_id,
        "lecture_id": None,
        "page_url": None,
        "amount": None,
        "error_code": None,
        "created_at": _random_timestamp(),
    }

    if event_type == "page_view":
        event["page_url"] = random.choice(PAGE_URLS)
    elif event_type == "lecture_play":
        event["lecture_id"] = random.choice(LECTURE_IDS)
    elif event_type == "purchase":
        event["lecture_id"] = random.choice(LECTURE_IDS)
        event["amount"] = round(random.uniform(10000, 99000), 2)
    elif event_type == "error":
        event["error_code"] = random.choice(ERROR_CODES)

    return event


def generate_events(
    count: int = 1000,
    weights: list[int] | None = None,
) -> list[Event]:
    session_ids = [str(uuid.uuid4())[:8] for _ in range(200)]

    return [
        _build_event(
            user_id=random.choice(USER_IDS),
            session_id=random.choice(session_ids),
            weights=weights,
        )
        for _ in range(count)
    ]


def save_events(events: list[Event]) -> None:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO events
                        (event_type, user_id, session_id, lecture_id,
                         page_url, amount, error_code, created_at)
                    VALUES
                        (%(event_type)s, %(user_id)s, %(session_id)s, %(lecture_id)s,
                         %(page_url)s, %(amount)s, %(error_code)s, %(created_at)s)
                    """,
                    events,
                )
        logger.info("%d개 이벤트 저장 완료", len(events))
    finally:
        conn.close()


def run(count: int = 1000, weights: list[int] | None = None) -> None:
    events = generate_events(count, weights=weights)
    save_events(events)
