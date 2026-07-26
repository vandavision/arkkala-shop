#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

COMPOSE_FILE="production.yml"
HEALTH_TIMEOUT=90
HEALTH_INTERVAL=3

if [[ ! -f "${COMPOSE_FILE}" ]]; then
    exit 1
fi

if [[ ! -f ".env.prod" ]]; then
    exit 1
fi

PREVIOUS_IMAGE_ID=$(docker compose -f "${COMPOSE_FILE}" images -q django 2>/dev/null || true)

git fetch --quiet
git pull --quiet

GIT_SHA=$(git rev-parse --short HEAD)
export IMAGE_TAG="${GIT_SHA}"

docker compose -f "${COMPOSE_FILE}" build --pull django celery_worker celery_beat nginx

docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

elapsed=0
status="starting"

while [[ "${elapsed}" -lt "${HEALTH_TIMEOUT}" ]]; do
    status=$(docker inspect --format='{{.State.Health.Status}}' arkkala_prod_django 2>/dev/null || echo "unknown")

    if [[ "${status}" == "healthy" ]]; then
        break
    fi

    if [[ "${status}" == "unhealthy" ]]; then
        break
    fi

    sleep "${HEALTH_INTERVAL}"
    elapsed=$((elapsed + HEALTH_INTERVAL))
done

if [[ "${status}" != "healthy" ]]; then
    docker compose -f "${COMPOSE_FILE}" logs --tail=50 django

    if [[ -n "${PREVIOUS_IMAGE_ID}" ]]; then
        docker tag "${PREVIOUS_IMAGE_ID}" "arkkala-django:${IMAGE_TAG}" || true
        IMAGE_TAG=$(docker inspect --format='{{index .RepoTags 0}}' "${PREVIOUS_IMAGE_ID}" 2>/dev/null | cut -d: -f2 || echo "latest")
        export IMAGE_TAG
        docker compose -f "${COMPOSE_FILE}" up -d django celery_worker celery_beat
    fi

    exit 1
fi

docker image prune -f --filter "until=24h" > /dev/null
docker compose -f "${COMPOSE_FILE}" ps