BigQuery
========

Google BigQuery tables with partitioning and clustering.

Usage
-----

.. code-block:: python

    from ddlglot import create_bigquery

    builder = create_bigquery()

Methods
-------

BigQuery-Specific Methods
~~~~~~~~~~~~~~~~~~~~~~~~~

partitioned_by()
^^^^^^^^^^^^^^^^

Set partition column.

.. code-block:: python

    .partitioned_by("event_date")

cluster_by()
^^^^^^^^^^^^

Add clustering columns.

.. code-block:: python

    .cluster_by("user_id", "region")

Validation
----------

- ``cluster_by()`` requires ``partitioned_by()`` to be set

Example
-------

.. code-block:: python

    from ddlglot import create_bigquery

    sql = (
        create_bigquery()
        .name("project.dataset.events")
        .column("id", "INT64")
        .column("event_date", "DATE")
        .column("user_id", "INT64")
        .partitioned_by("event_date")
        .cluster_by("user_id")
        .sql()
    )
