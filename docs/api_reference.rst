API Reference
=============

Core Functions
--------------

create()
~~~~~~~~

.. code-block:: python

    from ddlglot import create

    builder = create(kind: str) -> CreateBuilder

Create a new DDL builder.

**Parameters:**

- ``kind`` (str): DDL kind ("TABLE", "VIEW", etc.)

Variants
--------

create_spark_delta()
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_spark_delta

    builder = create_spark_delta(kind: str = "TABLE") -> SparkDeltaBuilder

create_hive()
~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_hive

    builder = create_hive(kind: str = "TABLE") -> HiveBuilder

create_postgres()
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_postgres

    builder = create_postgres(kind: str = "TABLE") -> PostgresBuilder

create_duckdb()
~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_duckdb

    builder = create_duckdb(kind: str = "TABLE") -> DuckDBBuilder

create_bigquery()
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_bigquery

    builder = create_bigquery(kind: str = "TABLE") -> BigQueryBuilder

Registry
--------

register_variant()
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import register_variant

    @register_variant("my_variant")
    class MyBuilder(CreateBuilder):
        pass

get_variant()
~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import get_variant

    builder_cls = get_variant("spark_delta")

create_variant()
~~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create_variant

    builder = create_variant("spark_delta", kind="TABLE")

list_variants()
~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import list_variants

    variants = list_variants()  # ['spark_delta', 'hive', ...]

Exceptions
----------

DDLGlotError
~~~~~~~~~~~~

Base exception for all ddlglot errors.

ValidationError
~~~~~~~~~~~~~~~

Base class for validation errors.

DialectValidationError
~~~~~~~~~~~~~~~~~~~~~~

Raised when DDL is invalid for a specific dialect.

UnsupportedFeatureError
~~~~~~~~~~~~~~~~~~~~~~~

Raised when a feature is not supported by the dialect.

PartitionByExpressionError
~~~~~~~~~~~~~~~~~~~~~~~~~

Raised when PARTITIONED BY with expressions is used where not supported.

ASTBuildError
~~~~~~~~~~~~~

Raised when AST construction fails.
