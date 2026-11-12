FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple \
    PIP_TRUSTED_HOST=mirror-pypi.runflare.com

WORKDIR /app

COPY arkkala/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./arkkala /app

COPY docker/dev/celery/start_worker /start_worker
RUN sed -i 's/\r$//g' /start_worker && chmod +x /start_worker

COPY docker/dev/celery/start_beat /start_beat
RUN sed -i 's/\r$//g' /start_beat && chmod +x /start_beat