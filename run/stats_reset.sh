#!/bin/bash

cd ../src

read -p "Press any key to continue... "

../.venv/bin/python manage.py stats_reset

read -p "Press any key to continue... "

