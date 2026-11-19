#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

COMPOSE_FILE="production.yml"
ENV_FILE=".env.prod"
BACKUP_DIR="docker/prod/postgres/backups"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="arkkala_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T postgres \
    sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
    | gzip > "${BACKUP_DIR}/${FILENAME}"

find "${BACKUP_DIR}" -name "arkkala_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete