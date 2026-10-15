# Data Quality Monitoring & Alerting System

This project implements a small internal-style data quality monitoring tool that:

- Ingests market data from CSV
- Runs data quality checks
- Logs issues clearly
- Generates alerts for failed checks

This project was built to simulate a small internal data monitoring tool used in engineering teams.

## Features

- CSV-based market data ingestion
- SQLite database storage
- Data quality validation checks
- Duplicate detection on `(symbol, timestamp)`
- Automatic alert generation for failed checks
- Safe UPSERT ingestion logic
- SQL queries for monitoring and debugging

## Technology Stack

- **Python** - application logic
- **SQLite** - relational database
- **SQLAlchemy** - database ORM
- **Pandas** - CSV ingestion and data processing
- **Python logging module** - structured logging 

---

## 📁 Project Structure

```
Project/
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies
├── README.md            # Project documentation
├── project.db           # SQLite database file
├── data/
│   └── sample_market_data.csv   # Sample input data
├── src/
│   ├── __init__.py
│   ├── alerts.py        # Alerting logic
│   ├── checks.py        # Data validation checks
│   ├── db.py            # Database connection/session setup
│   ├── db_ingest.py     # Database upsert logic
│   ├── ingest.py        # CSV ingestion logic
│   ├── init_db.py       # Database initialization
│   ├── logger.py        # Logging configuration
│   └── models.py        # SQLAlchemy models/schema
├── .gitignore           # Git ignore rules
└── venv/                # Virtual environment (not committed)
```

## System Architecture

```
CSV File
  ↓
Ingestion Layer (ingest.py)
  ↓
SQLite Database (market_data)
  ↓
Data Quality Checks (checks.py) 
  ↓
data_checks table
  ↓
Alert Generation
  ↓
alerts table
```
---

## Database Schema

The system uses three main tables:

### market_data

| Column    | Type            | Description                      |
|-----------|-----------------|--------------------------------- |
| id        | INTEGER (PK)    | Auto-incrementing row identifier |
| timestamp | TEXT (NOT NULL) | Market data timestamp            |
| symbol    | TEXT (NOT NULL) | Stock symbol                     |
| price     | REAL            | Asset price (must be >= 0)       |
| volume    | INTEGER         | Trading volume (must be >= 0)    |

Unique constraint:

(symbol, timestamp)

---

### data_checks

| Column     | Type               | Description                        |
|------------|--------------------|------------------------------------|
| id         | INTEGER (PK)       | Auto-incrementing check identifier |
| check_name | TEXT (NOT NULL)    | Name of validation check           |
| passed     | INTEGER (NOT NULL) | 1 = pass, 0 = fail                 |
| message    | TEXT (NOT NULL)    | Check result message               |
| created_at | TEXT               | Timestamp of check execution       |

---

### alerts

| Column     | Type            | Description                        |
|------------|-----------------|------------------------------------|
| id         | INTEGER (PK)    | Auto-incrementing alert identifier |
| check_id   | INTEGER (FK)    | Reference to data_checks.id        |
| severity   | TEXT (NOT NULL) | Alert level (warning / error)      |
| message    | TEXT (NOT NULL) | Alert message                      |
| created_at | TEXT            | Alert creation time                |
```
Relationship:

alerts.check_id → data_checks.id
```
---

## Requirements

- Python 3.9+
- SQLite3 

---

## ⚙️ Setup

From the project root:

### Create a virtual environment

```bash
python -m venv venv
```


### Activate the virtual environment

Linux / macOS:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```
## Running the Application

From the project root:

```bash
python main.py
```

## Database Usage (SQL Queries)

### Reset Database

```sql 
/*
If you ever get “UNIQUE constraint failed…” errors on rerun, it usually means old rows are still in market_data and you re-inserted the same (symbol, timestamp) again without upsert.
Example on how to Reset the Database for the given tables.
*/

DELETE FROM alerts;
DELETE FROM data_checks;
DELETE FROM market_data;

DELETE FROM sqlite_sequence
WHERE name IN ('alerts','data_checks','market_data');
```

### Insert/Upsert Market Data (Safe for Reruns)

```sql
/*
The market_data table has a unique constraint/index on (symbol, timestamp), so inserting the exact same (symbol, timestamp) twice will fail unless you UPSERT.
Example with Inserted two rows(one with missing price)
*/

INSERT INTO market_data (timestamp, symbol, price, volume)
VALUES ('2026-02-08 10:02:00', 'AAPL', 123.45, 1200);

INSERT INTO market_data (timestamp, symbol, price, volume)
VALUES ('2026-02-08 12:02:00', 'AAPL', NULL, 100);
/*
Upsert (update the existing row if it already exists.)
This example will update the existing (AAPL, 2026-02-08 10:02:00) row instead of failing.
*/

INSERT INTO market_data (timestamp, symbol, price, volume)
VALUES ('2026-02-08 10:02:00', 'AAPL', 999.99, 777)
ON CONFLICT (symbol, timestamp)
DO UPDATE SET
  price  = excluded.price,
  volume = excluded.volume;

-- This should update the price = 999.99 and volume = 777 
```


### Run Data Quality Checks (Inserting into `data_checks`)


The following queries run **data quality validations** against the `market_data` table and store the results in the `data_checks` table.

Each check records:

- the **name of the check**
- whether it **passed or failed**
- a **human-readable message describing the result**


#### Check 1 — Missing prices:

This check detects rows where `price` is **NULL**.

```sql
INSERT INTO data_checks (check_name, passed, message)
SELECT
  'missing_values_price' AS check_name,
  CASE WHEN (COUNT(*) - COUNT(price)) = 0 THEN 1 ELSE 0 END AS passed,
  CASE
    WHEN (COUNT(*) - COUNT(price)) = 0 THEN 'No missing prices'
    ELSE (COUNT(*) - COUNT(price)) || ' missing prices detected'
  END AS message
FROM market_data;
```

#### Check 2 — Duplicate (symbol, timestamp) collisions:

This check detects duplicate rows where the same `(symbol, timestamp)` combination appears more than once.

```sql
INSERT INTO data_checks (check_name, passed, message)
SELECT
  'duplicate_symbol_timestamp' AS check_name,
  CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END AS passed,
  CASE
    WHEN COUNT(*) = 0 THEN 'No duplicates of symbol and timestamp found.'
    ELSE COUNT(*) || ' duplicates of symbol and timestamp found.'
  END AS message
FROM (
  SELECT symbol, timestamp
  FROM market_data
  GROUP BY symbol, timestamp
  HAVING COUNT(*) > 1
) dups;

-- If a unique index on (symbol, timestamp) is already in place, then this should always pass unless the constraint has been disabled or avoided.
```

#### Check 3 - Zero volume rows:

This check detects and counts rows where volume = 0.

```sql 
INSERT INTO data_checks (check_name, passed, message)
SELECT
  'zero_volume' AS check_name,
  CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END AS passed,
  CASE
    WHEN COUNT(*) = 0 THEN 'No zero volume rows'
    ELSE COUNT(*) || ' zero volume rows detected'
  END AS message
FROM market_data
WHERE volume = 0;
```

### Generate Alerts from Failed Checks (no duplicates):

This query finds the newest failed check that has not yet triggered an alert and inserts it into the alerts table.

```sql
INSERT OR IGNORE INTO alerts (check_id, severity, message)
SELECT
  dc.id,
  'warning',
  dc.message
FROM data_checks dc
LEFT JOIN alerts a ON a.check_id = dc.id
WHERE dc.passed = 0
  AND a.check_id IS NULL
ORDER BY dc.id DESC
LIMIT 1;
```

### Debug Queries

```sql
SELECT * FROM market_data
ORDER BY id DESC;

SELECT * FROM data_checks
ORDER BY id DESC;

SELECT * FROM alerts
ORDER BY id DESC;
```

### View latest result per check_name (most useful monitoring view):

```sql
SELECT dc.*
FROM data_checks dc
JOIN (
  SELECT check_name, MAX(created_at) AS max_created_at
  FROM data_checks
  GROUP BY check_name
) latest
ON dc.check_name = latest.check_name
AND dc.created_at = latest.max_created_at
ORDER BY dc.created_at DESC;
```


## Possible Future Improvements

- Automated scheduled ingestion
- Slack / email alert integration
- Web dashboard for monitoring checks
- Historical tracking of check failures