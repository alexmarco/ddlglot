Core Builder
============

CreateBuilder
-------------

The core builder provides a fluent API for generating DDL statements.

Factory Function
~~~~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import create

    builder = create("table")  # or create("view")

Methods
~~~~~~~

name()
^^^^^^

Set the table or view name.

.. code-block:: python

    .name("schema.table_name")

column()
^^^^^^^^

Add a column definition with optional constraints.

.. code-block:: python

    .column("name", "VARCHAR(100)")
    .column("id", "INT", pk=True, not_null=True)
    .column("price", "DECIMAL(10,2)", default=0)

**Parameters:**

- ``name`` (str): Column name
- ``dtype`` (str): Data type
- ``not_null`` (bool, optional): Add NOT NULL constraint
- ``pk`` (bool, optional): Add PRIMARY KEY constraint
- ``unique`` (bool, optional): Add UNIQUE constraint
- ``default`` (optional): Default value

columns()
^^^^^^^^^

Add multiple columns at once.

.. code-block:: python

    .columns(("id", "INT"), ("name", "VARCHAR(100)"))

primary_key()
^^^^^^^^^^^^^

Add a table-level PRIMARY KEY constraint.

.. code-block:: python

    .primary_key("col1", "col2")

unique_key()
^^^^^^^^^^^^

Add a table-level UNIQUE constraint.

.. code-block:: python

    .unique_key("email")

if_not_exists()
^^^^^^^^^^^^^^^

Add IF NOT EXISTS clause.

.. code-block:: python

    .if_not_exists()

temporary()
^^^^^^^^^^^

Mark as TEMPORARY table.

.. code-block:: python

    .temporary()

comment()
^^^^^^^^^

Add a table comment.

.. code-block:: python

    .comment("User information table")

as_select()
^^^^^^^^^^^

Set CTAS expression or view definition.

.. code-block:: python

    .as_select(exp.select("*").from_("other_table"))

using()
^^^^^^^

Set USING format (for file-based tables).

.. code-block:: python

    .using("delta")

partitioned_by()
^^^^^^^^^^^^^^^^

Add PARTITIONED BY clause.

.. code-block:: python

    .partitioned_by("date_column")

location()
^^^^^^^^^^

Set LOCATION path.

.. code-block:: python

    .location("s3://bucket/path/")

tblproperties()
^^^^^^^^^^^^^^^

Add TBLPROPERTIES.

.. code-block:: python

    .tblproperties({"key": "value"})

Output Methods
~~~~~~~~~~~~~~

to_ast()
^^^^^^^^

Return SQLGlot AST expression.

.. code-block:: python

    ast = builder.to_ast()

sql()
^^^^^

Generate SQL string.

.. code-block:: python

    sql = builder.sql(dialect="postgres")
    sql_pretty = builder.sql(dialect="postgres", pretty=True, indent=4)

**Parameters:**

- ``dialect`` (str, optional): SQL dialect (default: None)
- ``pretty`` (bool, optional): Enable pretty printing (default: False)
- ``indent`` (int, optional): Spaces per indent level (default: 2)
- ``pad`` (int, optional): Alignment padding (default: 2)
- ``max_text_width`` (int, optional): Max line width before wrapping (default: 80)
