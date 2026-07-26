# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
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