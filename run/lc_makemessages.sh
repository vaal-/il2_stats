#!/bin/bash

cd ../src

../.venv/bin/python manage.py makemessages -a

read -p "Press any key to continue... "

