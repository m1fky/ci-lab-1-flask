import os
import random

from flask import Flask, jsonify, request

from app.metrics import HTTP_REQUESTS_TOTAL, metrics_response
from app.visits import create_visits_blueprint

# Доля ответов 500 в «сломанной» версии (CHAOS_MODE=true)
CHAOS_ERROR_RATE = 0.3


def create_app(db_conn=None, redis_url=None):
    app = Flask(__name__)

    @app.after_request
    def record_metrics(response):
        # запросы самого Prometheus к /metrics в статистику не входят
        if request.path != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(status_code=str(response.status_code)).inc()
        return response

    @app.route("/metrics")
    def metrics():
        return metrics_response()

    @app.route("/health")
    def health():
        """Health-check; при CHAOS_MODE=true часть ответов намеренно 500."""
        if os.environ.get("CHAOS_MODE") == "true" and random.random() < CHAOS_ERROR_RATE:
            return jsonify(status="error"), 500
        return jsonify(status="ok"), 200

    # /visits подключается, только если переданы зависимости: БД и Redis
    if db_conn is not None and redis_url:
        app.register_blueprint(create_visits_blueprint(db_conn, redis_url))

    return app
