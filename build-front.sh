#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${PROJECT_DIR}/frontend"

if [[ ! -f "${FRONTEND_DIR}/.env.production" ]]; then
    echo "Error: frontend/.env.production not found."
    exit 1
fi

cd "${FRONTEND_DIR}"

echo "[1/4] Installing frontend dependencies..."
npm ci --registry=https://registry.npmmirror.com

echo "[2/4] Building production bundle..."
rm -rf dist_tmp
npx vite build --outDir dist_tmp

echo "[3/4] Syncing into ./frontend/dist without breaking Docker mount inode..."
mkdir -p dist
if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete dist_tmp/ dist/
else
    find dist -mindepth 1 -delete
    cp -a dist_tmp/. dist/
fi
rm -rf dist_tmp

echo "[4/4] Setting read permissions for Nginx..."
chmod -R a+rX dist

echo "Frontend build completed and live."