ARG PYTHON_VERSION=3.13.0
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir uv

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --system -r requirements.txt

COPY . .

CMD uv run --no-project bot.py
