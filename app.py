import logging

import matplotlib
import matplotlib.pyplot as plt
import streamlit as st

matplotlib.use("Agg")

from db import get_connection, setup_database  # noqa: E402
from event_generator import generate_events, save_events  # noqa: E402

logging.basicConfig(level=logging.INFO)


def _fetch(conn, query: str) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def _chart_counts(conn) -> plt.Figure:
    rows = _fetch(conn, """
        SELECT event_type, COUNT(*) AS cnt
        FROM events GROUP BY event_type ORDER BY cnt DESC
    """)
    fig, ax = plt.subplots()
    ax.bar([r[0] for r in rows], [r[1] for r in rows])
    ax.set_title("Event Type Counts")
    ax.set_xlabel("Event Type")
    ax.set_ylabel("Count")
    return fig


def _chart_ratio(conn) -> plt.Figure:
    rows = _fetch(conn, """
        SELECT event_type, COUNT(*) AS cnt
        FROM events GROUP BY event_type ORDER BY cnt DESC
    """)
    fig, ax = plt.subplots()
    ax.pie([r[1] for r in rows], labels=[r[0] for r in rows], autopct="%1.1f%%")
    ax.set_title("Event Type Distribution")
    return fig


def _chart_trend(conn) -> plt.Figure:
    rows = _fetch(conn, """
        SELECT DATE(created_at) AS date, COUNT(*) AS cnt
        FROM events
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(created_at) ORDER BY date
    """)
    fig, ax = plt.subplots()
    ax.plot([str(r[0]) for r in rows], [r[1] for r in rows], marker="o")
    ax.set_title("Daily Event Trend (Last 7 Days)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45)
    return fig


def _chart_top10(conn) -> plt.Figure:
    rows = _fetch(conn, """
        SELECT user_id, COUNT(*) AS cnt
        FROM events GROUP BY user_id ORDER BY cnt DESC LIMIT 10
    """)
    users = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    fig, ax = plt.subplots()
    ax.barh(users[::-1], counts[::-1])
    ax.set_title("Top 10 Users by Activity")
    ax.set_xlabel("Event Count")
    return fig


st.set_page_config(page_title="LiveClass Event Pipeline", layout="wide")
st.title("LiveClass Event Pipeline")

st.sidebar.header("이벤트 설정")

count = st.sidebar.number_input(
    "생성할 이벤트 수", min_value=100, max_value=10000, value=1000, step=100
)

st.sidebar.subheader("이벤트 타입 가중치")
w_page_view = st.sidebar.slider("page_view", 0, 100, 50)
w_lecture_play = st.sidebar.slider("lecture_play", 0, 100, 30)
w_purchase = st.sidebar.slider("purchase", 0, 100, 15)
w_error = st.sidebar.slider("error", 0, 100, 5)

total = w_page_view + w_lecture_play + w_purchase + w_error
if total == 0:
    st.sidebar.error("가중치 합계가 0입니다.")
else:
    st.sidebar.caption(f"합계: {total}")

if st.sidebar.button("이벤트 생성 및 시각화", disabled=(total == 0)):
    with st.spinner("DB 초기화 중..."):
        setup_database()

    weights = [w_page_view, w_lecture_play, w_purchase, w_error]

    with st.spinner(f"{count}개 이벤트 생성 중..."):
        events = generate_events(count=int(count), weights=weights)
        save_events(events)

    st.success(f"{count}개 이벤트 저장 완료")

    conn = get_connection()
    try:
        col1, col2 = st.columns(2)
        with col1:
            fig = _chart_counts(conn)
            st.pyplot(fig)
            plt.close(fig)
        with col2:
            fig = _chart_ratio(conn)
            st.pyplot(fig)
            plt.close(fig)

        fig = _chart_trend(conn)
        st.pyplot(fig)
        plt.close(fig)

        fig = _chart_top10(conn)
        st.pyplot(fig)
        plt.close(fig)
    finally:
        conn.close()
