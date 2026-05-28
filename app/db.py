import psycopg2
from psycopg2 import pool

db_pool = None

def init_pool(db_config, max_retries=10, delay=2):
    global db_pool
    for attempt in range(max_retries):
        try:
            db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)
            return 
        except Exception as e:
            if attempt == max_retries - 1:
                raise


def get_db():
    return db_pool.getconn()

def release_db(conn):
    db_pool.putconn(conn)