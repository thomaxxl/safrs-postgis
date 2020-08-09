## Overview

Docker image for safrs + psql + postgis

## Run

set the `SWAGGER_HOST` and run docker-compose:

```bash
SWAGGER_HOST=192.168.235.136 docker-compose up
```

## Swagger Configuration

The docker-compose.yml contains following environment variables:

```
SWAGGER_HOST: $SWAGGER_HOST
SWAGGER_PORT: 1237
```

change them accordingly
