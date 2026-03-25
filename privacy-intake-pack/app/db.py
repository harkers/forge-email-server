import os
from contextlib import contextmanager
from psycopg import connect
from psycopg.rows import dict_row

DATABASE_URL = os.environ["DATABASE_URL"]

@contextmanager
def get_db():
    conn = connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()
