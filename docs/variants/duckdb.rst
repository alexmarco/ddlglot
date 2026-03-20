DuckDB
======

DuckDB tables.

Usage
-----

.. code-block:: python

    from ddlglot import create_duckdb

    builder = create_duckdb()

Validation
----------

DuckDB does not support:

- ``partitioned_by()``
- ``location()``
- ``tblproperties()``

Attempting to use these will raise ``UnsupportedFeatureError``.

Example
-------

.. code-block:: python

    from ddlglot import create_duckdb

    sql = (
        create_duckdb()
        .name("users")
        .column("id", "INT", pk=True, not_null=True)
        .column("name", "VARCHAR")
        .sql()
    )
