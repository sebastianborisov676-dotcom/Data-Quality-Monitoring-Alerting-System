# Data Quality Monitoring & Alerting System

A Python-based data quality monitoring system that ingests market data, validates it against configurable quality checks, stores results in SQLite, generates alerts for failed checks, and exports monitoring reports.

The project is designed to resemble a small internal monitoring tool used by engineering or data teams to detect and investigate data-quality problems.


## Features

- CSV market-data ingestion with Pandas
- SQLite persistence using SQLAlchemy
- Configurable data-quality checks
- Missing-value, value-range and non-negative validation
- Duplicate protection for `(symbol, timestamp)` records
- Safe UPSERT logic for repeated ingestion
- Persistent storage of check results
- Automatic alert creation for failed checks
- Querying of the latest result for each check
- Tracking of currently active alerts
- CSV export of check results and active alerts
- Structured application logging
- Error handling around ingestion, database operations and reporting

## Technology Stack

- **Python** - application logic and workflow orchestration
- **Pandas** - CSV ingestion and data processing
- **SQLAlchemy** - ORM, database sessions and queries
- **SQLite** - relational persistence
- **Python logging** - application and diagnostic logging
- **Git/GitHub** - version control and project history


## Project Structure

```text
Data-Quality-Monitoring-Alerting-System/
├── main.py                  # Application entry point and workflow orchestration
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── .gitignore               # Git ignore rules
├── data/
│   └── sample_market_data.csv   # Sample input dataset
└── src/
    ├── __init__.py
    ├── alerts.py            # Alert output logic
    ├── checks.py            # Data-quality validation checks
    ├── db.py                # Database engine and session configuration
    ├── db_checks.py         # Persistence of check results and alerts
    ├── db_ingest.py         # Database ingestion and UPSERT logic
    ├── db_reports.py        # Queries for latest checks and active alerts
    ├── ingest.py            # CSV ingestion logic
    ├── init_db.py           # Database initialization
    ├── logger.py            # Logging configuration
    ├── models.py            # SQLAlchemy database models
    ├── report_export.py     # CSV report export logic
    └── reporting.py         # Report generation and logging workflow
```

Local runtime files such as the SQLite database, generated reports, virtual environments, editor settings, and Python cache files are excluded from version control through `.gitignore`.


## System Architecture

```text
CSV Input
   ↓
Ingestion Layer
   ├── ingest.py
   └── db_ingest.py
   ↓
SQLite Database
   ├── market_data
   ├── data_checks
   └── alerts
   ↓
Validation Layer
   └── checks.py
   ↓
Persistence Layer
   └── db_checks.py
   ↓
Reporting Layer
   ├── db_reports.py
   ├── reporting.py
   └── report_export.py
   ↓
Outputs
   ├── Structured logs
   ├── Active alerts
   └── CSV monitoring reports
```

The application workflow is coordinated from `main.py`, which initializes the database, ingests the sample dataset, runs the configured quality checks, stores the results, queries the latest monitoring state, exports reports, and logs or raises alerts for failed checks.


## Database Schema

The application uses three main tables: `market_data`, `data_checks`, and `alerts`.

### `market_data`

Stores the ingested market records.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `timestamp` | TEXT | Market-data timestamp |
| `symbol` | TEXT | Asset symbol |
| `price` | FLOAT | Asset price; may be null |
| `volume` | INTEGER | Trading volume; may be null |

Database constraints:

- `price` must be non-negative when present
- `volume` must be non-negative when present
- `(symbol, timestamp)` must be unique

The unique constraint prevents the same market record from being inserted multiple times and supports the project's UPSERT ingestion logic.

### `data_checks`

Stores the history of data-quality check results.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `check_name` | TEXT | Name of the validation check |
| `passed` | INTEGER | `1` for pass, `0` for fail |
| `message` | TEXT | Human-readable check result |
| `created_at` | DATETIME | Time the result was created |

The application keeps a limited history of recent check results rather than allowing the table to grow indefinitely.

### `alerts`

Stores the currently active data-quality issues.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `check_id` | INTEGER | Foreign key to `data_checks.id` |
| `severity` | TEXT | Alert severity, currently `warning` |
| `message` | TEXT | Description of the failed check |
| `created_at` | DATETIME | Time the alert was created |

Each alert is linked to the `DataCheck` result that triggered it.

The alert table represents the current monitoring state rather than a permanent alert history. When a check passes, any existing alert for that check type is removed. When it fails again, the previous alert is replaced with the latest failure.


## Requirements

- Python 3.11+
- `pip`
- Git

SQLite is used through Python's database tooling, so no separate database server is required.

## Setup

Clone the repository:

```bash
git clone https://github.com/sebastianborisov676-dotcom/Data-Quality-Monitoring-Alerting-System.git
cd Data-Quality-Monitoring-Alerting-System
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

Linux / macOS:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

The project currently uses Pandas, SQLAlchemy, NumPy, and supporting Python packages defined in `requirements.txt`.

## Running the Application

From the project root:

```bash
python main.py
```

On each run, the application:

1. initializes the local SQLite database if required
2. loads the sample market dataset
3. stores or updates market records
4. runs the configured data-quality checks
5. stores check results and updates active alerts
6. queries the latest monitoring state
7. exports CSV reports
8. logs the final monitoring results

Generated runtime files such as the SQLite database and CSV reports are excluded from Git version control.


## SQL Examples

Although the application uses SQLAlchemy for persistence and queries, the project also includes direct SQL examples to demonstrate the underlying database operations.

### UPSERT Market Data

The `(symbol, timestamp)` unique constraint allows repeated ingestion to update an existing market record instead of creating a duplicate.

```sql
INSERT INTO market_data (timestamp, symbol, price, volume)
VALUES ('2026-02-08 10:02:00', 'AAPL', 999.99, 777)
ON CONFLICT (symbol, timestamp)
DO UPDATE SET
    price = excluded.price,
    volume = excluded.volume;
```

### View the Latest Result for Each Check

```sql
SELECT dc.*
FROM data_checks dc
JOIN (
    SELECT check_name, MAX(id) AS latest_id
    FROM data_checks
    GROUP BY check_name
) latest
ON dc.id = latest.latest_id
ORDER BY dc.id DESC;
```

This produces the current monitoring view by returning only the newest result for each data-quality check.

### Inspect Active Alerts

```sql
SELECT
    a.id AS alert_id,
    a.severity,
    dc.check_name,
    a.message,
    a.created_at
FROM alerts a
JOIN data_checks dc
    ON a.check_id = dc.id
ORDER BY a.id DESC;
```

These queries mirror the same concepts implemented through SQLAlchemy in the Python application.

## Possible Future Improvements

- Automated or scheduled data ingestion
- Email or Slack alert integration
- REST API for accessing monitoring results
- Web dashboard for viewing checks, alerts, and historical trends
- Automated tests for validation, persistence, and reporting logic
- Additional configurable data-quality rules
- Migration from SQLite to PostgreSQL for a more production-like setup
