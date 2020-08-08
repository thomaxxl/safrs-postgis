FROM python:3.7-alpine
WORKDIR /app
ENV PYTHONPATH /app
COPY . .

# psycopg2 needs build tools
RUN apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    git postgresql-client

RUN apk --update add build-base libxslt-dev

RUN apk add --virtual .build-deps \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        gcc libc-dev geos-dev geos && \
    runDeps="$(scanelf --needed --nobanner --recursive /usr/local \
    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
    | xargs -r apk info --installed \
    | sort -u)" && \
    apk add --virtual .rundeps $runDeps

RUN geos-config --cflags

RUN pip install --disable-pip-version-check -r requirements.txt

RUN apk del build-base python3-dev && \
    rm -rf /var/cache/apk/*

# Use CMD instead of ENTRYPOINT to allow easier run of other commands (like "sh")
# Also Pycharm can only handle CMD overrides
CMD ["/app/entrypoint.sh"]
