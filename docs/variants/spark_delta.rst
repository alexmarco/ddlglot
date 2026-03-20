Spark+Delta
===========

Delta Lake tables in Apache Spark.

Usage
-----

.. code-block:: python

    from ddlglot import create_spark_delta

    builder = create_spark_delta()

Methods
-------

Delta-Specific Methods
~~~~~~~~~~~~~~~~~~~~~~

enable_cdf()
^^^^^^^^^^^^^

Enable Change Data Feed.

.. code-block:: python

    .enable_cdf(True)

append_only()
^^^^^^^^^^^^^

Set appendOnly property.

.. code-block:: python

    .append_only(True)

log_retention()
^^^^^^^^^^^^^^^

Set logRetentionDuration.

.. code-block:: python

    .log_retention("30 days")

deleted_file_retention()
^^^^^^^^^^^^^^^^^^^^^^^^

Set deletedFileRetentionDuration.

.. code-block:: python

    .deleted_file_retention("7 days")

generated_column()
^^^^^^^^^^^^^^^^^^

Create a GENERATED ALWAYS AS column.

.. code-block:: python

    .generated_column("event_date", "DATE", "CAST(ts AS DATE)")

Validation
----------

The builder validates:

- ``partitioned_by()`` only accepts column names (not expressions)
- TBLPROPERTIES must use ``delta.`` prefix

Example
-------

.. code-block:: python

    from ddlglot import create_spark_delta

    sql = (
        create_spark_delta()
        .name("default.events")
        .column("id", "INT")
        .column("ts", "TIMESTAMP")
        .generated_column("event_date", "DATE", "CAST(ts AS DATE)")
        .partitioned_by("event_date")
        .enable_cdf(True)
        .sql()
    )
