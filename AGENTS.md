# AGENTS.md - Developer Guide for ddlglot

## Overview

`ddlglot` is a Python library that provides a fluent builder API for generating DDL (Data Definition Language) statements using SQLGlot's AST. It supports multiple SQL dialects (PostgreSQL, SQLite, DuckDB, Spark/Delta Lake, etc.).

---

## 1. Commands

### Build & Install

```bash
# Install the package in editable mode
uv pip install -e .

# Build the package
hatch build
```

### Run Tests

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_core.py

# Run a single test function
pytest tests/test_core.py::test_create_table_basic

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=ddlglot --cov-report=term-missing
```

### Linting & Type Checking

```bash
# Run ruff (linter + formatter)
ruff check . --fix
ruff format .

# Run mypy (type checking - errors stop, warnings don't)
mypy src
```

---

## 2. Code Style Guidelines

### General

- **Language**: English for all code, comments, and documentation
- **Python version**: 3.13+
- **Build system**: hatchling (via `pyproject.toml`)

### Imports

```python
# Standard library first
from __future__ import annotations
from typing import Any

# Third-party packages
from sqlglot import expressions as exp

# Local modules
from ddlglot.builder import CreateBuilder, create
```

- Use `from __future__ import annotations` for forward references
- Always use explicit relative imports for package modules (`from .exceptions import ...`)
- Alphabetize imports within each group

### Formatting

- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, except when string contains double quotes
- **Trailing commas**: Use in multi-line expressions

```python
# Good
def example(
    arg1: str,
    arg2: int,
) -> dict[str, Any]:
    return {"arg1": arg1, "arg2": arg2}

# Bad
def example(arg1: str, arg2: int) -> dict[str, Any]:
    return {"arg1": arg1, "arg2": arg2}
```

### Types

- Use explicit type hints for all function parameters and return types
- Use `Optional[X]` instead of `X | None` for Python < 3.10 compatibility
- Use `Dict`, `Tuple`, `List`, ... instead `list`, `dict`, `tuple`, ... for python < 3.10 compatibility
- Prefer type aliases for complex types:

```python
Lit = Union[str, int, float, bool]
```

### Naming Conventions

| Element         | Convention            | Example                |
| --------------- | --------------------- | ---------------------- |
| Modules         | snake_case            | `builder.py`           |
| Classes         | PascalCase            | `CreateBuilder`        |
| Functions       | snake_case            | `create()`, `to_ast()` |
| Variables       | snake_case            | `self._table`          |
| Constants       | UPPER_SNAKE_CASE      | `DELTA_FORMAT`         |
| Private members | `_leading_underscore` | `self._columns`        |

### Classes & Methods

- Use fluent builder pattern: methods return `self` for chaining
- Use `__init__` for object construction
- Use `@staticmethod` for pure utility functions

```python
class CreateBuilder:
    def name(self, table: str) -> CreateBuilder:
        """Set the table/view name."""
        self._table = table
        return self
```

### Error Handling

- Use explicit exceptions with descriptive messages from `exceptions.py`
- Raise `ASTBuildError` for AST construction failures (e.g., missing table name)
- Use validation exceptions from `exceptions.py` for other errors

```python
def to_ast(self) -> exp.Create:
    """Build and return SQLGlot exp.Create AST."""
    if not self._table:
        raise ASTBuildError("Missing .name(<table>)")
```

### Docstrings

- Use Numpy-style docstrings for public APIs:

```python
def sql(
    self,
    dialect: str | None = None,
    pretty: bool = False,
    indent: int = 2,
    pad: int = 2,
    max_text_width: int = 80,
) -> str:
    """Generate SQL DDL string.

    Args:
        dialect: SQL dialect (e.g., "postgres", "spark").
        pretty: Enable pretty formatting.
        indent: Number of spaces per indentation level (default: 2).
        pad: Number of spaces for alignment padding (default: 2).
        max_text_width: Maximum line width before wrapping (default: 80).

    Returns:
        The generated SQL string.
    """
    return self.to_ast().sql(
        dialect=dialect,
        pretty=pretty,
        indent=indent,
        pad=pad,
        max_text_width=max_text_width,
    )
```

- **Do not add comments** unless explicitly requested

### Testing

- Place tests in `tests/` directory
- Use `pytest` as test runner
- Follow naming: `test_<module>.py`
- One test class per module, test functions prefixed with `test_`
- **Always compare full SQL output**, never substring checks

```python
# tests/test_core.py
class TestCreateTable:
    """Tests for CREATE TABLE statements."""

    def test_create_table_basic_postgres(self) -> None:
        """Test basic CREATE TABLE with Postgres dialect."""
        sql = (
            create("table")
            .name("public.users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres")
        )
        expected = "CREATE TABLE public.users (id INT NOT NULL, name VARCHAR(100))"
        assert sql == expected
```

---

## 3. Project Structure

```txt
ddlglot/
├── pyproject.toml
├── src/ddlglot/
│   ├── __init__.py          # Public API exports
│   ├── builder.py           # Core CreateBuilder + create()
│   ├── exceptions.py        # Custom exception hierarchy
│   └── properties.py        # Property helpers
└── tests/
    ├── test_core.py         # Core builder tests
    └── test_validation.py   # Validation tests
```

---

## 4. Key Libraries

- **sqlglot**: AST and SQL generation (installed as dependency)
- **pytest**: Testing framework
- **ruff**: Linting and formatting (with comprehensive rule sets)
- **mypy**: Static type checking

---

## 5. Dialect-Specific Notes

- The builder is **dialect-agnostic** at the AST level
- Dialect-specific generation happens at `.sql(dialect=...)` call
- Supported dialects: `postgres`, `sqlite`, `duckdb`, `spark`, `bigquery`, `hive`, `databricks`, etc.
- SQLGlot's `Generator` handles dialect-specific syntax translation automatically

---

## 6. Common Tasks

### Adding New DDL Properties

1. Add method to `CreateBuilder` (e.g., `.tblproperties()`)
2. Implement property building in `_build_properties()`
3. Use appropriate SQLGlot expression type (e.g., `exp.Properties`, `exp.Property`)
4. Add tests with full SQL comparison

### Adding New Exceptions

1. Add to `src/ddlglot/exceptions.py`
2. Extend appropriate base class (`DDLGlotError`, `ValidationError`, etc.)
3. Include descriptive message and relevant context
4. Add tests for error cases

### Adding New Tests

1. Follow the existing test structure in `tests/test_core.py`
2. Always use full SQL comparison: `assert sql == expected`
3. Include docstrings describing what is tested
4. Test multiple dialects when relevant

---

## 7. Git Workflow

- Use Conventional Commits: `feat(scope): description`, `fix(scope): description`
- Run `pytest` and `ruff check .` before committing
- Never commit directly to `main`; use feature branches
