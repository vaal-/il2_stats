#!/bin/bash

pip install -U virtualenv

cd ../
virtualenv .venv

.venv/bin/pip install -U wheel pip

.venv/bin/pip install -U -r requirements.txt

read -p "Press any key to continue... "

cd src

../.venv/bin/python manage.py collectstatic --noinput

read -p "Press any key to continue... "

../.venv/bin/python manage.py migrate --noinput

read -p "Press any key to continue... "

../.venv/bin/python manage.py import_csv_data

read -p "Press any key to continue... "

../.venv/bin/python manage.py createsuperuser

read -p "Press any key to continue... "
