"""Счётчик посещений: запись в PostgreSQL и кэширование результата в Redis."""
import redis as redis_lib
from flask import Blueprint, jsonify

CACHE_KEY = "visits_count"
CACHE_TTL_SECONDS = 10

# Минимальная миграция (DDL) для таблицы visits
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
)
"""


def init_schema(db_conn):
    """Создаёт таблицу visits, если её ещё нет."""
    with db_conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
    db_conn.commit()


def create_visits_blueprint(db_conn, redis_url):
    bp = Blueprint("visits", __name__)
    cache = redis_lib.from_url(redis_url)

    @bp.route("/visits")
    def visits():
        cached = cache.get(CACHE_KEY)
        if cached:
            return jsonify(count=int(cached), source="cache")

        with db_conn.cursor() as cur:
            cur.execute("INSERT INTO visits (created_at) VALUES (NOW()) RETURNING id")
            new_id = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM visits")
            count = cur.fetchone()[0]
        db_conn.commit()

        cache.set(CACHE_KEY, count, ex=CACHE_TTL_SECONDS)
        return jsonify(count=count, source="db", lastId=new_id)

    return bp
