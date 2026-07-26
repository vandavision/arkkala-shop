#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

COMPOSE_FILE="production.yml"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="arkkala_${TIMESTAMP}.sql.gz"

docker compose -f "${COMPOSE_FILE}" exec -T postgres \
    sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
    | gzip > "docker/prod/postgres/backups/${FILENAME}"

find docker/prod/postgres/backups -name "arkkala_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete