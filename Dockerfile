# ==========================================
# STAGE 1: Builder / Tester
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies to a virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run basic syntax validation and checks
RUN python -m py_compile run_pipeline.py

# ==========================================
# STAGE 2: Production Airflow & Application
# ==========================================
FROM apache/airflow:2.7.1-python3.11

USER root

# Install postgres client and compilers for python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements and install
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --user -r /requirements.txt

# Copy project files into Airflow environment
COPY --chown=airflow:root . /opt/airflow/

ENV PYTHONPATH="/opt/airflow"
