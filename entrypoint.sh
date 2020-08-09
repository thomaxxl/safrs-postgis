#!/usr/bin/env sh


if [[ -z ${SWAGGER_HOST} ]]; then
  echo "Warning: SWAGGER_HOST environment variable not set, using localhost" >&2
  export SWAGGER_HOST=localhost
fi

init_db(){
  echo "INIT DB"
  sleep 10
  psql -h "${DB_HOST}" -U "${DB_USER}" -c "create database ${DB_NAME}"
  psql -h "${DB_HOST}" -U "${DB_USER}" "${DB_NAME}" < postgis-init.sql
}


export PGPASSFILE=$(mktemp)
echo "*:*:*:${DB_USER}:${DB_PWD}" > "${PGPASSFILE}"
chmod 600 "${PGPASSFILE}"


for i in {1..10}
do
  # wait to be sure postgres db is up
  sleep 9
  # test psql service connection
  ( ping -c1 "${DB_HOST}" && \
    psql -h "${DB_HOST}" -U "${DB_USER}" postgres -c '\l' ) > /dev/null 2>&1 && break
  echo "Waiting for ${DB_HOST}"
done

psql -h "${DB_HOST}" -U "${DB_USER}" -c '\c safrs' || init_db


if [ $FLASK_ENV = "development" ]; then
    ## Skip the workers when in develop mode
    exec gunicorn \
        --bind :80 \
        --access-logfile - \
        --graceful-timeout 2 \
        --timeout 10 \
        --reload \
        "app:run_app()"
else
    exit
    exec gunicorn \
        --bind :80 \
        --access-logfile - \
        --graceful-timeout 10 \
        --timeout 120 \
        --workers 4 \
        "app:run_app()"
fi
