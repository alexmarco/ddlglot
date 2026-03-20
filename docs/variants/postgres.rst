PostgreSQL
==========

PostgreSQL tables.

Usage
-----

.. code-block:: python

    from ddlglot import create_postgres

    builder = create_postgres()

Example
-------

.. code-block:: python

    from ddlglot import create_postgres

    sql = (
        create_postgres()
        .name("public.users")
        .column("id", "INT", pk=True, not_null=True)
        .column("name", "VARCHAR(100)")
        .column("created_at", "TIMESTAMP")
        .sql()
    )
