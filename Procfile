cache: redis-server /usr/local/etc/redis.conf
web: inveniomanage runserver
worker: celery worker --purge -E -A invenio.celery.celery --loglevel=INFO --workdir=$VIRTUAL_ENV
workermon: flower --broker=redis://localhost:6379/1
