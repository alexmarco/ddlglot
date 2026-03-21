API Reference
=============

Core Functions
-------------

create()
~~~~~~~~

.. code-block:: python

    from ddlglot import create

    builder = create(kind: str) -> CreateBuilder

Create a new DDL builder.

**Parameters:**

- ``kind`` (str): DDL kind ("TABLE", "VIEW", etc.)

**Returns:**

- CreateBuilder instance

CreateBuilder
~~~~~~~~~~~~~

.. code-block:: python

    from ddlglot import CreateBuilder

The main builder class. Use the ``create()`` factory function instead of instantiating directly.

Exceptions
----------

DDLGlotError
~~~~~~~~~~~~

Base exception for all ddlglot errors.

ASTBuildError
~~~~~~~~~~~~~

Raised when AST construction fails (e.g., missing table name).

SchemaValidationError
~~~~~~~~~~~~~~~~~~~~~

Raised when schema definition is invalid.

ValidationError
~~~~~~~~~~~~~~

Base class for validation errors.
