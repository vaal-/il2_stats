cd ../src
"../.venv/Scripts/waitress-serve.exe" --host=localhost --port=80 --threads=10 --asyncore-use-poll --ident="IL2 stats" --max-request-body-size=5242880 core.wsgi:application
pause
