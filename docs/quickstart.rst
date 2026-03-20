Quick Start
===========

Installation
-------------

.. code-block:: bash

    pip install ddlglot

Basic Usage
-----------

Creating Tables
~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create

    # Simple table
    sql = (
        create("table")
        .name("users")
        .column("id", "INT")
        .column("name", "VARCHAR(100)")
        .sql(dialect="postgres")
    )

Using Variants
~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_spark_delta

    # Delta Lake table
    sql = (
        create_spark_delta()
        .name("default.events")
        .column("id", "INT")
        .partitioned_by("event_date")
        .enable_cdf(True)
        .sql()
    )

Column Definitions
-----------------

.. code-block:: python

    from ddlglot import create

    sql = (
        create("table")
        .name("orders")
        .column("id", "INT", pk=True, not_null=True)
        .column("total", "DECIMAL(10,2)", default=0)
        .column("active", "BOOLEAN", default=True)
        .sql(dialect="postgres")
    )

Table Constraints
----------------

.. code-block:: python

    from ddlglot import create

    sql = (
        create("table")
        .name("order_items")
        .column("order_id", "INT")
        .column("product_id", "INT")
        .primary_key("order_id", "product_id")
        .sql(dialect="postgres")
    )

Views and CTAS
--------------

.. code-block:: python

    from ddlglot import create
    from sqlglot import exp

    # Create view
    sql = (
        create("view")
        .name("active_users")
        .as_select(exp.select("*").from_("users").where("active = true"))
        .sql(dialect="postgres")
    )

    # Create table as select
    sql = (
        create("table")
        .name("user_summary")
        .as_select(
            exp.select("user_id", exp.Count("*").as_("count"))
            .from_("orders")
            .group_by("user_id")
        )
        .sql(dialect="postgres")
    )

Dialect-Specific Features
------------------------

Spark+Delta
~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_spark_delta

    sql = (
        create_spark_delta()
        .name("default.events")
        .column("id", "INT")
        .column("ts", "TIMESTAMP")
        .generated_column("event_date", "DATE", "CAST(ts AS DATE)")
        .enable_cdf(True)
        .append_only(False)
        .sql()
    )

Hive
~~~~

.. code-block:: python

    from ddlglot import create_hive

    sql = (
        create_hive()
        .name("default.events")
        .column("id", "INT")
        .stored_as("PARQUET")
        .row_format("SERDE", serde="org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe")
        .sql()
    )

BigQuery
~~~~~~~~

.. code-block:: python

    from ddlglot import create_bigquery

    sql = (
        create_bigquery()
        .name("project.dataset.events")
        .column("id", "INT64")
        .column("event_date", "DATE")
        .partitioned_by("event_date")
        .cluster_by("user_id")
        .sql()
    )

Validation
----------

The library validates dialect-specific constraints:

.. code-block:: python

    from ddlglot import create_duckdb
    from ddlglot.exceptions import UnsupportedFeatureError

    try:
        # This will raise an error - DuckDB doesn't support partitioning
        create_duckdb().name("test").partitioned_by("date").sql()
    except UnsupportedFeatureError as e:
        print(f"Error: {e}")
