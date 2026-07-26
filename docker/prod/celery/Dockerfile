# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY arkkala/requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=arkkala.settings.prod

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system celery \
    && useradd --system --gid celery --home-dir /app --shell /usr/sbin/nologin celery

COPY --from=builder /app/wheels /wheels
COPY arkkala/requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY ./arkkala /app
COPY ./docker/scripts/wait_for_deps.py /wait_for_deps.py
COPY ./docker/prod/celery/start_worker /start_worker
COPY ./docker/prod/celery/start_beat /start_beat

RUN sed -i 's/\r$//g' /start_worker /start_beat \
    && chmod +x /start_worker /start_beat \
    && mkdir -p /app/celerybeat \
    && chown -R celery:celery /app /start_worker /start_beat /wait_for_deps.py

USER celery