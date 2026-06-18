CREATE TABLE IF NOT EXISTS events (
    id          SERIAL          PRIMARY KEY,
    event_type  VARCHAR(50)     NOT NULL,
    user_id     VARCHAR(50)     NOT NULL,
    session_id  VARCHAR(50)     NOT NULL,
    lecture_id  VARCHAR(50),
    page_url    TEXT,
    amount      NUMERIC(10, 2),
    error_code  VARCHAR(50),
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);
