Hive
====

Apache Hive tables with SERDE and storage format support.

Usage
-----

.. code-block:: python

    from ddlglot import create_hive

    builder = create_hive()

Methods
-------

Hive-Specific Methods
~~~~~~~~~~~~~~~~~~~~~

stored_as()
^^^^^^^^^^^

Set STORED AS format.

.. code-block:: python

    .stored_as("PARQUET")
    .stored_as("ORC")
    .stored_as("AVRO")

row_format()
^^^^^^^^^^^^

Set ROW FORMAT.

.. code-block:: python

    .row_format("DELIMITED")
    .row_format("SERDE", serde="org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe")

stored_as_input_output()
^^^^^^^^^^^^^^^^^^^^^^^^

Set STORED AS INPUTFORMAT OUTPUTFORMAT.

.. code-block:: python

    .stored_as_input_output(
        "org.apache.hadoop.mapred.TextInputFormat",
        "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"
    )

Example
-------

.. code-block:: python

    from ddlglot import create_hive

    sql = (
        create_hive()
        .name("default.events")
        .column("id", "INT")
        .column("name", "STRING")
        .stored_as("PARQUET")
        .partitioned_by("dt")
        .location("/warehouse/events")
        .sql()
    )
