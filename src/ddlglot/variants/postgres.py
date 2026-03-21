"""Postgres variant."""

from __future__ import annotations

from typing import Any

from sqlglot import expressions as exp

from ..builder import create
from ..registry import register_variant


@register_variant("postgres")
class PostgresBuilder:
    """Fluent preset for PostgreSQL tables."""

    def __init__(self, kind: str = "TABLE") -> None:
        self._core = create(kind)

    def name(self, table: str) -> PostgresBuilder:
        """Set table name."""
        self._core.name(table)
        return self

    def if_not_exists(self, flag: bool = True) -> PostgresBuilder:
        """Add IF NOT EXISTS clause."""
        self._core.if_not_exists(flag)
        return self

    def temporary(self, flag: bool = True) -> PostgresBuilder:
        """Mark as TEMPORARY table."""
        self._core.temporary(flag)
        return self

    def comment(self, text: str) -> PostgresBuilder:
        """Add table comment."""
        self._core.comment(text)
        return self

    def column(
        self,
        name: str,
        dtype: str,
        *,
        not_null: bool = False,
        pk: bool = False,
        unique: bool = False,
        default: Any | None = None,
    ) -> PostgresBuilder:
        """Add a column definition."""
        self._core.column(name, dtype, not_null=not_null, pk=pk, unique=unique, default=default)
        return self

    def columns(self, *pairs) -> PostgresBuilder:
        """Add multiple columns."""
        self._core.columns(*pairs)
        return self

    def primary_key(self, *cols: str) -> PostgresBuilder:
        """Add PRIMARY KEY constraint."""
        self._core.primary_key(*cols)
        return self

    def unique_key(self, *cols: str) -> PostgresBuilder:
        """Add UNIQUE constraint."""
        self._core.unique_key(*cols)
        return self

    def as_select(self, select_expr: exp.Expression) -> PostgresBuilder:
        """Set CTAS expression."""
        self._core.as_select(select_expr)
        return self

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot AST."""
        return self._core.to_ast()

    def sql(self, dialect: str = "postgres", pretty: bool = False) -> str:
        """Generate SQL string with PostgreSQL dialect."""
        return self._core.sql(dialect=dialect, pretty=pretty)


def create_postgres(kind: str = "TABLE") -> PostgresBuilder:
    """Create a new PostgreSQL table builder."""
    return PostgresBuilder(kind)
