release: mkdir -p media && mkdir -p logs && python manage.py migrate
web: gunicorn cutter.wsgi --log-file -