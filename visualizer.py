import logging
import os

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

from db import get_connection  # noqa: E402
from queries import QUERIES  # noqa: E402

logger = logging.getLogger(__name__)

CHARTS_DIR = os.path.join(os.path.dirname(__file__), "charts")


def _fetch(conn, query: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def _save(fig: plt.Figure, filename: str) -> None:
    os.makedirs(CHARTS_DIR, exist_ok=True)
    fig.savefig(os.path.join(CHARTS_DIR, filename), bbox_inches="tight")
    plt.close(fig)
    logger.info("%s saved", filename)


def chart_event_type_counts(conn) -> None:
    rows = _fetch(conn, QUERIES["event_type_counts"])

    types = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots()
    ax.bar(types, counts)
    ax.set_title("Event Type Counts")
    ax.set_xlabel("Event Type")
    ax.set_ylabel("Count")

    _save(fig, "event_type_counts.png")


def chart_date_trend(conn) -> None:
    rows = _fetch(conn, QUERIES["date_trend_7days"])

    dates = [str(r[0]) for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots()
    ax.plot(dates, counts, marker="o")
    ax.set_title("Daily Event Trend (Last 7 Days)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45)

    _save(fig, "date_trend.png")


def chart_top10_users(conn) -> None:
    rows = _fetch(conn, QUERIES["top10_users_by_activity"])

    users = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots()
    ax.barh(users[::-1], counts[::-1])
    ax.set_title("Top 10 Users by Activity")
    ax.set_xlabel("Event Count")

    _save(fig, "top10_users.png")


def chart_event_type_ratio(conn) -> None:
    # event_type_ratio: (event_type, count, percentage) — 파이 차트는 count로 비율 표현
    rows = _fetch(conn, QUERIES["event_type_ratio"])

    types = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots()
    ax.pie(counts, labels=types, autopct="%1.1f%%")
    ax.set_title("Event Type Distribution")

    _save(fig, "event_type_ratio.png")


def run() -> None:
    conn = get_connection()
    try:
        chart_event_type_counts(conn)
        chart_date_trend(conn)
        chart_top10_users(conn)
        chart_event_type_ratio(conn)
        logger.info("all charts saved to %s", CHARTS_DIR)
    finally:
        conn.close()
