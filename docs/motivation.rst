Motivation
==========

Why ddlglot exists and when to use it.

Origin
------

ddlglot was born from a practical problem in data pipelines built with `Ibis`_. While
Ibis excels at transforming and analyzing data across multiple backends, its DDL
(Data Definition Language) capabilities are limited.

When creating tables in a data warehouse, you often need features that go beyond
simple schema definition:

- Partition columns with specific storage layouts
- File formats and compression settings
- Location paths for external tables
- Table properties for optimization or data lake features
- Dialect-specific syntax for Spark, BigQuery, Hive, etc.

Ibis's ``create_table()`` requires data to insert and does not expose a complete
DDL API for these features. The common workaround is to write SQL as raw strings:

.. code-block:: python

    # Common workaround: raw SQL strings
    ddl = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            id INT PRIMARY KEY,
            name VARCHAR({length}),
            created_at TIMESTAMP
        ) USING DELTA
        PARTITIONED BY (created_at)
        LOCATION '{location}'
    """
    con.raw_sql(ddl)

This approach works, but introduces several problems.

The Problem with Raw SQL
------------------------

Writing DDL as raw strings has significant drawbacks:

**Security risk**
    Interpolating values into SQL strings can lead to SQL injection vulnerabilities
    if not handled carefully. Even with careful escaping, it is easy to make mistakes.

**No validation**
    Syntax errors are only discovered at runtime, when the SQL is executed against
    the database. Typos and dialect-specific mistakes can cause pipelines to fail.

**No type checking**
    Column names, types, and constraints are just strings. There is no autocompletion,
    no IDE support, and no compile-time checking.

**Poor maintainability**
    As schemas evolve, raw SQL strings become scattered across the codebase.
    Refactoring is error-prone and tedious.

**Dialect lock-in**
    SQL that works for Spark may not work for BigQuery or PostgreSQL.
    Migrating to a different backend requires rewriting all DDL strings manually.

Why Not Use an ORM Instead?
---------------------------

Several ORM and migration tools exist for Python. Here is why they may not be
the right fit for data engineering use cases:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Tool
     - Limitation
   * - **SQLAlchemy / Alembic**
     - Designed for application models and incremental migrations.
       Auto-generated migrations require constant manual editing.
       Partitioned tables are problematic (see SQLAlchemy `#539`_, open since 2019).
       Conditional DDL per dialect is cumbersome.
   * - **Django ORM**
     - Only supports PostgreSQL, SQLite, and MySQL out of the box.
       No support for cloud-specific features like BigQuery partitioning
       or Spark table formats.
   * - **Ibis**
     - ``create_table()`` requires data or an expression to insert.
       Does not expose a complete DDL API.
       You still need ``raw_sql()`` for many use cases.
   * - **Raw SQL strings**
     - Security vulnerabilities from SQL injection.
       No validation, type checking, or IDE support.
       Difficult to migrate between dialects.

.. _`#539`: https://github.com/sqlalchemy/sqlalchemy/issues/539

ORMs are excellent for defining application models where Python classes map to
database tables. However, data engineering often requires schemas that do not map
directly to Python objects:

- Staging tables for ELT pipelines
- Aggregated tables with specific partitioning schemes
- External tables pointing to data lake storage
- Temporary tables for incremental processing

In these cases, you need full control over the DDL, and ORMs fall short.

When Not to Use ddlglot
-----------------------

ddlglot is not a replacement for ORM tools in application development. Do not
use ddlglot when:

- You are defining domain models that map to application entities
- Your team uses Django, SQLAlchemy, or similar for application data access
- You need database introspection to compare models against existing schemas

Use ddlglot when you need **complete control over DDL** for data engineering
use cases where ORMs do not provide the necessary features.

The Solution: ddlglot
----------------------

ddlglot provides a fluent, type-safe builder API for generating DDL statements.
It uses `SQLGlot`_ under the hood to translate the generic AST to dialect-specific
SQL, supporting Spark, BigQuery, Hive, PostgreSQL, DuckDB, SQLite, and more.

.. _`SQLGlot`: https://github.com/tobymao/sqlglot

.. code-block:: python

    from ddlglot import create

    ddl = (
        create("table")
        .if_not_exists()
        .name("analytics.events_enriched")
        .column("event_id", "BIGINT", pk=True, not_null=True)
        .column("user_id", "BIGINT", not_null=True)
        .column("event_type", "VARCHAR(50)")
        .column("created_at", "TIMESTAMP")
        .partitioned_by("event_year", "event_month")
        .location("s3://warehouse/analytics/events_enriched/")
        .using("delta")
        .tblproperties({
            "delta.autoOptimize.optimizeWrite": "true",
        })
        .sql(dialect="spark")
    )

Benefits
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Aspect
     - Raw SQL
     - ORM migrations
     - ddlglot
   * - Security
     - Injection risk
     - Safe
     - Safe (no interpolation)
   * - Validation
     - Runtime only
     - Limited
     - Type hints + tests
   * - Dialect support
     - Manual
     - Partial
     - Automatic via SQLGlot
   * - Advanced features
     - Depends on you
     - Basic
     - Complete (partitions, props, etc.)
   * - Testing
     - Difficult
     - Migration tests
     - Unit tests
   * - Maintainability
     - Hardcoded strings
     - Models + migrations
     - Fluent builder

Practical Example: Ibis + ddlglot for Spark
------------------------------------------

This example shows how ddlglot complements Ibis in a Spark data pipeline.
Ibis handles data transformation, while ddlglot defines the complete DDL for
the destination table with features that Ibis does not support.

.. code-block:: python

    import ibis
    import ddlglot

    # 1. Connect to Spark and load raw data
    con = ibis.spark.connect(...)
    raw = con.table("raw_events")

    # 2. Define transformations with Ibis
    enriched = (
        raw.select(
            raw.event_id,
            raw.user_id,
            raw.event_type,
            raw.payload,
            raw.created_at,
        )
        .filter(raw.event_type.isin(["purchase", "refund"]))
        .mutate(
            event_year=raw.created_at.year(),
            event_month=raw.created_at.month(),
        )
    )

    # 3. Define DDL with ddlglot
    # Features that Ibis does not support: partitioning, location, format,
    # table properties, etc.
    ddl = (
        ddlglot.create("table")
        .name("analytics.events_enriched")
        .column("event_id", "BIGINT", pk=True, not_null=True)
        .column("user_id", "BIGINT", not_null=True)
        .column("event_type", "VARCHAR(50)")
        .column("payload", "STRING")
        .column("created_at", "TIMESTAMP")
        .column("event_year", "INT")
        .column("event_month", "INT")
        .partitioned_by("event_year", "event_month")
        .location("s3://warehouse/analytics/events_enriched/")
        .using("delta")
        .tblproperties({
            "delta.autoOptimize.optimizeWrite": "true",
            "delta.enableChangeDataFeed": "true",
        })
        .sql(dialect="spark")
    )

    # 4. Execute DDL to create the table
    con.raw_sql(ddl)

    # 5. Insert transformed data with Ibis
    con.create_table("analytics.events_enriched", enriched)

This approach gives you the best of both worlds:

- **Ibis**: Expressive data transformation with a unified API across backends
- **ddlglot**: Complete DDL control with dialect-specific features and type safety

Comparison with Similar Tools
-----------------------------

Other Python tools exist for generating SQL. Here is how ddlglot compares:

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Tool
     - DDL focus
     - Multi-dialect
     - Fluent API
   * - **sqlglot** (raw)
     - Yes
     - Yes
     - No (imperative AST)
   * - **SQLAlchemy** (DDL)
     - Partial
     - Yes
     - Yes
   * - **ddlglot**
     - Yes
     - Yes
     - Yes

sqlglot is the engine behind ddlglot. While sqlglot provides powerful AST
manipulation, its API is imperative and requires understanding the internal
expression tree. ddlglot wraps sqlglot with a fluent builder interface that
makes common DDL patterns simple and readable.

What ddlglot Does NOT Do
-------------------------

ddlglot is a **DDL generator**, not an executor. It does not:

- Execute SQL against a database
- Manage database connections
- Handle migrations or schema evolution
- Provide database introspection

This is by design. Separation of concerns keeps ddlglot lightweight and
backend-agnostic. You can use ddlglot alongside any database client:

.. code-block:: python

    # Generate DDL
    ddl = create("table").name("t").column("id", "INT").sql(dialect="postgres")

    # Execute with your preferred client
    con.raw_sql(ddl)              # Ibis
    cursor.execute(ddl)            # DBAPI2 (psycopg2, sqlite3, etc.)
    engine.execute(text(ddl))     # SQLAlchemy
    !psql -c "$ddl"               # CLI tool

This flexibility means you can integrate ddlglot into existing workflows
without changing your database stack.

.. _`Ibis`: https://ibis-project.org/
