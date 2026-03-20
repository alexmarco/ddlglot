# ddlglot

**Fluent DDL builder API using SQLGlot's AST**

[![CI](https://github.com/alexmarco/ddlglot/actions/workflows/ci.yml/badge.svg)](https://github.com/alexmarco/ddlglot/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ddlglot.svg)](https://pypi.org/project/ddlglot/)
[![Python versions](https://img.shields.io/pypi/pyversions/ddlglot.svg)](https://pypi.org/project/ddlglot/)

## Features

- **Fluent API**: Chain method calls to build DDL statements
- **Multiple Dialects**: Support for Spark, Delta Lake, Hive, PostgreSQL, DuckDB, BigQuery
- **Type Safe**: Full type hints and validation
- **SQLGlot Powered**: Leverage SQLGlot's AST for SQL generation

## Installation

```bash
pip install ddlglot
```

Or with uv:

```bash
uv add ddlglot
```

## Quick Start

```python
from ddlglot import create

# Create a table
sql = (
    create("table")
    .name("public.users")
    .column("id", "INT", not_null=True)
    .column("name", "VARCHAR(100)")
    .sql(dialect="postgres")
)
# CREATE TABLE public.users (id INT NOT NULL, name VARCHAR(100))
```

## Dialect Variants

### Spark+Delta

```python
from ddlglot import create_spark_delta

sql = (
    create_spark_delta()
    .name("default.events")
    .column("id", "INT")
    .partitioned_by("event_date")
    .enable_cdf(True)
    .sql()
)
```

### Hive

```python
from ddlglot import create_hive

sql = (
    create_hive()
    .name("default.events")
    .column("id", "INT")
    .stored_as("PARQUET")
    .sql()
)
```

### BigQuery

```python
from ddlglot import create_bigquery

sql = (
    create_bigquery()
    .name("project.dataset.events")
    .column("id", "INT64")
    .partitioned_by("event_date")
    .cluster_by("user_id")
    .sql()
)
```

## Validation

The library validates dialect-specific constraints:

```python
from ddlglot import create_duckdb
from ddlglot.exceptions import UnsupportedFeatureError

# DuckDB doesn't support partitioning
try:
    create_duckdb().name("test").partitioned_by("date").sql()
except UnsupportedFeatureError as e:
    print(f"Error: {e}")
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Lint
ruff check src tests

# Type check
mypy src
```

## License

MIT License
