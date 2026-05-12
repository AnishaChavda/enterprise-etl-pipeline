# Enterprise ETL Pipeline & Data Warehouse Synchronizer

## Project Description

Enterprise ETL Pipeline & Data Warehouse Synchronizer is a production-level Python data engineering project designed to automate the extraction, transformation, and loading (ETL) of business data from multiple third-party APIs into a centralized PostgreSQL data warehouse.

The system integrates APIs such as Stripe and Salesforce to collect raw business data while handling pagination, API rate limits, retry mechanisms, and secure authentication. Extracted data is processed using Pandas and Polars for cleaning, validation, transformation, and standardization into a unified schema.

The transformed data is loaded into a PostgreSQL warehouse using SQLAlchemy with support for incremental loading and upsert operations to prevent duplicate records. Apache Airflow is used for workflow orchestration and scheduled daily ETL execution.

The project also includes Docker containerization, logging, testing, CI/CD-ready structure, and optional AWS S3 integration for intermediate storage. The main objective is to build a scalable, secure, and reliable ETL pipeline that creates a single source of truth for analytics and reporting.

## Tech Stack

- Python 3.11+
- Pandas / Polars
- PostgreSQL
- SQLAlchemy
- Apache Airflow
- Requests
- Pydantic
- Tenacity
- Docker
- AWS S3

## Features

- Automated ETL Workflow
- API Integration
- Data Cleaning & Transformation
- Incremental Data Loading
- Error Handling & Logging
- Workflow Scheduling with Airflow
- Docker Support
- CI/CD Ready Structure
- Team Collaboration using GitHub
