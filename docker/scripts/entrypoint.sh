#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

python /wait_for_deps.py
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

exec "$@"