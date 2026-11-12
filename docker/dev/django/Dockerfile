FROM docker.arvancloud.ir/python:3.12-slim

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
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

COPY arkkala/requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install django-debug-toolbar ipython watchfiles

COPY ./docker/scripts/wait_for_deps.py /wait_for_deps.py

COPY ./arkkala /app