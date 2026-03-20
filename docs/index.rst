ddlglot
=======

Welcome to ddlglot's documentation!

ddlglot is a Python library that provides a **fluent builder API** for generating DDL (Data Definition Language) statements using SQLGlot's AST.

Features
--------

- **Fluent API**: Chain method calls to build DDL statements
- **Multiple Dialects**: Support for Spark, Delta Lake, Hive, PostgreSQL, DuckDB, BigQuery
- **Type Safe**: Full type hints and validation
- **SQLGlot Powered**: Leverage SQLGlot's AST for SQL generation

Quick Start
-----------

.. code-block:: python

    from ddlglot import create

    # Create a table
    sql = (
        create("table")
        .name("public.users")
        .column("id", "INT", not_null=True)
        .column("name", "VARCHAR(100)")
        .sql(dialect="postgres")
    )
    print(sql)
    # CREATE TABLE public.users (id INT NOT NULL, name VARCHAR(100))

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   core_builder
   variants/index
   api_reference

Installation
------------

.. code-block:: bash

    pip install ddlglot

License
-------

MIT License
