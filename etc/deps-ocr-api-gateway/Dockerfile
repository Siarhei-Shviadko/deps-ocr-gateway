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
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"

ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        wget \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        libcurl4-openssl-dev libssl-dev

FROM python-base as build

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./src/pyproject.toml ./src/poetry.lock* /app/

# Allow installing dev dependencies to run tests
COPY ./vendors /vendors
COPY ./src/deps_ocr_gateway /app/deps_ocr_gateway

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH python3 - \
    && poetry --version \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root --only main --no-cache --all-extras \
    && rm -rf /root/.cache/pypoetry/artifacts /root/.cache/pypoetry/cache

ARG USER=deps
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID $USER && \
    useradd --no-log-init -u $UID -g $GID -ms /bin/bash $USER

FROM build as develop

RUN poetry install --no-interaction --no-ansi --no-root --no-cache --all-extras \
    && rm -rf /root/.cache/pypoetry/artifacts /root/.cache/pypoetry/cache

COPY ./src/deps_ocr_gateway /app/deps_ocr_gateway
COPY ./src/tests /app/tests
COPY ./src/setup.cfg /app/setup.cfg

ARG BUILD_HASH
ARG BUILD_TAG
ARG BUILD_DATE

ENV SERVICE_INFO_HASH=$BUILD_HASH \
    SERVICE_INFO_TAG=$BUILD_TAG \
    SERVICE_INFO_DATE=$BUILD_DATE

USER deps

CMD ["python", "deps_ocr_gateway", "serve"]

FROM build as runtime

COPY ./vendors /vendors
COPY ./src/deps_ocr_gateway /app/deps_ocr_gateway
COPY ./src/tests /app/gateway_tests
COPY ./src/setup.cfg /app/setup.cfg

ARG BUILD_HASH
ARG BUILD_TAG
ARG BUILD_DATE

ENV SERVICE_INFO_HASH=$BUILD_HASH \
    SERVICE_INFO_TAG=$BUILD_TAG \
    SERVICE_INFO_DATE=$BUILD_DATE

USER deps

CMD ["python", "deps_ocr_gateway", "serve"]
