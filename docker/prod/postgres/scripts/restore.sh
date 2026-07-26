#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

COMPOSE_FILE="production.yml"
DUMP_FILE="${1:?Usage: $0 <path-to-dump.sql.gz>}"

if [[ ! -f "${DUMP_FILE}" ]]; then
    exit 1
fi

read -r -p "This will DROP and recreate the production database. Type 'yes' to continue: " CONFIRM
if [[ "${CONFIRM}" != "yes" ]]; then
    exit 1
fi

docker compose -f "${COMPOSE_FILE}" stop django celery_worker celery_beat

gunzip -c "${DUMP_FILE}" | docker compose -f "${COMPOSE_FILE}" exec -T postgres \
    sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'

docker compose -f "${COMPOSE_FILE}" up -d django celery_worker celery_beat