ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL:+$REPOSITORY_URL/base/}deps-tesseract-5-3-2:3.12.11 AS python-base


ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    VENV_PATH=/app/.venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib" \
    OCR_ENGINE=TESSERACT
ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"


FROM python-base as downloading

WORKDIR /tmp/tesseract-ocr/

RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata_fast/raw/main/bel.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata_best/raw/main/rus.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/ukr.traineddata \
    && wget  https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata


FROM python-base as build

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        libcurl4-openssl-dev libssl-dev \
        python3-pip

ENV OCR_ENABLE_CUDA_GPU=false

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./engine_src/tesseract_env/pyproject.toml ./engine_src/tesseract_env/poetry.lock* /app/

# Allow installing dev dependencies to run tests
COPY ./vendors /vendors
COPY ./engine_src/deps_ocr_engines/infrastructure/engines /app/deps_ocr_engines/infrastructure/engines

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH python3 - \
    && poetry --version \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-root --only main --no-cache -E tesseract-engine \
    && /app/.venv/bin/pip uninstall --yes opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python opencv-contrib-python-headless \
    && /app/.venv/bin/pip install --no-cache-dir opencv-contrib-python-headless==4.8.1.78

ARG USER=deps
ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID $USER && \
    useradd --no-log-init -u $UID -g $GID -ms /bin/bash $USER

COPY --from=downloading /tmp/tesseract-ocr/ /usr/local/share/tessdata/

# Get tesseract micr models for Chetan Jakkoju to extract micr bank check data
COPY ./etc/deps-ocr-api-gateway/models/tesseract-ocr/ /usr/local/share/tessdata/

FROM build as develop

RUN poetry install --no-interaction --no-ansi --no-root --no-cache -E tesseract-engine \
    && /app/.venv/bin/pip uninstall --yes opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python opencv-contrib-python-headless \
    && /app/.venv/bin/pip install --no-cache-dir opencv-contrib-python-headless==4.8.1.78

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

COPY --from=build /usr/local/share/tessdata/ /usr/local/share/tessdata/

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

