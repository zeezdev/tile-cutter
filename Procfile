release: mkdir -p media && mkdir -p logs && python manage.py migrate && ./node_modules/bower/bin/bower update
web: gunicorn cutter.wsgi --log-file -