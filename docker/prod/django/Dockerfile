FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple \
    PIP_TRUSTED_HOST=mirror-pypi.runflare.com

WORKDIR /app

RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --home-dir /app --shell /usr/sbin/nologin django

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
    && pip install --no-cache-dir gunicorn uvicorn psycopg2-binary redis

COPY ./arkkala /app/
COPY ./docker/scripts/wait_for_deps.py /wait_for_deps.py
COPY ./docker/scripts/entrypoint.sh /entrypoint.sh
COPY ./docker/scripts/healthcheck.py /healthcheck.py

RUN sed -i 's/\r$//g' /entrypoint.sh /wait_for_deps.py /healthcheck.py \
    && mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R django:appgroup /app /wait_for_deps.py /entrypoint.sh /healthcheck.py \
    && chmod +x /entrypoint.sh /healthcheck.py

USER django

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python /healthcheck.py

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "arkkala.asgi:application"]