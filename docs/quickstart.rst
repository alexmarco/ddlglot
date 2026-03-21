Quick Start
===========

Installation
-------------

.. code-block:: bash

    pip install ddlglot

Basic Usage
-----------

Creating Tables
~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create

    # Simple table for PostgreSQL
    sql = (
        create("table")
        .name("users")
        .column("id", "INT")
        .column("name", "VARCHAR(100)")
        .sql(dialect="postgres")
    )

Output:

.. code-block:: sql

    CREATE TABLE users (id INT, name VARCHAR(100))

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

Output:

.. code-block:: sql

    CREATE TABLE orders (id INT NOT NULL, total DECIMAL(10, 2) DEFAULT 0, active BOOLEAN DEFAULT TRUE)

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

Output:

.. code-block:: sql

    CREATE TABLE order_items (order_id INT, product_id INT, PRIMARY KEY (order_id, product_id))

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
        .sql(dialect="postgres", pretty=True)
    )

Output:

.. code-block:: sql

    CREATE VIEW active_users AS
    SELECT
      *
    FROM users
    WHERE active = TRUE

Dialect-Specific Features
------------------------

Spark+Delta
~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create

    sql = (
        create("table")
        .name("events")
        .column("id", "INT")
        .column("event_date", "DATE")
        .using("delta")
        .partitioned_by("event_date")
        .location("s3://warehouse/events/")
        .sql(dialect="spark", pretty=True)
    )

Output:

.. code-block:: sql

    CREATE TABLE events (
      id INT,
      event_date DATE
    )
    USING DELTA
    PARTITIONED BY (event_date)
    LOCATION 's3://warehouse/events/'

Hive
~~~~

.. code-block:: python

    from ddlglot import create

    sql = (
        create("table")
        .name("events")
        .column("id", "INT")
        .stored_as("PARQUET")
        .row_format("DELIMITED")
        .location("/warehouse/events/")
        .sql(dialect="hive", pretty=True)
    )

Output:

.. code-block:: sql

    CREATE TABLE events (
      id INT
    )
    ROW FORMAT DELIMITED
    STORED AS PARQUET
    LOCATION '/warehouse/events/'

BigQuery
~~~~~~~~

BigQuery uses INT64 and STRING instead of INT and VARCHAR:

.. code-block:: python

    from ddlglot import create

    sql = (
        create("table")
        .name("project.dataset.events")
        .column("id", "INT")
        .column("name", "VARCHAR(100)")  # VARCHAR is translated to STRING
        .partitioned_by("event_date")
        .sql(dialect="bigquery", pretty=True)
    )

Output:

.. code-block:: sql

    CREATE TABLE project.dataset.events (
      id INT64,
      name STRING
    )
    PARTITION BY event_date

SQLite
~~~~~~

SQLite uses INTEGER instead of INT:

.. code-block:: python

    from ddlglot import create

    sql = create("table").name("users").column("id", "INT").sql(dialect="sqlite")

Output:

.. code-block:: sql

    CREATE TABLE users (id INTEGER)

Pretty Printing
--------------

.. code-block:: python

    from ddlglot import create

    sql = (
        create("table")
        .name("users")
        .column("id", "INT")
        .column("name", "VARCHAR(100)")
        .column("email", "VARCHAR(255)")
        .sql(dialect="postgres", pretty=True, max_text_width=50)
    )

Output:

.. code-block:: sql

    CREATE TABLE users (
      id INT,
      name VARCHAR(100),
      email VARCHAR(255)
    )
