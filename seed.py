import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

load_dotenv()


def get_db_config():
    return {
        "dbname": os.getenv("DB_NAME", "farm_db"), 
        "user": os.getenv("DB_USER", "user"), 
        "password": os.getenv("DB_PASSWORD", "password"), 
        "host": os.getenv("DB_HOST", "db"),
        "port": int(os.getenv("DB_PORT", 5432)),
    }

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS farm_stats (
    id SERIAL PRIMARY KEY,
    farm VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    abort INTEGER NOT NULL,
    bulls_from_cows INTEGER NOT NULL,
    bulls_from_heifers INTEGER NOT NULL,
    conception_cows INTEGER NOT NULL,
    conception_heifers INTEGER NOT NULL,
    cows_from_cows INTEGER NOT NULL,
    cows_from_heifers INTEGER NOT NULL,
    dead_bulls INTEGER NOT NULL,
    dead_heifers INTEGER NOT NULL,
    preg_rate_cows REAL NOT NULL,
    preg_rate_heifers REAL NOT NULL,
    reproduction_cows INTEGER NOT NULL,
    reproduction_heifers INTEGER NOT NULL
);
"""

INSERT_SQL = """
INSERT INTO farm_stats (
    farm, date, abort, bulls_from_cows, bulls_from_heifers,
    conception_cows, conception_heifers, cows_from_cows, cows_from_heifers,
    dead_bulls, dead_heifers, preg_rate_cows, preg_rate_heifers,
    reproduction_cows, reproduction_heifers
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


def seed_database():
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()

    cur.execute(CREATE_TABLE_SQL)
    conn.commit()

    date_str = "Mon, 23 Mar 2026 00:00:00 GMT"
    date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").date()

    test_data = ("Ферма 1", date_obj, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0, 0)

    cur.execute(INSERT_SQL, test_data)
    conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed_database()
