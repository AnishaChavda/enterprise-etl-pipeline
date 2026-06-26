
# Enterprise ETL Pipeline & Data Warehouse Synchronizer
# Enterprise ETL Pipeline & Data Warehouse Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)
![Airflow](https://img.shields.io/badge/Airflow-2.x-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Snowflake](https://img.shields.io/badge/Snowflake-Ready-lightblue.svg)

## 📖 Overview

The **Enterprise ETL Pipeline** is a robust, production-grade data integration system designed to consolidate business data from disparate SaaS platforms into a centralized Data Warehouse. 

It handles automated extraction from **Stripe**, **Salesforce**, and **Zendesk**, runs rigorous data validation, transforms it into unified schemas, and performs incremental loading (upserts) into **PostgreSQL** or **Snowflake**. The entire workflow is orchestratable via **Apache Airflow**, fully containerized using **Docker Compose**, and heavily monitored with **Slack and Email** alerts.

---

# APIs Used

- Stripe Customers API
- Stripe Charges API
- Stripe Payment Intents API


# Features

- Modular extraction architecture
- Multiple Stripe API integrations
- Config-driven development
- Retry handling
- Logging system
- Raw JSON data storage
- Enterprise-style project structure

## Technologies Used

* Python
* Pandas
* Pydantic
* Stripe API
* Requests
* Logging
* Git & GitHub

---

## Project Architecture

```text
Stripe API
    ↓
Raw JSON Extraction
    ↓
Data Cleaning
    ↓
Schema Mapping
    ↓
Data Validation
    ↓
Final Dataset Generation
    ↓
Database Loading (Future)
```

---

## Project Structure

```text
enterprise-etl-pipeline/
│
├── extraction/
│   ├── customers_extractor.py
│   ├── charges_extractor.py
│   ├── payments_extractor.py
│   └── salesforce_connector.py
│
├── transformation/
│   ├── customers_transform.py
│   ├── customers_cleaning.py
│   ├── customers_transform_mapping.py
│   ├── pipeline.py
│   └── final_dataset.py
│
├── validation/
│   ├── __init__.py
│   ├── customer_schema.py
│   └── validate_customers.py
│
├── utils/
│   └── stripe_client.py
│
├── configs/
│   └── config.py
│
├── logs/
│   ├── customer_extraction.log
│   ├── charges_extraction.log
│   └── payments_extraction.log
│
├── data/
│   ├── raw/
│   │   └── stripe/
│   │       ├── customers/
│   │       ├── charges/
│   │       └── payments/
│   │
│   ├── transformed/
│   │   └── customers.csv
│   │
│   ├── processed/
│   │   └── customers_clean.csv
│   │
│   ├── mapped/
│   │   └── customers_mapped.csv
│   │
│   ├── validated/
│   │   └── customers_validated.csv
│   │
│   └── final/
│       └── customers_final.csv
│
├── tests/
│
├── .env
├── .env.example
├── requirements.txt
├── run_pipeline.py
└── README.md
```

# How to Run
Activate Virtual Environment

venv\Scripts\activate

Run Transformation Pipeline

python transformation/pipeline.py

Run Validation

python validation/validate_customers.py

Generate Final Dataset

python transformation/final_dataset.py

# Output

Final cleaned datasets are stored inside:

data/final/

customers_final.csv
# Future Improvements

- Salesforce integration
- Data transformation layer
- Database loading
- Airflow scheduling
- Docker deployment
## Team Members
- Anisha Chavda
- krushil lukhi

### Core Capabilities
- **Multi-Source Extraction:** Pulls raw data from Stripe (Customers, Charges, Subscriptions), Salesforce (Accounts, Opportunities), and Zendesk (Tickets).
- **Data Validation & Transformation:** Uses Python and Pydantic to clean, map, and strictly validate data formats before loading.
- **Incremental Loading:** Optimized loading using cursors to only process new/updated records, supporting UPSERT/MERGE operations.
- **Audit Logging:** Every ETL job run is tracked with metadata (status, rows processed, cursor position, duration, and error messages).
- **Automated Alerts:** Real-time Slack webhooks and SMTP email notifications on pipeline success or failure.

### Tech Stack
- **Languages:** Python
- **Databases:** PostgreSQL (Primary DWH & Airflow backend), Snowflake (Data Warehouse integration)
- **Orchestration:** Apache Airflow (with CeleryExecutor & Redis)
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions (Black, Flake8, Bandit security scanning, Pytest)

---

## 📂 Project Structure

```text
enterprise-etl-pipeline 2/
├── airflow/dags/      # Apache Airflow DAGs (e.g., daily_etl_pipeline.py)
├── db/                # Database connectivity (postgres.py, snowflake.py)
├── docker/            # Dockerfiles and DB initialization scripts
├── extraction/        # API integrators (stripe, salesforce, zendesk)
├── loading/           # SQLAlchemy models and Incremental Loader logic
├── transformation/    # Data transformation and mapping functions
├── validation/        # Pydantic validation models
├── utils/             # Monitoring, Logging, and Notifications
├── tests/             # Pytest suite for unit/integration testing
├── docker-compose.yml # Local deployment infrastructure
├── run_pipeline.py    # Local standalone execution script
└── requirements.txt   # Python dependencies
```

---

## 🚀 Getting Started

### 1. Environment Setup

Copy the environment template and configure your credentials:
```bash
cp .env.example .env
```
Fill out `.env` with your API keys (Stripe, Salesforce, Zendesk), Database URLs, and Alert credentials (Slack Webhook, SMTP).

### 2. Running Locally (Without Docker)

You can run the pipeline directly using Python via the entrypoint script. Make sure you are in the correct directory.

```bash
# 1. Activate your virtual environment (if using one)
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python run_pipeline.py
```
This will initialize schemas, run extraction, perform transformations, validate data, and load it into your local DB while generating a health dashboard report in your console.

### 3. Running with Docker & Airflow (Recommended)

To spin up the entire architecture (PostgreSQL, Redis, Airflow Webserver, Scheduler, and Worker):

```bash
docker compose up --build -d
```
- **Airflow Webserver:** [http://localhost:8080](http://localhost:8080) (Default login: `admin` / `admin`)
- **PostgreSQL Database:** `localhost:5432`

---

## ⏱️ Orchestration with Airflow

The main DAG is located at `airflow/dags/daily_etl_pipeline.py`.
It breaks down the `run_pipeline.py` script into distinct logical tasks:
1. `extract_data`
2. `transform_and_load`
3. `data_quality_checks`

Airflow tracks SLA (Service Level Agreements) and alerts if the pipeline is taking longer than expected or fails.

---

## 🧪 Testing and CI/CD

Run the test suite locally:
```bash
pytest -q
```

**GitHub Actions** CI/CD is configured to automatically:
1. Format code using `black`
2. Lint code using `flake8`
3. Run security vulnerability scans with `bandit`
4. Execute `pytest` test suite
5. Validate the Docker build

---

## 📊 Monitoring & Data Quality

- **Data Quality:** Validation is strictly enforced. Any records containing negative invoice amounts, invalid email formats, or missing primary keys are dropped or quarantined, and a `ValueError` is raised if critical constraints fail.
- **Health Dashboard:** A summary report is printed after execution, including Success/Failure rates, Average Duration, and Data Warehouse Freshness.
- **Alerts:** Failing tasks immediately trigger notifications via Email (SMTP) and Slack, including the traceback error for fast incident resolution.
