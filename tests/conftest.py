import pytest
from dotenv import load_dotenv
from db import get_connection, setup_database

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def init_database():
    setup_database()


@pytest.fixture
def db_conn():
    conn = get_connection()
    yield conn
    conn.rollback()
    conn.close()
