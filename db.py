import logging
import os

import psycopg2

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def setup_database():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_path) as schema_file:
        schema_sql = schema_file.read()

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
        logger.info("events 테이블 준비 완료")
    finally:
        conn.close()
