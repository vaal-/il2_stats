#!/bin/bash

cd ../
.venv/bin/pip install -U -r requirements.txt

read -p "Press any key to continue... "

cd src

../.venv/bin/python manage.py collectstatic --noinput

read -p "Press any key to continue... "

../.venv/bin/python manage.py migrate --noinput

read -p "Press any key to continue... "

../.venv/bin/python manage.py import_csv_data

read -p "Press any key to continue... "

../.venv/bin/python manage.py clearsessions

read -p "Press any key to continue... "
