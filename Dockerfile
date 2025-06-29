ARG PYTHON_VERSION=3.13.0
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --locked


COPY . .

CMD uv run bot.py
