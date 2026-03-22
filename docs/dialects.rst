Dialects Reference
=================

SQLGlot translates the generic AST to dialect-specific SQL. Below are the
translation rules and feature support for each dialect.

Type Translation Tables
-----------------------

Numeric Types
~~~~~~~~~~~~~

+---------------------+----------+---------+----------+---------+----------+--------+
| Generic             | Postgres | SQLite  | BigQuery | Spark   | DuckDB   | MySQL   |
+=====================+==========+=========+==========+=========+==========+========+
| INT                 | INT      | INTEGER | INT64    | INT     | BIGINT   | INT    |
+---------------------+----------+---------+----------+---------+----------+--------+
| BIGINT              | BIGINT   | INTEGER | INT64    | BIGINT  | BIGINT   | BIGINT |
+---------------------+----------+---------+----------+---------+----------+--------+
| SMALLINT            | SMALLINT | INTEGER | INT64    | SMALLINT| SMALLINT | SMALLINT|
+---------------------+----------+---------+----------+---------+----------+--------+
| TINYINT             | SMALLINT | INTEGER | INT64    | TINYINT | TINYINT  | TINYINT|
+---------------------+----------+---------+----------+---------+----------+--------+
| FLOAT               | REAL     | REAL    | FLOAT64  | FLOAT   | DOUBLE   | DOUBLE |
+---------------------+----------+---------+----------+---------+----------+--------+
| DOUBLE              | DOUBLE   | REAL    | FLOAT64  | DOUBLE  | DOUBLE   | DOUBLE |
+---------------------+----------+---------+----------+---------+----------+--------+
| DECIMAL(p,s)        | DECIMAL  | TEXT    | NUMERIC  | DECIMAL | DECIMAL  | DECIMAL|
+---------------------+----------+---------+----------+---------+----------+--------+

String Types
~~~~~~~~~~~~

+---------------------+----------+---------+----------+---------+----------+--------+
| Generic             | Postgres | SQLite  | BigQuery | Spark   | DuckDB   | MySQL   |
+=====================+==========+=========+==========+=========+==========+========+
| VARCHAR(n)          | VARCHAR  | TEXT    | STRING   | VARCHAR | VARCHAR  | VARCHAR |
+---------------------+----------+---------+----------+---------+----------+--------+
| CHAR(n)             | CHAR     | TEXT    | STRING   | STRING  | VARCHAR  | CHAR   |
+---------------------+----------+---------+----------+---------+----------+--------+
| TEXT                | TEXT     | TEXT    | STRING   | STRING  | VARCHAR  | TEXT   |
+---------------------+----------+---------+----------+---------+----------+--------+

.. warning::

   SQLite ignores length specifiers on VARCHAR and CHAR. ``VARCHAR(100)`` is
   stored as ``TEXT`` — the number in parentheses has no effect. SQLite uses
   type affinity, not strict typing.

Temporal Types
~~~~~~~~~~~~~~

+---------------------+----------+---------+----------+---------+----------+--------+
| Generic             | Postgres | SQLite  | BigQuery | Spark   | DuckDB   | MySQL   |
+=====================+==========+=========+==========+=========+==========+========+
| DATE                | DATE     | TEXT    | DATE     | DATE    | DATE     | DATE    |
+---------------------+----------+---------+----------+---------+----------+--------+
| TIMESTAMP           | TIMESTAMP| TEXT    | TIMESTAMP| TIMESTAMP| TIMESTAMP| TIMESTAMP|
+---------------------+----------+---------+----------+---------+----------+--------+
| DATETIME            | TIMESTAMP| TEXT    | DATETIME | TIMESTAMP| TIMESTAMP| DATETIME|
+---------------------+----------+---------+----------+---------+----------+--------+
| TIME                | TIME     | TEXT    | TIME     | TIME    | TIME     | TIME    |
+---------------------+----------+---------+----------+---------+----------+--------+

Boolean Types
~~~~~~~~~~~~~

+---------------------+----------+---------+----------+---------+----------+--------+
| Generic             | Postgres | SQLite  | BigQuery | Spark   | DuckDB   | MySQL   |
+=====================+==========+=========+==========+=========+==========+========+
| BOOLEAN             | BOOLEAN  | INTEGER | BOOL     | BOOLEAN | BOOLEAN  | TINYINT |
+---------------------+----------+---------+----------+---------+----------+--------+

Dialect Feature Matrix
----------------------

+---------------------+--------+---------+---------+---------+---------+--------+
| Feature             | Postgres| SQLite  | BigQuery| Spark   | DuckDB  | Hive   |
+=====================+========+=========+=========+=========+=========+========+
| IF NOT EXISTS       | X      | X       | X       | X       | X       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| TEMPORARY           | X      | X       | -       | X       | X       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| Table comment       | X      | -       | X       | X       | X       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| Column comment      | X      | -       | X       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| USING format        | -      | -       | -       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| Delta format        | -      | -       | -       | X       | -       | -      |
+---------------------+--------+---------+---------+---------+---------+--------+
| PARTITIONED BY      | -      | -       | X       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| LOCATION            | -      | -       | -       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| STORED AS           | -      | -       | -       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| ROW FORMAT          | -      | -       | -       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| TBLPROPERTIES       | -      | -       | -       | X       | -       | X      |
+---------------------+--------+---------+---------+---------+---------+--------+
| Primary key         | X      | X*      | -       | -       | X       | -      |
+---------------------+--------+---------+---------+---------+---------+--------+
| Unique constraint   | X      | X*      | -       | -       | X       | -      |
+---------------------+--------+---------+---------+---------+---------+--------+

- ``X`` = Supported
- ``-`` = Not applicable / not supported by the dialect
- ``X*`` = SQLite supports PRIMARY KEY and UNIQUE but they are not enforced
  during inserts

.. note::

   Spark also supports Delta Lake format via ``.using("delta")``.

Known Limitations
-----------------

SQLite
~~~~~~

- VARCHAR and CHAR length specifiers are ignored — all are stored as ``TEXT``
- BOOLEAN is translated to ``INTEGER``
- BOOLEAN default values are translated to ``0``/``1``
- Foreign keys are not enforced by default (requires ``PRAGMA foreign_keys = ON``)
- DATE/TIMESTAMP are stored as ``TEXT``

BigQuery
~~~~~~~~

- No PRIMARY KEY or UNIQUE table-level constraints in standard SQL
- Partitioned tables must use ``PARTITION BY <column>`` — column lists not supported
- Fully qualified names use dot notation: ``project.dataset.table``

Hive
~~~~

- No ``DEFAULT`` column constraints — use ``TBLPROPERTIES`` or ``ROW FORMAT``
  for default-like behavior via SerDe options
- ``.partitioned_by()`` and ``.columns()`` are independent — ensure partition
  columns are also listed in ``.columns()``

Spark
~~~~~

- ``PARTITIONED BY`` columns must be listed in the main column list
- When using ``.partitioned_by()``, the partition columns must be included
  in the column definitions as well

DuckDB
~~~~~~

- ``TIMESTAMP`` is the preferred datetime type; ``DATETIME`` is an alias
- ``BOOLEAN`` defaults like ``DEFAULT TRUE`` are supported

MySQL
~~~~~~

- ``DOUBLE`` is used instead of ``FLOAT`` for double-precision
- BOOLEAN is translated to ``TINYINT``

Error Handling
--------------

If a dialect does not support a feature, SQLGlot raises an ``UnsupportedError``.
For example, using ``.partitioned_by()`` with ``dialect="postgres"`` will fail
because PostgreSQL does not support the ``PARTITIONED BY`` clause.

To avoid errors, check the feature matrix above or use dialect-specific
conditional logic in your application.
