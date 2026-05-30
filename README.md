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

# Project Structure
enterprise-etl-pipeline/
│
├── extraction/
│   ├── __init__.py
│   ├── customers_extractor.py
│   ├── charges_extractor.py
│   ├── payments_extractor.py
│   └── salesforce_connector.py
│
├── utils/
│   ├── __init__.py
│   └── stripe_client.py
│
├── configs/
│   ├── __init__.py
│   └── config.py
│
├── logs/
│   ├── customer_extraction.log
│   ├── charges_extraction.log
│   └── payments_extraction.log
│
├── data/
│   └── raw/
│       └── stripe/
│           ├── customers/
│           ├── charges/
│           └── payments/
│
├── tests/
│
├── .env
├── .env.example
├── README.md
├── requirements.txt
└── run_pipeline.py

# Future Improvements

- Salesforce integration
- Data transformation layer
- Database loading
- Airflow scheduling
- Docker deployment
