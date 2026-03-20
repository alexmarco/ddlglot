"""DuckDB variant."""

from __future__ import annotations

from typing import Any, Optional

from sqlglot import expressions as exp

from ..builder import create
from ..exceptions import UnsupportedFeatureError
from ..registry import register_variant


@register_variant("duckdb")
class DuckDBBuilder:
    """Fluent preset for DuckDB tables."""

    def __init__(self, kind: str = "TABLE") -> None:
        self._core = create(kind)

    def name(self, table: str) -> "DuckDBBuilder":
        """Set table name."""
        self._core.name(table)
        return self

    def if_not_exists(self, flag: bool = True) -> "DuckDBBuilder":
        """Add IF NOT EXISTS clause."""
        self._core.if_not_exists(flag)
        return self

    def temporary(self, flag: bool = True) -> "DuckDBBuilder":
        """Mark as TEMPORARY table."""
        self._core.temporary(flag)
        return self

    def comment(self, text: str) -> "DuckDBBuilder":
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
        default: Optional[Any] = None,
    ) -> "DuckDBBuilder":
        """Add a column definition."""
        self._core.column(name, dtype, not_null=not_null, pk=pk, unique=unique, default=default)
        return self

    def columns(self, *pairs) -> "DuckDBBuilder":
        """Add multiple columns."""
        self._core.columns(*pairs)
        return self

    def primary_key(self, *cols: str) -> "DuckDBBuilder":
        """Add PRIMARY KEY constraint."""
        self._core.primary_key(*cols)
        return self

    def unique_key(self, *cols: str) -> "DuckDBBuilder":
        """Add UNIQUE constraint."""
        self._core.unique_key(*cols)
        return self

    def partitioned_by(self, *cols) -> "DuckDBBuilder":
        """Add PARTITIONED BY clause.

        Raises:
            UnsupportedFeatureError: DuckDB does not support partitioning.
        """
        raise UnsupportedFeatureError(
            "PARTITIONED BY",
            "DuckDB",
            "DuckDB does not support table partitioning.",
        )

    def location(self, path: str) -> "DuckDBBuilder":
        """Set LOCATION path.

        Raises:
            UnsupportedFeatureError: DuckDB does not support external locations.
        """
        raise UnsupportedFeatureError(
            "LOCATION",
            "DuckDB",
            "DuckDB does not support external table locations.",
        )

    def tblproperties(self, props: dict[str, Any]) -> "DuckDBBuilder":
        """Add TBLPROPERTIES.

        Raises:
            UnsupportedFeatureError: DuckDB does not support TBLPROPERTIES.
        """
        raise UnsupportedFeatureError(
            "TBLPROPERTIES",
            "DuckDB",
            "DuckDB does not support table properties.",
        )

    def as_select(self, select_expr: exp.Expression) -> "DuckDBBuilder":
        """Set CTAS expression."""
        self._core.as_select(select_expr)
        return self

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot AST."""
        return self._core.to_ast()

    def sql(self, dialect: str = "duckdb", pretty: bool = False) -> str:
        """Generate SQL string with DuckDB dialect."""
        return self._core.sql(dialect=dialect, pretty=pretty)


def create_duckdb(kind: str = "TABLE") -> DuckDBBuilder:
    """Create a new DuckDB table builder."""
    return DuckDBBuilder(kind)
