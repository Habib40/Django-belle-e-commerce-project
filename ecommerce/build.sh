#!/usr/bin/env/bash
#error exit
set -o errexit


pip install requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate