"""Core fluent builder for DDL generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

from sqlglot import expressions as exp

from .exceptions import ASTBuildError
from .types import DDL, ColumnDef

if TYPE_CHECKING:
    pass

Lit = Union[str, int, float, bool]


def create(kind: str) -> CreateBuilder:
    """Create a new DDL builder for the specified kind (TABLE, VIEW, etc.)."""
    return CreateBuilder(kind)


class CreateBuilder:
    """Fluent builder for generating DDL statements using SQLGlot AST."""

    def __init__(self, kind: str) -> None:
        self.kind = kind.upper()
        self._table: str | None = None
        self._columns: list[exp.ColumnDef] = []
        self._table_constraints: list[exp.Expression] = []
        self._if_not_exists = False
        self._temporary: bool | None = None
        self._comment: str | None = None
        self._ctas_select: exp.Expression | None = None
        self._using: str | None = None
        self._partition_cols: list[exp.Expression] = []
        self._location: str | None = None
        self._tblprops: dict[str, Lit] = {}

    def name(self, table: str) -> CreateBuilder:
        """Set the table/view name."""
        self._table = table
        return self

    def if_not_exists(self, flag: bool = True) -> CreateBuilder:
        """Add IF NOT EXISTS clause."""
        self._if_not_exists = flag
        return self

    def temporary(self, flag: bool = True) -> CreateBuilder:
        """Mark as TEMPORARY table."""
        self._temporary = flag
        return self

    def comment(self, text: str) -> CreateBuilder:
        """Add table comment."""
        self._comment = text
        return self

    def column(
        self,
        name: str,
        dtype: str,
        *,
        not_null: bool = False,
        pk: bool = False,
        unique: bool = False,
        default: Lit | None = None,
    ) -> CreateBuilder:
        """Add a column definition."""
        constraints: list[exp.ColumnConstraint] = []
        if not_null:
            constraints.append(exp.ColumnConstraint(kind=exp.NotNullColumnConstraint()))
        if pk:
            constraints.append(exp.ColumnConstraint(kind=exp.PrimaryKey()))
        if unique:
            constraints.append(exp.ColumnConstraint(kind=exp.UniqueColumnConstraint()))
        if default is not None:
            lit = self._literal(default)
            constraints.append(exp.ColumnConstraint(kind=exp.DefaultColumnConstraint(this=lit)))

        self._columns.append(
            exp.ColumnDef(
                this=exp.to_identifier(name),
                kind=exp.DataType.build(dtype),
                constraints=constraints or None,
            )
        )
        return self

    def columns(self, *pairs: tuple[str, str]) -> CreateBuilder:
        """Add multiple columns from (name, dtype) pairs."""
        for name, dtype in pairs:
            self.column(name, dtype)
        return self

    def primary_key(self, *cols: str) -> CreateBuilder:
        """Add PRIMARY KEY constraint."""
        self._table_constraints.append(
            exp.PrimaryKey(expressions=[exp.to_identifier(c) for c in cols])
        )
        return self

    def unique_key(self, *cols: str) -> CreateBuilder:
        """Add UNIQUE constraint."""
        self._table_constraints.append(
            exp.UniqueColumnConstraint(
                this=exp.Schema(expressions=[exp.to_identifier(c) for c in cols])
            )
        )
        return self

    def as_select(self, select_expr: exp.Expression) -> CreateBuilder:
        """Set CTAS/VIEW expression (receives exp.Select)."""
        self._ctas_select = select_expr
        return self

    def using(self, fmt: str) -> CreateBuilder:
        """Set USING format (e.g., 'delta' in Spark)."""
        self._using = fmt
        return self

    def partitioned_by(self, *cols: str | exp.Expression) -> CreateBuilder:
        """Add PARTITIONED BY clause."""
        for col in cols:
            self._partition_cols.append(exp.to_identifier(col) if isinstance(col, str) else col)
        return self

    def location(self, path: str) -> CreateBuilder:
        """Set LOCATION path."""
        self._location = path
        return self

    def tblproperties(self, props: dict[str, Lit]) -> CreateBuilder:
        """Add TBLPROPERTIES (Spark/Hive)."""
        self._tblprops.update(props or {})
        return self

    @staticmethod
    def _literal(value: Lit) -> exp.Expression:
        """Convert Python value to SQLGlot literal."""
        if isinstance(value, bool):
            return exp.Boolean(this=value)
        if isinstance(value, (int, float)):
            return exp.Literal.number(value)
        return exp.Literal.string(value)

    def _build_properties(self) -> exp.Properties | None:
        """Build SQLGlot Properties expression."""
        exprs: list[exp.Expression] = []

        if self._temporary:
            exprs.append(exp.TemporaryProperty())

        if self._partition_cols:
            exprs.append(
                exp.PartitionedByProperty(this=exp.Schema(expressions=self._partition_cols))
            )

        if self._using:
            exprs.append(exp.FileFormatProperty(this=exp.to_identifier(self._using.upper())))

        if self._location:
            exprs.append(exp.LocationProperty(this=exp.Literal.string(self._location)))

        if self._tblprops:
            for k, v in self._tblprops.items():
                exprs.append(
                    exp.Property(
                        this=(exp.to_identifier(k) if "." not in k else exp.Identifier(this=k)),
                        value=self._literal(v),
                    )
                )

        if self._comment:
            exprs.append(exp.SchemaCommentProperty(this=exp.Literal.string(self._comment)))

        return exp.Properties(expressions=exprs) if exprs else None

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot exp.Create AST."""
        if not self._table:
            raise ASTBuildError("Missing .name(<table>)")

        table = exp.to_table(self._table)
        props = self._build_properties()

        if self._ctas_select is not None or self.kind == "VIEW":
            expr = self._ctas_select or exp.select("*")
            return exp.Create(
                kind=self.kind,
                this=table,
                expression=expr,
                properties=props,
                exists=self._if_not_exists,
            )

        schema = exp.Schema(this=table, expressions=[*self._columns, *self._table_constraints])
        return exp.Create(
            kind=self.kind,
            this=schema,
            properties=props,
            exists=self._if_not_exists,
        )

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

    def build(self) -> DDL:
        """Freeze and return a DDL object for inspection.

        Returns:
            A DDL instance with all defined properties accessible.
        """
        ast = self.to_ast()
        return DDL(
            kind=self.kind,
            table_name=self._table or "",
            columns=tuple(self._build_column_defs()),
            primary_keys=self._build_primary_keys(),
            unique_keys=self._build_unique_keys(),
            partition_cols=tuple(
                col.name if isinstance(col, exp.Identifier) else str(col)
                for col in self._partition_cols
            ),
            location=self._location,
            file_format=self._using.upper() if self._using else None,
            tblproperties=dict(self._tblprops),
            comment=self._comment,
            if_not_exists=self._if_not_exists,
            temporary=bool(self._temporary),
            _ast=ast,
        )

    def _build_column_defs(self) -> list[ColumnDef]:
        """Build public ColumnDef objects from internal column definitions."""
        result = []
        for col in self._columns:
            name = col.this.name if col.this else ""
            dtype = col.kind.sql() if col.kind else ""

            not_null = False
            pk = False
            unique = False
            default = None

            if col.constraints:
                for constraint in col.constraints:
                    if isinstance(constraint.kind, exp.NotNullColumnConstraint):
                        not_null = True
                    elif isinstance(constraint.kind, exp.PrimaryKey):
                        pk = True
                    elif isinstance(constraint.kind, exp.UniqueColumnConstraint):
                        unique = True
                    elif isinstance(constraint.kind, exp.DefaultColumnConstraint):
                        default = self._extract_default_value(constraint.kind)

            result.append(
                ColumnDef(
                    name=name,
                    dtype=dtype,
                    not_null=not_null,
                    pk=pk,
                    unique=unique,
                    default=default,
                )
            )
        return result

    def _extract_default_value(self, constraint: exp.DefaultColumnConstraint) -> Lit | None:
        """Extract Python value from DefaultColumnConstraint."""
        inner = constraint.this
        if isinstance(inner, exp.Boolean):
            return inner.this
        if isinstance(inner, exp.Literal):
            val = inner.this
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return val
            if isinstance(val, str):
                if val.isdigit():
                    return int(val)
                try:
                    return float(val)
                except ValueError:
                    return val
        return None

    def _build_primary_keys(self) -> tuple[str, ...]:
        """Build tuple of primary key column names."""
        for constraint in self._table_constraints:
            if isinstance(constraint, exp.PrimaryKey):
                return tuple(c.name for c in constraint.expressions)
        return ()

    def _build_unique_keys(self) -> tuple[tuple[str, ...], ...]:
        """Build tuple of unique constraint column tuples."""
        result: list[tuple[str, ...]] = []
        for constraint in self._table_constraints:
            if isinstance(constraint, exp.UniqueColumnConstraint):
                if constraint.this and constraint.this.expressions:
                    result.append(tuple(c.name for c in constraint.this.expressions))
                else:
                    result.append(())
        if result:
            return tuple(result)
        return ()

    @property
    def table_name(self) -> str | None:
        """Return the table/view name."""
        return self._table

    @property
    def columns_defs(self) -> list[ColumnDef]:
        """Return parsed column definitions."""
        return self._build_column_defs()

    @property
    def primary_keys(self) -> tuple[str, ...]:
        """Return primary key column names."""
        return self._build_primary_keys()

    @property
    def unique_keys(self) -> tuple[tuple[str, ...], ...]:
        """Return unique constraint column tuples."""
        return self._build_unique_keys()

    @property
    def partition_columns(self) -> tuple[str, ...]:
        """Return partition column names."""
        return tuple(
            col.name if isinstance(col, exp.Identifier) else str(col)
            for col in self._partition_cols
        )
