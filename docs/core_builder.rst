Core Builder
==========

The CreateBuilder provides a fluent API for generating DDL statements. It works in
two stages:

1. **Build**: Chain methods to construct an abstract syntax tree (AST)
2. **Generate**: Call ``.sql()`` to translate the AST to dialect-specific SQL

.. code-block:: python

    # Stage 1: Build the AST
    builder = (
        create("table")
        .name("users")
        .column("id", "INT", pk=True, not_null=True)
        .column("name", "VARCHAR(100)")
    )

    # Stage 2: Generate SQL for a specific dialect
    sql = builder.sql(dialect="postgres")
    # Output: CREATE TABLE users (id INT NOT NULL, name VARCHAR(100))

Method Classification
--------------------

Methods are classified into two categories:

- **Universal**: Work with any dialect
- **Dialect-specific**: Only work with certain dialects; using them with
  unsupported dialects raises an ``UnsupportedError`` at generation time

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Method
     - Scope
     - Description
   * - ``.name()``
     - Universal
     - Set table/view name (required)
   * - ``.column()``
     - Universal
     - Add column with type and constraints
   * - ``.columns()``
     - Universal
     - Add multiple columns at once
   * - ``.primary_key()``
     - Universal
     - Add table-level PRIMARY KEY
   * - ``.unique_key()``
     - Universal
     - Add table-level UNIQUE constraint
   * - ``.if_not_exists()``
     - Universal
     - Add IF NOT EXISTS clause
   * - ``.temporary()``
     - Universal
     - Mark as TEMPORARY table
   * - ``.comment()``
     - Universal
     - Add table comment
   * - ``.as_select()``
     - Universal
     - Set CTAS or view definition (SQLGlot expression)
   * - ``.using()``
     - Dialect-specific
     - Set USING format (Delta, Parquet, etc.) — Spark, Hive only
   * - ``.partitioned_by()``
     - Dialect-specific
     - Add PARTITIONED BY — BigQuery, Spark, Hive only
   * - ``.location()``
     - Dialect-specific
     - Set LOCATION path — Spark, Hive only
   * - ``.stored_as()``
     - Dialect-specific
     - Set STORED AS (PARQUET, ORC, etc.) — Hive only
   * - ``.row_format()``
     - Dialect-specific
     - Set ROW FORMAT — Hive only
   * - ``.tblproperties()``
     - Dialect-specific
     - Add TBLPROPERTIES — Spark, Hive only

Methods Reference
-----------------

Universal Methods
~~~~~~~~~~~~~~~~~

These methods work with any SQL dialect and never raise UnsupportedError.

name()
^^^^^^

Set the table or view name. This is the only required method — without it,
``to_ast()`` raises ``ASTBuildError``.

.. code-block:: python

    .name("schema.table_name")       # Fully qualified
    .name("users")                   # Simple name

column()
^^^^^^^^

Add a column definition with optional constraints.

.. code-block:: python

    .column("name", "VARCHAR(100)")
    .column("id", "INT", pk=True, not_null=True)
    .column("price", "DECIMAL(10,2)", default=0)

**Parameters:**

- ``name`` (str): Column name
- ``dtype`` (str): Data type (any string — SQLGlot translates it per dialect)
- ``not_null`` (bool, optional): Add NOT NULL constraint
- ``pk`` (bool, optional): Add PRIMARY KEY constraint (sets not_null=True)
- ``unique`` (bool, optional): Add UNIQUE constraint
- ``default`` (optional): Default value (int, float, str, bool)

columns()
^^^^^^^^^

Add multiple columns at once. Equivalent to calling ``.column()`` multiple times.

.. code-block:: python

    .columns(
        ("id", "INT", "pk"),
        ("name", "VARCHAR(100)"),
        ("created_at", "TIMESTAMP"),
    )

primary_key()
^^^^^^^^^^^^^

Add a table-level PRIMARY KEY constraint. Differs from ``pk=True`` in ``.column()``
because it creates a standalone constraint, not a column-level one.

.. code-block:: python

    .primary_key("user_id", "tenant_id")  # Composite key

unique_key()
^^^^^^^^^^^^

Add a table-level UNIQUE constraint.

.. code-block:: python

    .unique_key("email")
    .unique_key("phone", "country_code")   # Composite unique

if_not_exists()
^^^^^^^^^^^^^^^

Add IF NOT EXISTS clause to the CREATE statement.

.. code-block:: python

    .if_not_exists()

temporary()
^^^^^^^^^^^

Mark the table as TEMPORARY. The generated SQL varies by dialect:

- Postgres: ``CREATE TEMPORARY TABLE``
- SQLite: ``CREATE TEMPORARY TABLE``
- Spark: ``CREATE TEMPORARY VIEW``
- Others: UnsupportedError

.. code-block:: python

    .temporary()

comment()
^^^^^^^^^

Add a table comment. Not supported by SQLite (silently ignored).

.. code-block:: python

    .comment("User authentication and profile data")

as_select()
^^^^^^^^^^^

Set the SELECT clause for CTAS (Create Table As Select) or view definitions.
Requires a SQLGlot expression, not a raw string.

.. code-block:: python

    from sqlglot import exp

    .as_select(exp.select("id", "name").from_("source_table"))

    # For views:
    .as_select(exp.select("*").from_("users").where("active = true"))

Dialect-Specific Methods
~~~~~~~~~~~~~~~~~~~~~~~

These methods only work with certain dialects. Using them with unsupported
dialects raises ``sqlglot.errors.UnsupportedError`` at generation time.

using()
^^^^^^^

Set the USING clause for file-based tables. Typically used with ``.partitioned_by()``
and ``.location()``.

**Supported dialects:** Spark, Hive

.. code-block:: python

    .using("delta")      # Delta Lake format
    .using("parquet")    # Parquet files
    .using("orc")        # ORC files

partitioned_by()
^^^^^^^^^^^^^^^^

Add PARTITIONED BY clause. In Spark/Hive, partition columns must also be defined
in ``.columns()``. In BigQuery, they are declared only here.

**Supported dialects:** BigQuery, Spark, Hive

.. code-block:: python

    # Spark/Hive: partition columns must be in .columns() too
    .column("event_date", "DATE")
    .partitioned_by("event_date")

    # BigQuery: only here (not in .columns())
    .partitioned_by("created_at")

location()
^^^^^^^^^^

Set the LOCATION path for external tables.

**Supported dialects:** Spark, Hive

.. code-block:: python

    .location("s3://warehouse/db/table/")
    .location("/mnt/data/table")

stored_as()
^^^^^^^^^^^

Set the STORED AS clause for Hive tables.

**Supported dialects:** Hive

.. code-block:: python

    .stored_as("PARQUET")
    .stored_as("ORC")
    .stored_as("TEXTFILE")

row_format()
^^^^^^^^^^^^

Set the ROW FORMAT clause for Hive tables.

**Supported dialects:** Hive

.. code-block:: python

    .row_format("DELIMITED")
    .row_format("SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'")

tblproperties()
^^^^^^^^^^^^^^^

Add TBLPROPERTIES key-value pairs. Used for table metadata, SerDe properties,
Delta Lake features, etc.

**Supported dialects:** Spark, Hive

.. code-block:: python

    .tblproperties({"delta.enableChangeDataFeed": "true"})
    .tblproperties({"format": "csv", "delimiter": ","})

Error Handling
~~~~~~~~~~~~~~

When using dialect-specific methods with unsupported dialects, SQLGlot raises
``UnsupportedError`` at generation time (when ``.sql()`` is called), not at
build time.

.. code-block:: python

    # This works fine — we only build the AST
    builder = (
        create("table")
        .name("events")
        .column("id", "INT")
        .partitioned_by("date")   # Works in memory
    )

    # This raises UnsupportedError
    sql = builder.sql(dialect="postgres")
    # UnsupportedError: Partitioning is not supported for postgres

**Best practices:**

- Use try/except around ``.sql()`` if targeting multiple dialects
- Check the method classification table before using dialect-specific features
- Refer to ``docs/dialects.rst`` for a complete feature matrix

Output Methods
~~~~~~~~~~~~~~

to_ast()
^^^^^^^^

Return the SQLGlot ``exp.Create`` AST. Use this for debugging or further
manipulation with SQLGlot APIs.

.. code-block:: python

    ast = builder.to_ast()
    # Returns: exp.Create instance

sql()
^^^^^

Generate the SQL string with optional dialect-specific translation.

.. code-block:: python

    sql = builder.sql()                         # Dialect-agnostic SQL
    sql = builder.sql(dialect="postgres")       # PostgreSQL-specific
    sql = builder.sql(dialect="spark", pretty=True)  # Pretty-printed

**Parameters:**

- ``dialect`` (str, optional): SQL dialect (default: None = generic)
- ``pretty`` (bool, optional): Enable pretty printing
- ``indent`` (int, optional): Spaces per indent level (default: 2)
- ``pad`` (int, optional): Alignment padding (default: 2)
- ``max_text_width`` (int, optional): Max line width before wrapping (default: 80)


DDL Inspection
~~~~~~~~~~~~~~

The ``.build()`` method returns an immutable ``DDL`` object that exposes all
defined properties for inspection. This is useful for generating metadata,
validating schemas, or integrating with other tools.

.. code-block:: python

    ddl = (
        create("table")
        .name("users")
        .column("id", "INT", pk=True, not_null=True)
        .column("name", "VARCHAR(100)")
        .column("created_at", "TIMESTAMP")
        .partitioned_by("created_at")
        .location("s3://warehouse/users/")
        .using("delta")
        .tblproperties({"delta.autoOptimize": "true"})
        .build()
    )

    # Inspect properties
    ddl.table_name       # → "users"
    ddl.kind             # → "TABLE"
    ddl.columns          # → (ColumnDef(...), ColumnDef(...), ...)
    ddl.primary_keys     # → ("id",)
    ddl.partition_cols   # → ("created_at",)
    ddl.location         # → "s3://warehouse/users/"
    ddl.file_format      # → "DELTA"
    ddl.tblproperties    # → {"delta.autoOptimize": "true"}

    # .sql() and .to_ast() are also available on DDL
    ddl.sql(dialect="spark")
    ddl.to_ast()

DDL object also exposes:

- ``if_not_exists``: Whether IF NOT EXISTS was set
- ``temporary``: Whether TEMPORARY was set
- ``comment``: Table comment
- ``unique_keys``: Tuple of unique constraint column tuples

.. code-block:: python

    ddl = (
        create("table")
        .name("users")
        .column("id", "INT")
        .column("email", "VARCHAR(100)")
        .unique_key("email")
        .build()
    )

    ddl.unique_keys  # → (("email",),)


Builder Inspection Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The builder itself also exposes inspection properties for convenience:

.. code-block:: python

    builder = (
        create("table")
        .name("users")
        .column("id", "INT", pk=True)
        .partitioned_by("id")
    )

    builder.table_name        # → "users"
    builder.columns_defs       # → [ColumnDef(...)]
    builder.primary_keys      # → ("id",)
    builder.partition_columns  # → ("id",)
    builder.unique_keys        # → ()


ColumnDef
^^^^^^^^^

The ``ColumnDef`` NamedTuple represents a column definition:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Attribute
     - Description
   * - ``name``
     - Column name (str)
   * - ``dtype``
     - Data type string (str)
   * - ``not_null``
     - Whether NOT NULL constraint is set (bool)
   * - ``pk``
     - Whether PRIMARY KEY constraint is set (bool)
   * - ``unique``
     - Whether UNIQUE constraint is set (bool)
   * - ``default``
     - Default value (Any)


Supported Dialects
------------------

ddlglot supports all SQLGlot dialects:

- ``postgres`` / ``postgresql``
- ``spark`` / ``sparksql``
- ``hive``
- ``bigquery``
- ``duckdb``
- ``sqlite``
- ``mysql``
- ``snowflake``
- ``redshift``
- And many more...

SQLGlot automatically handles dialect-specific syntax translation at generation
time.