"""Метрики Prometheus: счётчик HTTP-запросов по коду ответа."""
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

# Счётчик создаётся один раз на уровне модуля: повторный вызов create_app()
# (например, в тестах) не пытается зарегистрировать его заново.
# Имя и метка совпадают с запросом PromQL в k8s/analysistemplate.yaml.
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total HTTP requests", ["status_code"]
)


def metrics_response():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
