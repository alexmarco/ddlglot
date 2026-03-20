"""Property helpers for DDL construction."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from sqlglot import expressions as exp


def literal(value: Any) -> exp.Expression:
    """Convert Python value to SQLGlot literal expression."""
    if isinstance(value, bool):
        return exp.Boolean(this=value)
    if isinstance(value, (int, float)):
        return exp.Literal.number(value)
    return exp.Literal.string(value)


def partition_by_property(
    cols: List[Union[str, exp.Expression]],
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


def tblproperties_property(props: Dict[str, Any]) -> List[exp.Property]:
    """Build TBLPROPERTIES as list of Property expressions."""
    return [
        exp.Property(
            this=(exp.to_identifier(k) if "." not in k else exp.Identifier(this=k)),
            value=literal(v),
        )
        for k, v in props.items()
    ]


def build_properties(
    partitioned_cols: Optional[List[Union[str, exp.Expression]]] = None,
    using: Optional[str] = None,
    location: Optional[str] = None,
    tblprops: Optional[Dict[str, Any]] = None,
    comment: Optional[str] = None,
) -> Optional[exp.Properties]:
    """Build Properties expression from components."""
    exprs: List[exp.Expression] = []

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
