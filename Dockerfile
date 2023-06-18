# Use the official Python image as the base
FROM python:3.10

# Configure Poetry
ENV POETRY_VERSION=1.5.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install PostgreSQL client
# RUN apt-get update && apt-get install -y postgresql-client

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry check
RUN poetry lock
RUN poetry install --no-root

# Install psycopg2
# RUN apt-get update && apt-get install -y libpq-dev
# RUN poetry run pip install psycopg2-binary

# Copy the CSV files to the container
COPY /data/regions_clean.csv /var/lib/postgresql/csv_data/
COPY /data/Athletes_summer_games_clean.csv /var/lib/postgresql/csv_data/
COPY /data/Athletes_winter_games_clean.csv /var/lib/postgresql/csv_data/

# WORKDIR /app/athlete_api

# Run the setup script to create the database tables and import data
# RUN python data_loader.py

COPY . /app 
# Run your app
# COPY athlete_api /app
# COPY tests /app

EXPOSE 8000
CMD [ "poetry", "run", "uvicorn", "athlete_api.main:app" ]