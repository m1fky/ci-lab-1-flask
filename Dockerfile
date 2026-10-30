# ---------- Стадия 1: build (полный образ Python) ----------
FROM python:3.12 AS build
WORKDIR /app

# Сначала только файл production-зависимостей и их установка.
# Пока requirements-prod.txt не меняется, этот слой берётся из кэша.
COPY requirements-prod.txt .
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir -r requirements-prod.txt

# Затем исходный код: его изменение пересобирает только слои ниже.
COPY app/ ./app/
RUN /opt/venv/bin/python -m compileall -q app

# ---------- Стадия 2: runtime (компактный образ) ----------
FROM python:3.12-slim AS runtime
LABEL org.opencontainers.image.source="https://github.com/m1fky/ci-lab-1-flask"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

# Из стадии build берём только готовое окружение и код приложения
COPY --from=build /opt/venv /opt/venv
COPY --from=build /app/app ./app

USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
