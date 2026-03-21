"""Spark + Delta Lake variant."""

from __future__ import annotations

from typing import Any

from sqlglot import expressions as exp

from ..builder import create
from ..exceptions import PartitionByExpressionError, UnsupportedFeatureError
from ..registry import register_variant

DELTA_FORMAT = "DELTA"
DELTA_PROPERTIES = {
    "enableChangeDataFeed": "delta.enableChangeDataFeed",
    "appendOnly": "delta.appendOnly",
    "logRetentionDuration": "delta.logRetentionDuration",
    "deletedFileRetentionDuration": "delta.deletedFileRetentionDuration",
    "dataSkippingNumIndexedCols": "delta.dataSkippingNumIndexedCols",
}


@register_variant("spark_delta")
class SparkDeltaBuilder:
    """Fluent preset for Spark+Delta tables."""

    def __init__(self, kind: str = "TABLE") -> None:
        self._core = create(kind).using(DELTA_FORMAT)
        self._validate_delta_properties: list[str] = []

    def name(self, table: str) -> SparkDeltaBuilder:
        """Set table name."""
        self._core.name(table)
        return self

    def if_not_exists(self, flag: bool = True) -> SparkDeltaBuilder:
        """Add IF NOT EXISTS clause."""
        self._core.if_not_exists(flag)
        return self

    def temporary(self, flag: bool = True) -> SparkDeltaBuilder:
        """Mark as TEMPORARY table."""
        self._core.temporary(flag)
        return self

    def comment(self, text: str) -> SparkDeltaBuilder:
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
    ) -> SparkDeltaBuilder:
        """Add a column definition."""
        self._core.column(name, dtype, not_null=not_null, pk=pk, unique=unique, default=default)
        return self

    def columns(self, *pairs) -> SparkDeltaBuilder:
        """Add multiple columns."""
        self._core.columns(*pairs)
        return self

    def primary_key(self, *cols: str) -> SparkDeltaBuilder:
        """Add PRIMARY KEY constraint."""
        self._core.primary_key(*cols)
        return self

    def unique_key(self, *cols: str) -> SparkDeltaBuilder:
        """Add UNIQUE constraint."""
        self._core.unique_key(*cols)
        return self

    def partitioned_by(self, *cols) -> SparkDeltaBuilder:
        """Add PARTITIONED BY clause.

        Note: Delta Lake only supports partitioning by column names,
        not by expressions. For partitioning by derived values,
        use generated_column() instead.
        """
        for col in cols:
            if not isinstance(col, str):
                raise PartitionByExpressionError("Delta Lake")
        self._core.partitioned_by(*cols)
        return self

    def location(self, path: str) -> SparkDeltaBuilder:
        """Set LOCATION path."""
        self._core.location(path)
        return self

    def tblproperties(self, props: dict[str, Any]) -> SparkDeltaBuilder:
        """Add TBLPROPERTIES."""
        for key in props:
            if not key.startswith("delta."):
                self._validate_delta_properties.append(key)
        self._core.tblproperties(props)
        return self

    def as_select(self, select_expr: exp.Expression) -> SparkDeltaBuilder:
        """Set CTAS expression."""
        self._core.as_select(select_expr)
        return self

    def enable_cdf(self, flag: bool = True) -> SparkDeltaBuilder:
        """Enable Change Data Feed."""
        return self.tblproperties({"delta.enableChangeDataFeed": flag})

    def append_only(self, flag: bool = True) -> SparkDeltaBuilder:
        """Set appendOnly property."""
        return self.tblproperties({"delta.appendOnly": flag})

    def log_retention(self, interval: str) -> SparkDeltaBuilder:
        """Set logRetentionDuration (e.g., '30 days')."""
        return self.tblproperties({"delta.logRetentionDuration": interval})

    def deleted_file_retention(self, interval: str) -> SparkDeltaBuilder:
        """Set deletedFileRetentionDuration (e.g., '7 days')."""
        return self.tblproperties({"delta.deletedFileRetentionDuration": interval})

    def generated_column(self, name: str, dtype: str, expression_sql: str) -> SparkDeltaBuilder:
        """Create a GENERATED ALWAYS AS column.

        Useful for partitioning by a derived date (Delta doesn't support
        PARTITIONED BY with expressions).
        """
        gen = exp.ColumnConstraint(
            kind=exp.GeneratedAsIdentityColumnConstraint(
                this=True, expression=exp.Anonymous(this=expression_sql)
            )
        )
        self._core._columns.append(
            exp.ColumnDef(
                this=exp.to_identifier(name),
                kind=exp.DataType.build(dtype),
                constraints=[gen],
            )
        )
        return self

    def _validate(self) -> None:
        """Validate Delta-specific constraints."""
        if self._validate_delta_properties:
            raise UnsupportedFeatureError(
                "TBLPROPERTIES without delta. prefix",
                "Delta Lake",
                "Use 'delta.<property>' naming convention.",
            )

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot AST."""
        self._validate()
        return self._core.to_ast()

    def sql(self, pretty: bool = False) -> str:
        """Generate SQL string with Spark dialect."""
        self._validate()
        return self._core.sql(dialect="spark", pretty=pretty)


def create_spark_delta(kind: str = "TABLE") -> SparkDeltaBuilder:
    """Create a new Spark+Delta table builder."""
    return SparkDeltaBuilder(kind)
