FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-docker.txt .
RUN python -m pip install --no-cache-dir -r requirements-docker.txt \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/output \
    && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5011

CMD ["gunicorn", "--bind", "0.0.0.0:5011", "--workers", "1", "--timeout", "300", "webapp:app"]
