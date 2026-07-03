FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY arkkala/requirements.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

COPY ./arkkala /app

RUN mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R www-data:www-data /app