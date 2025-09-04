FROM python:3.12-alpine

RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    bash \
    libffi-dev \
    musl-dev \
    linux-headers \
    && python -m ensurepip \
    && pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY . /app/

CMD ["poetry", "run", "python", "main.py"]
