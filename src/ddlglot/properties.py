"""Property helpers for DDL construction."""

from __future__ import annotations

from typing import Any

from sqlglot import expressions as exp


def literal(value: Any) -> exp.Expression:
    """Convert Python value to SQLGlot literal expression."""
    if isinstance(value, bool):
        return exp.Boolean(this=value)
    if isinstance(value, (int, float)):
        return exp.Literal.number(value)
    return exp.Literal.string(value)


def partition_by_property(
    cols: list[str | exp.Expression],
) -> exp.PartitionedByProperty:
    """Build PARTITIONED BY property."""
    expressions = [exp.to_identifier(c) if isinstance(c, str) else c for c in cols]
    return exp.PartitionedByProperty(this=exp.Schema(expressions=expressions))


def location_property(path: str) -> exp.LocationProperty:
    """Build LOCATION property."""
    return exp.LocationProperty(this=exp.Literal.string(path))


def file_format_property(fmt: str) -> exp.FileFormatProperty:
    """Build USING/FORMAT property."""
    return exp.FileFormatProperty(this=exp.to_identifier(fmt.upper()))


def comment_property(text: str) -> exp.SchemaCommentProperty:
    """Build COMMENT property."""
    return exp.SchemaCommentProperty(this=exp.Literal.string(text))


def tblproperties_property(props: dict[str, Any]) -> list[exp.Property]:
    """Build TBLPROPERTIES as list of Property expressions."""
    return [
        exp.Property(
            this=(exp.to_identifier(k) if "." not in k else exp.Identifier(this=k)),
            value=literal(v),
        )
        for k, v in props.items()
    ]


def build_properties(
    partitioned_cols: list[str | exp.Expression] | None = None,
    using: str | None = None,
    location: str | None = None,
    tblprops: dict[str, Any] | None = None,
    comment: str | None = None,
) -> exp.Properties | None:
    """Build Properties expression from components."""
    exprs: list[exp.Expression] = []

    if partitioned_cols:
        exprs.append(partition_by_property(partitioned_cols))

    if using:
        exprs.append(file_format_property(using))

    if location:
        exprs.append(location_property(location))

    if tblprops:
        exprs.extend(tblproperties_property(tblprops))

    if comment:
        exprs.append(comment_property(comment))

    return exp.Properties(expressions=exprs) if exprs else None
