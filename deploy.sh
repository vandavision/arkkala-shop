#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

COMPOSE_FILE="production.yml"
ENV_FILE=".env.prod"
COMPOSE_CMD="docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE}"
HEALTH_TIMEOUT=90
HEALTH_INTERVAL=3

if [[ ! -f "${COMPOSE_FILE}" ]]; then
    echo "Error: ${COMPOSE_FILE} not found."
    exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Error: ${ENV_FILE} not found."
    exit 1
fi

if [[ ! -f "./frontend/dist/index.html" ]]; then
    echo "Error: ./frontend/dist/index.html not found. Run ./build-front.sh first."
    exit 1
fi

PREVIOUS_IMAGE_ID=$(${COMPOSE_CMD} images -q django 2>/dev/null || true)

git fetch --quiet
git pull --quiet

GIT_SHA=$(git rev-parse --short HEAD)
export IMAGE_TAG="${GIT_SHA}"

${COMPOSE_CMD} build --pull django celery_worker celery_beat nginx prerender
${COMPOSE_CMD} up -d --remove-orphans

elapsed=0
status="starting"

while [[ "${elapsed}" -lt "${HEALTH_TIMEOUT}" ]]; do
    status=$(docker inspect --format='{{.State.Health.Status}}' arkkala_prod_django 2>/dev/null || echo "unknown")

    if [[ "${status}" == "healthy" || "${status}" == "unhealthy" ]]; then
        break
    fi

    sleep "${HEALTH_INTERVAL}"
    elapsed=$((elapsed + HEALTH_INTERVAL))
done

if [[ "${status}" != "healthy" ]]; then
    echo "Django healthcheck failed (status: ${status}). Rolling back..."
    ${COMPOSE_CMD} logs --tail=50 django

    if [[ -n "${PREVIOUS_IMAGE_ID}" ]]; then
        docker tag "${PREVIOUS_IMAGE_ID}" "arkkala-django:${IMAGE_TAG}" || true
        IMAGE_TAG=$(docker inspect --format='{{index .RepoTags 0}}' "${PREVIOUS_IMAGE_ID}" 2>/dev/null | cut -d: -f2 || echo "latest")
        export IMAGE_TAG
        ${COMPOSE_CMD} up -d django celery_worker celery_beat
    fi

    exit 1
fi

docker image prune -f --filter "until=24h" > /dev/null
${COMPOSE_CMD} ps