# ddlglot

**Fluent DDL builder using SQLGlot's AST**

[![CI](https://github.com/alexmarco/ddlglot/actions/workflows/ci.yml/badge.svg)](https://github.com/alexmarco/ddlglot/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ddlglot.svg)](https://pypi.org/project/ddlglot/)
[![Python versions](https://img.shields.io/pypi/pyversions/ddlglot.svg)](https://pypi.org/project/ddlglot/)
[![Docs](https://img.shields.io/badge/docs-github.io-blue)](https://alexmarco.github.io/ddlglot/)

## Features

- **Fluent API**: Chain method calls to build DDL statements
- **Multi-dialect**: PostgreSQL, SQLite, DuckDB, Spark, BigQuery, Hive, and more
- **Type Safe**: Full type hints and validation
- **DDL Inspection**: Inspect table metadata without parsing SQL strings
- **SQLGlot Powered**: Leverages SQLGlot's AST for SQL generation

## Installation

```bash
pip install ddlglot
```

## Quick Start

```python
from ddlglot import create

sql = (
    create("table")
    .name("public.users")
    .column("id", "INT", not_null=True, pk=True)
    .column("name", "VARCHAR(100)")
    .column("active", "BOOLEAN", default=True)
    .sql(dialect="postgres")
)
# CREATE TABLE public.users (
#   id INT NOT NULL PRIMARY KEY,
#   name VARCHAR(100),
#   active BOOLEAN DEFAULT TRUE
# )
```

## Dialect Examples

The same builder generates correct SQL for any dialect:

```python
from ddlglot import create

ddl = (
    create("table")
    .name("events")
    .column("id", "INT")
    .column("event_date", "DATE")
    .column("value", "DOUBLE")
)

print(ddl.sql(dialect="postgres"))
# CREATE TABLE events (id INT, event_date DATE, value DOUBLE PRECISION)

print(ddl.sql(dialect="spark"))
# CREATE TABLE events (id INT, event_date DATE, value DOUBLE)

print(ddl.sql(dialect="bigquery"))
# CREATE TABLE events (id INT64, event_date DATE, value FLOAT64)
```

## Advanced Features

### Partitioning and Location (Spark/Delta Lake)

```python
from ddlglot import create

sql = (
    create("table")
    .name("events")
    .using("delta")
    .column("id", "INT")
    .column("event_date", "DATE")
    .partitioned_by("event_date")
    .location("s3://warehouse/events")
    .tblproperties({"delta.autoOptimize.optimizeWrite": True})
    .sql(dialect="spark")
)
```

### DDL Inspection

Inspect the table definition as structured data — no string parsing needed:

```python
from ddlglot import create

ddl = (
    create("table")
    .name("users")
    .column("id", "INT", not_null=True, pk=True)
    .column("name", "VARCHAR(100)")
    .column("score", "INT", default=0)
    .unique_key("name")
    .build()
)

print(ddl.table_name)      # "users"
print(ddl.primary_keys)    # ("id",)
print(ddl.unique_keys)     # (("name",),)
print(ddl.columns[0].pk)   # True
print(ddl.columns[2].default)  # 0
```

### CTAS (CREATE TABLE AS SELECT)

```python
from sqlglot import select
from ddlglot import create

sql = (
    create("table")
    .name("user_summary")
    .column("user_id", "INT")
    .column("total_orders", "INT")
    .as_select(select("user_id", "COUNT(1).AS_(total_orders)").from_("orders"))
    .sql(dialect="postgres")
)
```

## Development

```bash
# Install with all dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -q

# Lint and format
uv run ruff check src tests
uv run ruff format src tests

# Type check
uv run mypy src

# Build docs
uv run sphinx-build -b html docs docs/_build/html
```

## Documentation

Full documentation is available at: https://alexmarco.github.io/ddlglot/

## License

MIT License
