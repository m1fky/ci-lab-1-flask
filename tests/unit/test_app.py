from app import create_app


def test_health_returns_200():
    client = create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_visits_not_registered_without_dependencies():
    client = create_app().test_client()

    assert client.get("/visits").status_code == 404


def test_visits_registered_with_dependencies():
    # redis.from_url не подключается к серверу до первой команды,
    # а соединение с БД при регистрации маршрута не используется
    app = create_app(db_conn=object(), redis_url="redis://localhost:6379/0")

    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/visits" in rules
