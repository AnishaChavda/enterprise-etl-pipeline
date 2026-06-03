
# Enterprise ETL Pipeline & Data Warehouse Synchronizer

## Project Description

Enterprise ETL Pipeline & Data Warehouse Synchronizer is a production-level Python data engineering project designed to automate the extraction, transformation, and loading (ETL) of business data from multiple third-party APIs into a centralized PostgreSQL data warehouse.

The system integrates APIs such as Stripe and Salesforce to collect raw business data while handling pagination, API rate limits, retry mechanisms, and secure authentication. Extracted data is processed using Pandas and Polars for cleaning, validation, transformation, and standardization into a unified schema.

The transformed data is loaded into a PostgreSQL warehouse using SQLAlchemy with support for incremental loading and upsert operations to prevent duplicate records. Apache Airflow is used for workflow orchestration and scheduled daily ETL execution.

The project also includes Docker containerization, logging, testing, CI/CD-ready structure, and optional AWS S3 integration for intermediate storage. The main objective is to build a scalable, secure, and reliable ETL pipeline that creates a single source of truth for analytics and reporting.

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

# Project Architecture

Stripe API
→ Raw JSON Extraction
→ Data Cleaning
→ Schema Mapping
→ Data Validation
→ Final Dataset Generation

# Technologies Used
Python
Pandas
Pydantic
Stripe API
Requests
Logging
Git & GitHub

# Project Structure
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
