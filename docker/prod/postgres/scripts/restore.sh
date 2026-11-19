#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

COMPOSE_FILE="production.yml"
ENV_FILE=".env.prod"
DUMP_FILE="${1:?Usage: $0 <path-to-dump.sql.gz>}"

if [[ ! -f "${DUMP_FILE}" ]]; then
    echo "Dump file not found: ${DUMP_FILE}"
    exit 1
fi

read -r -p "This will overwrite the production database. Type 'yes' to continue: " CONFIRM
if [[ "${CONFIRM}" != "yes" ]]; then
    exit 1
fi

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" stop django celery_worker celery_beat

gunzip -c "${DUMP_FILE}" | docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T postgres \
    sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d django celery_worker celery_beat