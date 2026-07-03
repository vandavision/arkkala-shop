FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY arkkala/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./arkkala /app

COPY docker/prod/celery/start_worker /start_worker
RUN sed -i 's/\r$//g' /start_worker
RUN chmod +x /start_worker

COPY docker/prod/celery/start_beat /start_beat
RUN sed -i 's/\r$//g' /start_beat
RUN chmod +x /start_beat