# AGENTS.md - Developer Guide for ddlglot

## Overview

`ddlglot` is a Python library that provides a fluent builder API for generating DDL (Data Definition Language) statements using SQLGlot's AST. It supports multiple SQL dialects (PostgreSQL, SQLite, DuckDB, Spark/Delta Lake, etc.).

---

## 1. Commands

### Build & Install

```bash
# Install the package in editable mode
pip install -e .

# Build the package
hatch build
```

### Testing

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
ruff check .
ruff format .

# Run mypy (type checking)
mypy src/ddlglot
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
from typing import Any, Dict, List, Optional, Tuple, Union

# Third-party packages
from sqlglot import expressions as exp

# Local modules
from ddlglot.builder import CreateBuilder, create
from ddlglot.variants.spark_delta import create_spark_delta
```

- Use `from __future__ import annotations` for forward references
- Always use explicit relative imports for package modules (`from ..builder import ...`)
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
) -> Dict[str, Any]:
    return {"arg1": arg1, "arg2": arg2}

# Bad
def example(arg1: str, arg2: int) -> Dict[str, Any]:
    return {"arg1": arg1, "arg2": arg2}
```

### Types

- Use explicit type hints for all function parameters and return types
- Use `Optional[X]` instead of `X | None` for Python < 3.10 compatibility
- Prefer type aliases for complex types:

```python
Lit = Union[str, int, float, bool]
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `spark_delta.py` |
| Classes | PascalCase | `CreateBuilder` |
| Functions | snake_case | `create()`, `to_ast()` |
| Variables | snake_case | `self._table` |
| Constants | UPPER_SNAKE_CASE | `DELTA_FORMAT` |
| Private members | `_leading_underscore` | `self._columns` |

### Classes & Methods

- Use fluent builder pattern: methods return `self` for chaining
- Use `__init__` for object construction
- Use `@staticmethod` for pure utility functions

```python
class CreateBuilder:
    def name(self, table: str) -> "CreateBuilder":
        self._table = table
        return self
```

### Error Handling

- Use explicit exceptions with descriptive messages
- Raise `ValueError` for invalid arguments

```python
def to_ast(self) -> exp.Create:
    if not self._table:
        raise ValueError("Falta .name(<tabla>)")
```

### Docstrings

- Use Google-style docstrings for public APIs:

```python
def sql(self, dialect: Optional[str] = None, pretty: bool = False) -> str:
    """Generate SQL DDL string.
    
    Args:
        dialect: SQL dialect (e.g., "postgres", "spark").
        pretty: Enable pretty formatting.
    
    Returns:
        The generated SQL string.
    """
    return self.to_ast().sql(dialect=dialect, pretty=pretty)
```

- **Do not add comments** unless explicitly requested

### Testing

- Place tests in `tests/` directory
- Use `pytest` as test runner
- Follow naming: `test_<module>.py`
- One test class per module, test functions prefixed with `test_`

```python
# tests/test_core.py
import pytest
from ddlglot import create

def test_create_table_basic():
    sql = (
        create("table")
        .name("public.users")
        .column("id", "INT", not_null=True)
        .sql(dialect="postgres")
    )
    assert "CREATE TABLE" in sql
```

---

## 3. Project Structure

```
ddlglot/
├── pyproject.toml
├── src/ddlglot/
│   ├── __init__.py
│   ├── builder.py          # Core fluent builder
│   ├── properties.py       # Property helpers
│   └── variants/
│       ├── __init__.py
│       └── spark_delta.py  # Spark + Delta preset
└── tests/
    ├── test_core.py
    └── test_spark_delta.py
```

---

## 4. Key Libraries

- **sqlglot**: AST and SQL generation (installed as dependency)
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **mypy**: Static type checking

---

## 5. Dialect-Specific Notes

- The builder is **dialect-agnostic** at the AST level
- Dialect-specific generation happens at `.sql(dialect=...)` call
- Supported dialects: `postgres`, `sqlite`, `duckdb`, `spark`, `databricks`, etc.
- SQLGlot's `Generator` handles dialect-specific syntax (e.g., `PARTITIONED BY` placement)

---

## 6. Common Tasks

### Adding a New Dialect Preset

1. Create `src/ddlglot/variants/<dialect>.py`
2. Extend `CreateBuilder` following the pattern in `spark_delta.py`
3. Export factory function `<dialect>_builder()`
4. Add tests in `tests/test_<dialect>.py`

### Adding New DDL Properties

1. Add method to `CreateBuilder` (e.g., `.tblproperties()`)
2. Implement property building in `_build_properties()`
3. Use appropriate SQLGlot expression type (e.g., `exp.Properties`, `exp.Property`)
4. Add tests covering the new property

---

## 7. Git Workflow

- Use Conventional Commits: `feat(scope): description`, `fix(scope): description`
- Run `pytest` and `ruff check .` before committing
- Never commit directly to `main`; use feature branches
