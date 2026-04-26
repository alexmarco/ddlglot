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
- **Documentation format**: reStructuredText (``.rst``), **not** Markdown.
  Use RST directives for admonitions (``.. warning::``, ``.. note::``), not
  Markdown-style alerts (``> [!WARNING]``).

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
- Use parameterized tests with `DialectCase` for multi-dialect testing

```python
# tests/test_core.py
from typing import NamedTuple

class DialectCase(NamedTuple):
    """Test case with dialect and expected SQL."""
    dialect: str
    expected: str

class TestCreateTable:
    """Tests for CREATE TABLE statements."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE users (id INT NOT NULL, name VARCHAR(100))",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE users (id INT64 NOT NULL, name STRING(100))",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE users (id INTEGER NOT NULL, name TEXT(100))",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_basic_table(self, case: DialectCase) -> None:
        """Test basic CREATE TABLE across dialects."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected
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
- **sphinx**: Documentation generation (installed as dev dependency)

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

## 7. Documentation

### Build & Preview

```bash
# Build HTML docs locally
uv run sphinx-build -b html docs docs/_build/html

# Serve locally (optional)
cd docs/_build/html && python -m http.server 8080
```

### Syntax Rules

- **Format**: reStructuredText (``.rst``), **not** Markdown.
- **Admonitions**: Use RST directives (``.. warning::``, ``.. note::``), not
  Markdown-style alerts (``> [!WARNING]``).

  ```rst
  .. warning::
     Text here.

  .. note::
     Text here.
  ```

- **Tables**: Use the ``.. list-table::`` directive. It does not require manual
  character alignment and is the recommended approach by Sphinx.

  ````rst
  .. list-table::
     :header-rows: 1
     :widths: 15 15 15

     * - Column 1
       - Column 2
       - Column 3
     * - Data 1
       - Data 2
       - Data 3
  ````

  Avoid manual RST table syntax (``---`` or ``===``) because it requires
  exact character alignment across all rows, which is error-prone and hard to
  maintain.

### Deployment

- Docs are deployed automatically to GitHub Pages via
  ``.github/workflows/docs.yml`` on push to ``main``.
- The Sphinx ``html_theme`` is ``sphinx_book_theme``.

---

## 8. Git Workflow

.. warning::

   **NEVER push directly to main or develop.** All changes must go through pull requests.
   Even as repository owner, use feature branches to maintain a clean history
   and ensure CI validation.

### Branch Model (Simplified GitFlow)

| Branch | Purpose | Merge via |
|---------|---------|-----------|
| `main` | Production-ready code | PR only (from Release PR or hotfix) |
| `develop` | Integration branch for next release | PR only (from feature/*, fix/*, docs/*) |

### Working Branches

| Pattern | Base branch | Merges into | Purpose |
|---------|-------------|-------------|---------|
| `feature/<issue>-<slug>` | `develop` | `develop` | New features |
| `fix/<issue>-<slug>` | `develop` | `develop` | Bug fixes |
| `docs/<issue>-<slug>` | `develop` | `develop` | Documentation |
| `hotfix/<version>-<slug>` | `main` | `main` + `develop` | Urgent production fixes |

### Rules

1. **Conventional Commits required** - validated by pre-commit hook
2. **PR required** for `main` and `develop`
3. **Merge method**: Only Merge Commits (no squash, no rebase)
4. **One task = One PR** - closes the related issue

### Commit Types and Version Impact

| Type | When to use | SemVer impact |
|------|-------------|---------------|
| `feat` | New feature | MINOR bump |
| `fix` | Bug fix | PATCH bump |
| `docs` | Documentation | None |
| `chore` | Maintenance | None |
| `refactor` | Code restructure | None |
| `feat!` / `BREAKING CHANGE` | Breaking change | MAJOR bump |

### Workflow Example

.. code-block:: bash

   # 1. Create issue #42 "Add new feature"

   # 2. Switch to develop and create feature branch
   git checkout develop
   git pull origin develop
   git checkout -b feature/42-add-search

   # 3. Work on the branch, make commits
   git add . && git commit -m "feat: add search functionality (#42)"

   # 4. Push and create PR to develop
   git push -u origin feature/42-add-search
   gh pr create --base develop --title "feat: add search (#42)" --body "Closes #42"

   # 5. After merge to develop, accumulate features...

   # 6. When ready: PR develop → main
   gh pr create --base main --head develop --title "chore: release v0.4.0" --body "..."

   # 7. After merge to main, Release Please creates Release PR automatically

   # 8. Merge Release PR → Tag + PyPI publish + Docs deploy

### Hotfix Process

.. code-block:: bash

   # For critical bugs in production
   git checkout main
   git pull origin main
   git checkout -b hotfix/0.3.1-fix-critical

   # Make fix and commit
   git commit -m "fix: resolve critical issue"

   # PR to main
   gh pr create --base main --title "fix: critical hotfix" --body "..."

   # After merge: tag created automatically or manually
   git tag v0.3.1
   git push origin v0.3.1

   # Back-merge to develop
   git checkout develop
   git merge main
   git push origin develop

---

## 9. Release Process

Release Please is **automatic** - it calculates version based on conventional commits.

### Version Calculation

Release Please automatically determines the next version:

| Conventional Commit | Version Bump | Example |
|-------------------|--------------|---------|
| `feat:` | MINOR | 0.3.0 → 0.4.0 |
| `fix:` | PATCH | 0.3.0 → 0.3.1 |
| `feat!:` / `BREAKING CHANGE:` | MAJOR | 0.3.0 → 1.0.0 |

### Release Workflow

1. Accumulate changes in `develop` via PRs (feature/*, fix/*, docs/*)
2. When ready: Create PR from `develop` → `main`
3. After merging to `main`:
   - Release Please creates/updates a Release PR with CHANGELOG.md
   - The Release PR shows all changes since last release
4. Review the Release PR changelog
5. Merge the Release PR → automatic tag + GitHub Release + PyPI publish
6. Docs deploy automatically via `.github/workflows/docs.yml`

### Release Please Configuration

The `.release-please-config.json` is configured without `"release-as"` to allow
automatic version calculation:

.. code-block:: json

   {
     "packages": {
       ".": {
         "package-name": "ddlglot",
         "release-type": "python"
       }
     }
   }

### After Release

- Tag is created automatically (e.g., `v0.4.0`)
- GitHub Release is created with CHANGELOG content
- Package is published to PyPI via trusted publishing (OIDC)
- Documentation is deployed to GitHub Pages

### Hotfix Releases

For critical production bugs:

.. code-block:: bash

   # 1. Create hotfix from main
   git checkout main
   git checkout -b hotfix/0.3.1-fix-critical

   # 2. Make fix and commit
   git commit -m "fix: resolve critical issue"

   # 3. PR to main
   gh pr create --base main --title "fix: critical hotfix" --body "..."

   # 4. After merge: tag and push
   git tag v0.3.1
   git push origin v0.3.1

   # 5. Back-merge to develop
   git checkout develop
   git merge main
   git push origin develop
