# Enterprise ETL Pipeline & Data Warehouse Platform

## Overview

This repository now includes a complete production-grade ETL pipeline with:

- PostgreSQL data warehouse schema and SQLAlchemy ORM models
- Snowflake connection and warehouse/schema provisioning
- Incremental loading, upsert handling, and audit metadata tracking
- Apache Airflow DAGs for orchestration and SLA monitoring
- Slack and email alerting for failures and success notifications
- Docker containerization and local orchestration via Docker Compose
- GitHub Actions CI/CD validation, linting, and Docker build
- Modular extraction, transformation, and loading components

## Architecture

- `extraction/`: API extraction logic for Stripe, Salesforce, and Zendesk
- `etl/`: orchestration utilities, transform functions, and loaders
- `db/`: database connectivity and ORM model definitions
- `airflow/dags/`: Airflow DAG definitions for daily workflows
- `utils/`: notification and monitoring utilities
- `docker/`: container build definitions
- `tests/`: unit tests for models, loaders, and alerts

## Setup

1. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your PostgreSQL, Snowflake, Slack, and SMTP credentials.

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Run Locally

Execute the pipeline from the repository root:

```bash
python run_pipeline.py
```

## Docker and Airflow

Start the application, PostgreSQL, Redis, and Airflow services with:

```bash
docker compose up --build
```

- Airflow Webserver: `http://localhost:8080`
- PostgreSQL: `localhost:5432`

## Airflow DAGs

The main orchestration DAG is:

- `airflow/dags/daily_etl_pipeline.py`

It includes tasks for extraction, validation, transformation, staging/warehouse loading, and notifications.

## CI/CD

GitHub Actions are configured in `.github/workflows/ci-cd.yml` to run on push and pull requests.

Pipeline steps:

1. Install dependencies
2. Run formatting check with `black`
3. Lint with `flake8`
4. Security scan with `bandit`
5. Run unit tests with `pytest`
6. Build Docker image

## Testing

Run unit tests locally:

```bash
pytest -q
```

## Deployment

Use Docker Compose for local development and leverage the GitHub Actions workflow for build validation.

### Notes

- PostgreSQL schema management is handled in `db/postgres.py`
- Snowflake initialization is handled in `db/snowflake.py`
- Slack and email alerts are configurable via `.env`
- ETL metadata and job runs are stored in the `audit` schema
