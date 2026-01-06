FROM python:3.12-slim@sha256:afeaa0e6e5ea3cbb757a6545521c6797e6a45d7bc55ea4ebfecb1a1c8aac3efc

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY *.py *.json *.sh defaults.env ./

RUN useradd --create-home --shell /sbin/nologin appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
