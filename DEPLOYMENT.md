# Enterprise ETL Pipeline & Data Warehouse Synchronizer - Deployment Documentation

This guide provides a comprehensive overview of setup, configuration, local docker deployment, production staging, and rollback procedures.

---

## 1. Environment Configuration

Copy `.env.example` to `.env` and fill in the required credentials:

```bash
# PostgreSQL target credentials
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/enterprise_etl

# Stripe credentials
STRIPE_SECRET_KEY=sk_test_...

# Salesforce credentials
SF_CLIENT_ID=3MVG9...
SF_CLIENT_SECRET=188...
SF_USERNAME=admin@salesforce.com
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_token

# Zendesk credentials
ZENDESK_SUBDOMAIN=your_subdomain
ZENDESK_EMAIL=admin@company.com
ZENDESK_TOKEN=your_token

# SMTP server credentials
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifier@company.com
SMTP_PASSWORD=smtp_password
EMAIL_FROM=notifier@company.com
EMAIL_TO=admin@company.com

# Slack alerts webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

---

## 2. Local Container Deployment (Docker Compose)

The pipeline is packaged with a Celery-based Airflow cluster.

### Commands

1. **Build and start services**:
   ```bash
   docker compose up -d --build
   ```

2. **Check service status**:
   ```bash
   docker compose ps
   ```

3. **View logs**:
   ```bash
   docker compose logs -f
   ```

4. **Shutdown services**:
   ```bash
   docker compose down -v
   ```

Upon startup, the PostgreSQL container initializes two databases: `airflow` and `enterprise_etl`. The `airflow-init` service automatically initializes the Airflow database metadata and creates an admin user (username: `admin`, password: `admin`).

Airflow web interface is accessible at `http://localhost:8080`.

---

## 3. Snowflake Warehouse Setup

To provision the required structures in Snowflake:

1. Configure Snowflake environment parameters:
   - `SNOWFLAKE_ACCOUNT`
   - `SNOWFLAKE_USER`
   - `SNOWFLAKE_PASSWORD`
   - `SNOWFLAKE_ROLE`
   - `SNOWFLAKE_WAREHOUSE`
   - `SNOWFLAKE_DATABASE`

2. Run the Snowflake initialization script:
   ```bash
   python loading/snowflake_setup.py
   ```
   *Note: This script establishes the three layers (RAW, STAGING, ANALYTICS), RBAC roles, and provisions tables.*

---

## 4. Run the Pipeline Locally (CLI Mode)

To execute the entire end-to-end pipeline (extraction -> transformation -> loading -> validation -> alerts) from the command line:

```bash
python run_pipeline.py
```
This script runs in *synthetic mode* automatically if credentials are not configured, verifying the system end-to-end without failing due to API key issues.

---

## 5. Deployment Strategy & Rollback Plan

### Blue-Green Zero-Downtime Database Deployment
1. When altering table schemas, apply backward-compatible migrations:
   - First add new nullable columns.
   - Deploy code updates that write to both new and old fields.
   - Run a backfill for existing rows.
   - Deploy code updates that read from the new columns.
   - Remove old columns (drop).
2. If using Snowflake, leverage **Zero-Copy Cloning** to instantly branch the analytics schema before schema changes, ensuring an instantaneous restore checkpoint.

### Rollback Procedures
- **Code rollbacks**: In GitHub Actions, trigger a rollback workflow that checks out the previous tag/commit, builds and re-tags the image as `latest`, and restarts the Docker services.
- **Database rollbacks**: Apply database schema undo scripts (or Alembic down migrations).
- **Snowflake rollbacks**: Revert back to the cloned schema branch by swapping tables:
  ```sql
  ALTER TABLE customers RENAME TO customers_failed;
  ALTER TABLE customers_clone RENAME TO customers;
  ```
