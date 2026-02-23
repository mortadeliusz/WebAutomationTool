"""
Database connection management
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import settings

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(settings.db_connection_string, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_db_cursor(conn):
    return conn.cursor()
