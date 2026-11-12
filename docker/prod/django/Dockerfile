FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple \
    PIP_TRUSTED_HOST=mirror-pypi.runflare.com

WORKDIR /app

RUN groupadd -r django && useradd -r -g django django

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./arkkala/requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn uvicorn psycopg2-binary redis

COPY ./arkkala /app/
COPY ./docker/scripts/wait_for_deps.py /wait_for_deps.py
COPY ./docker/scripts/entrypoint.sh /entrypoint.sh

RUN chown -R django:django /app /wait_for_deps.py /entrypoint.sh \
    && chmod +x /entrypoint.sh

USER django

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/healthz/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "arkkala.asgi:application"]