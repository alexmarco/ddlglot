"""BigQuery variant with partitioning and clustering."""

from __future__ import annotations

from typing import Any

from sqlglot import expressions as exp

from ..builder import create
from ..exceptions import DialectValidationError
from ..registry import register_variant


@register_variant("bigquery")
class BigQueryBuilder:
    """Fluent preset for BigQuery tables."""

    def __init__(self, kind: str = "TABLE") -> None:
        self._core = create(kind)
        self._partition_by: str | None = None
        self._cluster_by: list[str] = []

    def name(self, table: str) -> BigQueryBuilder:
        """Set table name."""
        self._core.name(table)
        return self

    def if_not_exists(self, flag: bool = True) -> BigQueryBuilder:
        """Add IF NOT EXISTS clause."""
        self._core.if_not_exists(flag)
        return self

    def temporary(self, flag: bool = True) -> BigQueryBuilder:
        """Mark as TEMPORARY table."""
        self._core.temporary(flag)
        return self

    def comment(self, text: str) -> BigQueryBuilder:
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
    ) -> BigQueryBuilder:
        """Add a column definition."""
        self._core.column(name, dtype, not_null=not_null, pk=pk, unique=unique, default=default)
        return self

    def columns(self, *pairs) -> BigQueryBuilder:
        """Add multiple columns."""
        self._core.columns(*pairs)
        return self

    def primary_key(self, *cols: str) -> BigQueryBuilder:
        """Add PRIMARY KEY constraint."""
        self._core.primary_key(*cols)
        return self

    def unique_key(self, *cols: str) -> BigQueryBuilder:
        """Add UNIQUE constraint."""
        self._core.unique_key(*cols)
        return self

    def partitioned_by(self, partition_expr: str) -> BigQueryBuilder:
        """Set PARTITION BY column."""
        self._partition_by = partition_expr
        return self

    def cluster_by(self, *cols: str) -> BigQueryBuilder:
        """Add CLUSTER BY columns.

        Note: BigQuery requires partitioning when using clustering.
        """
        self._cluster_by.extend(cols)
        return self

    def as_select(self, select_expr: exp.Expression) -> BigQueryBuilder:
        """Set CTAS expression."""
        self._core.as_select(select_expr)
        return self

    def _validate(self) -> None:
        """Validate BigQuery-specific constraints."""
        if self._cluster_by and not self._partition_by:
            raise DialectValidationError(
                "CLUSTER BY requires PARTITION BY in BigQuery",
                dialect="bigquery",
            )

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot AST."""
        self._validate()
        return self._core.to_ast()

    def sql(self, dialect: str = "bigquery", pretty: bool = False) -> str:
        """Generate SQL string with BigQuery dialect."""
        self._validate()
        return self._core.sql(dialect=dialect, pretty=pretty)


def create_bigquery(kind: str = "TABLE") -> BigQueryBuilder:
    """Create a new BigQuery table builder."""
    return BigQueryBuilder(kind)
