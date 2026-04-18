# DEPS OCR GATEWAY

### Description

Service for making OCR using different engines

## Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.

## Local development

### Building service
```bash
# Setup environment variables for run
make install

# Fill required variables in .env file.
# Actual information about variables could be found at KB onboarding page
make build
```

### General workflow

By default, the dependencies are managed with [Poetry](https://python-poetry.org/), go there and install it.

By default, only one TESSERACT engin is enabled.

To add/remove an additional engine in a local project, set the appropriate env variable in the
`etc/deps-ocr-gateway/dev.env` file as `true/false`", for example `EASYOCR_ENABLED=true`, and
uncomment/comment out the corresponding services in docker-compose.yml and docker-compose.override.yml.

Run service by `make run` command and open Swagger documentation at `http://localhost:5010/api/ocr/docs`

For production run, set `DEBUG=false` and get running instance at `http://localhost:8000/api/ocr/v1/docs`

### Running tests

Before running tests, linters, etc. make sure that you've built docker image with dev dependencies. For building it,
run:

```console
docker-compose build ocr
```
