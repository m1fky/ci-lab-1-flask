import psycopg2
import pytest
import redis as redis_lib
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from app import create_app
from app.visits import init_schema


@pytest.fixture()
def visits_env():
    """Свежие PostgreSQL и Redis для каждого теста.

    Без scope фикстура выполняется заново для каждого теста, поэтому тесты не
    зависят друг от друга и могут идти параллельно. Порты выдаёт Testcontainers,
    фиксированных портов нет. Контейнеры удаляются при выходе из with,
    в том числе если тест упал.
    """
    with PostgresContainer("postgres:16", driver=None) as pg, RedisContainer("redis:7") as rc:
        conn = psycopg2.connect(pg.get_connection_url())
        init_schema(conn)
        redis_url = f"redis://{rc.get_container_host_ip()}:{rc.get_exposed_port(6379)}/0"
        app = create_app(db_conn=conn, redis_url=redis_url)
        cache = redis_lib.from_url(redis_url)
        try:
            yield app.test_client(), cache
        finally:
            cache.close()
            conn.close()
