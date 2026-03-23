"""Public types for DDL inspection."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from sqlglot import expressions as exp


@dataclass(frozen=True, slots=True)
class ColumnDef:
    """Immutable column definition."""

    name: str
    dtype: str
    not_null: bool = False
    pk: bool = False
    unique: bool = False
    default: Any = None


@dataclass(frozen=True, slots=True)
class DDL:
    """Immutable DDL descriptor with inspection methods."""

    kind: str
    table_name: str
    _ast: exp.Create = field(repr=False)
    columns: tuple[ColumnDef, ...] = field(default_factory=tuple)
    primary_keys: tuple[str, ...] = field(default_factory=tuple)
    unique_keys: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    partition_cols: tuple[str, ...] = field(default_factory=tuple)
    location: str | None = None
    file_format: str | None = None
    tblproperties: Mapping[str, Any] = field(default_factory=dict)
    comment: str | None = None
    if_not_exists: bool = False
    temporary: bool = False

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
        return self._ast.sql(
            dialect=dialect,
            pretty=pretty,
            indent=indent,
            pad=pad,
            max_text_width=max_text_width,
        )

    def to_ast(self) -> exp.Create:
        """Return the underlying SQLGlot exp.Create AST."""
        return self._ast
