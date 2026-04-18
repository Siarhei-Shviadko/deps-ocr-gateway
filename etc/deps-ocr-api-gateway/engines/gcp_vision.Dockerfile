ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL}/base/python:3.12.11-slim AS python-base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    VENV_PATH=/app/.venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib" \
    OCR_ENGINE=GCP_VISION
ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

FROM python-base as build

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libcurl4-openssl-dev libssl-dev

WORKDIR /app/

# # Copy poetry.lock* in case it doesn't exist in the repo
COPY ./engine_src/pyproject.toml ./engine_src/poetry.lock* /app/

# # Allow installing dev dependencies to run tests
COPY ./vendors /vendors
COPY ./engine_src/deps_ocr_engines/infrastructure/engines /app/deps_ocr_engines/infrastructure/engines

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH python3 - \
    && poetry --version \
    && poetry config virtualenvs.in-project true

RUN poetry install --no-interaction --no-ansi --no-root --only main --no-cache -E gcpvision-engine  \
    && rm -rf /root/.cache/pypoetry/artifacts /root/.cache/pypoetry/cache

ARG USER=deps
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID $USER && \
    useradd --no-log-init -u $UID -g $GID -ms /bin/bash $USER

FROM build as develop

RUN poetry install --no-interaction --no-ansi --no-root --no-cache -E gcpvision-engine \
    && rm -rf /root/.cache/pypoetry/artifacts /root/.cache/pypoetry/cache

COPY ./engine_src/deps_ocr_engines /app/deps_ocr_engines
COPY ./engine_src/engines_tests /app/engines_tests
COPY ./engine_src/engines_setup.cfg /app/setup.cfg

ARG BUILD_HASH
ARG BUILD_TAG
ARG BUILD_DATE

ENV SERVICE_INFO_HASH=$BUILD_HASH \
    SERVICE_INFO_TAG=$BUILD_TAG \
    SERVICE_INFO_DATE=$BUILD_DATE

USER deps

CMD ["python", "deps_ocr_engines", "serve"]

FROM build as runtime

COPY ./vendors /vendors
COPY ./engine_src/deps_ocr_engines /app/deps_ocr_engines
COPY ./engine_src/engines_tests /app/engines_tests
COPY ./engine_src/engines_setup.cfg /app/setup.cfg

ARG BUILD_HASH
ARG BUILD_TAG
ARG BUILD_DATE

ENV SERVICE_INFO_HASH=$BUILD_HASH \
    SERVICE_INFO_TAG=$BUILD_TAG \
    SERVICE_INFO_DATE=$BUILD_DATE

USER deps

CMD ["python", "deps_ocr_engines", "serve"]
