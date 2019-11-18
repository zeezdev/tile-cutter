release: mkdir -p media && mkdir -p logs && python manage.py migrate && npm install -g bower && ./node_modules/bower/bin/bower update
web: gunicorn cutter.wsgi --log-file -