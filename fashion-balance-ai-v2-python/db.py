"""MySQL access. Each request uses its own connection; SQL values are bound parameters."""
import os
from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor


@contextmanager
def transaction():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'), port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'), password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'fashion_balance'), charset='utf8mb4',
        cursorclass=DictCursor, connect_timeout=5, read_timeout=15, write_timeout=15,
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def query(sql, values=(), connection=None):
    """Return dict rows for SELECT; id/affected counts for writes."""
    if connection is None:
        with transaction() as conn:
            return query(sql, values, conn)
    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        if cursor.description:
            return list(cursor.fetchall())
        return {'insert_id': cursor.lastrowid, 'affected': cursor.rowcount}
