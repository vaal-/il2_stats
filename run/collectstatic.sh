#!/bin/bash

cd ../src

../.venv/bin/python manage.py collectstatic --noinput

read -p "Press any key to continue... "

