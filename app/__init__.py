from flask import Flask, jsonify

from app.visits import create_visits_blueprint


def create_app(db_conn=None, redis_url=None):
    app = Flask(__name__)

    @app.route("/health")
    def health():
        """Health-check endpoint для проверки контейнера."""
        return jsonify(status="ok"), 200

    # /visits подключается, только если переданы зависимости: БД и Redis
    if db_conn is not None and redis_url:
        app.register_blueprint(create_visits_blueprint(db_conn, redis_url))

    return app
