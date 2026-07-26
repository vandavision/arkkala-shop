#!/usr/bin/env python
import os
import socket
import sys
import time

MAX_RETRIES: int = int(os.environ.get("WAIT_FOR_DEPS_MAX_RETRIES", "60"))
RETRY_INTERVAL: float = float(os.environ.get("WAIT_FOR_DEPS_INTERVAL", "2"))

def wait_for_tcp(host: str, port: int, name: str) -> None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with socket.create_connection((host, port), timeout=3):
                return
        except OSError:
            time.sleep(RETRY_INTERVAL)
    sys.exit(1)

def wait_for_postgres() -> None:
    host: str = os.environ.get("POSTGRES_HOST", "postgres")
    port: int = int(os.environ.get("POSTGRES_PORT", "5432"))
    wait_for_tcp(host, port, "PostgreSQL")

def wait_for_redis() -> None:
    broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    try:
        without_scheme: str = broker_url.split("://", 1)[1]
        hostport: str = without_scheme.split("@")[-1].split("/")[0]
        host, port = hostport.split(":")
        wait_for_tcp(host, int(port), "Redis")
    except (IndexError, ValueError):
        pass

if __name__ == "__main__":
    wait_for_postgres()
    wait_for_redis()