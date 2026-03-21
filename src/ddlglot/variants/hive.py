"""Hive variant with SERDE/ROW FORMAT support."""

from __future__ import annotations

from typing import Any

from sqlglot import expressions as exp

from ..builder import create
from ..registry import register_variant


@register_variant("hive")
class HiveBuilder:
    """Fluent preset for Hive tables."""

    def __init__(self, kind: str = "TABLE") -> None:
        self._core = create(kind)
        self._row_format: exp.Expression | None = None
        self._stored_as: str | None = None
        self._stored_as_input_format: tuple[str, str] | None = None

    def name(self, table: str) -> HiveBuilder:
        """Set table name."""
        self._core.name(table)
        return self

    def if_not_exists(self, flag: bool = True) -> HiveBuilder:
        """Add IF NOT EXISTS clause."""
        self._core.if_not_exists(flag)
        return self

    def temporary(self, flag: bool = True) -> HiveBuilder:
        """Mark as TEMPORARY table."""
        self._core.temporary(flag)
        return self

    def comment(self, text: str) -> HiveBuilder:
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
    ) -> HiveBuilder:
        """Add a column definition."""
        self._core.column(name, dtype, not_null=not_null, pk=pk, unique=unique, default=default)
        return self

    def columns(self, *pairs) -> HiveBuilder:
        """Add multiple columns."""
        self._core.columns(*pairs)
        return self

    def primary_key(self, *cols: str) -> HiveBuilder:
        """Add PRIMARY KEY constraint."""
        self._core.primary_key(*cols)
        return self

    def unique_key(self, *cols: str) -> HiveBuilder:
        """Add UNIQUE constraint."""
        self._core.unique_key(*cols)
        return self

    def partitioned_by(self, *cols) -> HiveBuilder:
        """Add PARTITIONED BY clause."""
        self._core.partitioned_by(*cols)
        return self

    def location(self, path: str) -> HiveBuilder:
        """Set LOCATION path."""
        self._core.location(path)
        return self

    def tblproperties(self, props: dict[str, Any]) -> HiveBuilder:
        """Add TBLPROPERTIES."""
        self._core.tblproperties(props)
        return self

    def as_select(self, select_expr: exp.Expression) -> HiveBuilder:
        """Set CTAS expression."""
        self._core.as_select(select_expr)
        return self

    def row_format(self, format_type: str, serde: str | None = None) -> HiveBuilder:
        """Set ROW FORMAT (DELIMITED, SERDE)."""
        if serde:
            self._row_format = exp.RowFormatSerdeProperty(this=exp.Literal.string(serde))
        else:
            self._row_format = exp.RowFormatDelimitedProperty()
        return self

    def stored_as(self, format_type: str) -> HiveBuilder:
        """Set STORED AS format (e.g., PARQUET, ORC, AVRO)."""
        self._stored_as = format_type.upper()
        return self

    def stored_as_input_output(self, input_format: str, output_format: str) -> HiveBuilder:
        """Set STORED AS INPUTFORMAT OUTPUTFORMAT."""
        self._stored_as_input_format = (input_format, output_format)
        return self

    def _build_properties(self) -> exp.Properties | None:
        """Build Hive-specific properties."""
        exprs: list[exp.Expression] = []

        if self._core._partition_cols:
            exprs.append(
                exp.PartitionedByProperty(this=exp.Schema(expressions=self._core._partition_cols))
            )

        if self._core._location:
            exprs.append(exp.LocationProperty(this=exp.Literal.string(self._core._location)))

        if self._core._tblprops:
            for k, v in self._core._tblprops.items():
                exprs.append(
                    exp.Property(
                        this=exp.to_identifier(k),
                        value=exp.Literal.string(str(v))
                        if isinstance(v, str)
                        else exp.Literal.number(v),
                    )
                )

        if self._core._comment:
            exprs.append(exp.SchemaCommentProperty(this=exp.Literal.string(self._core._comment)))

        if self._stored_as:
            exprs.append(exp.FileFormatProperty(this=exp.to_identifier(self._stored_as)))

        if self._stored_as_input_format:
            inp, out = self._stored_as_input_format
            exprs.append(
                exp.RowFormatProperty(
                    this=exp.RowFormatSerdeProperty(this=exp.Literal.string(f"{inp} {out}"))
                )
            )

        if self._row_format:
            exprs.append(self._row_format)

        return exp.Properties(expressions=exprs) if exprs else None

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot AST."""
        if not self._core._table:
            from ..exceptions import ASTBuildError

            raise ASTBuildError("Missing .name(<table>)")

        table = exp.to_table(self._core._table)
        props = self._build_properties()

        schema = exp.Schema(
            this=table,
            expressions=[*self._core._columns, *self._core._table_constraints],
        )

        return exp.Create(
            kind=self._core.kind,
            this=table,
            expression=schema,
            properties=props,
            exists=self._core._if_not_exists,
        )

    def sql(self, dialect: str = "hive", pretty: bool = False) -> str:
        """Generate SQL string with Hive dialect."""
        return self.to_ast().sql(dialect=dialect, pretty=pretty)


def create_hive(kind: str = "TABLE") -> HiveBuilder:
    """Create a new Hive table builder."""
    return HiveBuilder(kind)
