from app.visits import CACHE_KEY, CACHE_TTL_SECONDS


def test_first_request_uses_database(visits_env):
    client, cache = visits_env

    response = client.get("/visits")

    assert response.status_code == 200
    body = response.get_json()
    assert body["source"] == "db"
    assert body["count"] == 1
    assert 0 < cache.ttl(CACHE_KEY) <= CACHE_TTL_SECONDS


def test_second_request_uses_cache(visits_env):
    client, _ = visits_env
    # Тест сам прогревает кэш и не полагается на другие тесты
    client.get("/visits")

    response = client.get("/visits")

    assert response.get_json() == {"count": 1, "source": "cache"}


def test_counter_grows_after_cache_expiry(visits_env):
    client, cache = visits_env
    client.get("/visits")
    cache.delete(CACHE_KEY)  # имитируем истечение TTL

    response = client.get("/visits")

    body = response.get_json()
    assert body["source"] == "db"
    assert body["count"] == 2
