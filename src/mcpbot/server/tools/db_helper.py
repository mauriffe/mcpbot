"""Secure PostgreSQL connection (read-only by default)."""

import psycopg2
import re
from typing import List, Dict
from contextlib import contextmanager
from dotenv import load_dotenv
import os
import logging

load_dotenv()
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

# Regex to block dangerous queries
FORBIDDEN = re.compile(r"^\s*(ALTER|CREATE|DELETE|DROP|INSERT|UPDATE|TRUNCATE|GRANT|REVOKE)\b", re.I)

logger = logging.getLogger(__name__)  # Module-level logger

@contextmanager
def get_conn(dbname: str = POSTGRES_DB, *, read_only: bool = True):
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=dbname,
        options="-c search_path=public",
    )
    try:
        if read_only:
            conn.set_session(readonly=True, autocommit=True)
        yield conn
    finally:
        conn.close()

async def execute_safe_query(database: str, query: str, max_rows: int = 100) -> List[Dict]:
    """Executes a SQL query safely."""
    if FORBIDDEN.match(query):
        raise ValueError(" Potentially destructive query blocked.")

    try:
        with get_conn(database) as conn, conn.cursor() as cur:
            cur.execute(query)
            if not cur.description:
                return []

            cols = [d[0] for d in cur.description]
            results = [dict(zip(cols, row)) for row in cur.fetchmany(max_rows)]
            logging.info(f"Query executed successfully: {len(results)} rows returned")
            return results
    except Exception as e:
        logging.error(f"SQL error: {e}")
        raise