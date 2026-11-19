FROM docker.arvancloud.ir/python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple \
    PIP_TRUSTED_HOST=mirror-pypi.runflare.com

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY arkkala/requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM docker.arvancloud.ir/python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=arkkala.settings.prod \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple \
    PIP_TRUSTED_HOST=mirror-pypi.runflare.com

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --home-dir /app --shell /usr/sbin/nologin celery

COPY --from=builder /app/wheels /wheels
COPY arkkala/requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY ./arkkala /app
COPY ./docker/scripts/wait_for_deps.py /wait_for_deps.py
COPY ./docker/prod/celery/start_worker /start_worker
COPY ./docker/prod/celery/start_beat /start_beat

RUN sed -i 's/\r$//g' /start_worker /start_beat /wait_for_deps.py \
    && chmod +x /start_worker /start_beat \
    && mkdir -p /app/celerybeat /app/mediafiles \
    && chown -R celery:appgroup /app /start_worker /start_beat /wait_for_deps.py

USER celery

CMD ["/start_worker"]