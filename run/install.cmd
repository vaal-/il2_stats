cd ../
python -m venv --clear .venv
".venv/Scripts/easy_install.exe" -q -U pip==20.3.4
".venv/Scripts/python.exe" -m pip install --quiet -r requirements.txt
pause
cd src
"../.venv/Scripts/python.exe" manage.py collectstatic --noinput --verbosity 0
pause
"../.venv/Scripts/python.exe" manage.py migrate --noinput --verbosity 0
pause
"../.venv/Scripts/python.exe" manage.py import_csv_data --verbosity 0
pause
"../.venv/Scripts/python.exe" manage.py createsuperuser --verbosity 0
pause
