"""Fluent builder for CREATE INDEX statements."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlglot import expressions as exp

from .types import IndexDef

if TYPE_CHECKING:
    pass


def create_index(name: str) -> IndexBuilder:
    """Create a new IndexBuilder for the specified index name."""
    return IndexBuilder(name)


class IndexBuilder:
    """Fluent builder for generating CREATE INDEX statements using SQLGlot AST."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._table: str | None = None
        self._columns: list[str] = []
        self._unique = False
        self._using: str | None = None
        self._where: str | None = None
        self._include: list[str] = []
        self._comment: str | None = None

    def on(self, table: str, *cols: str) -> IndexBuilder:
        """Set the table and columns to index.

        Args:
            table: Table name.
            *cols: Column names to include in the index.
        """
        self._table = table
        self._columns = list(cols)
        return self

    def unique(self, flag: bool = True) -> IndexBuilder:
        """Mark the index as UNIQUE."""
        self._unique = flag
        return self

    def using(self, algorithm: str) -> IndexBuilder:
        """Set the index algorithm (e.g., btree, hash, gist, gin, brin).

        Args:
            algorithm: Index type (backend-specific).
        """
        self._using = algorithm.lower()
        return self

    def where(self, predicate: str) -> IndexBuilder:
        """Add a WHERE clause for partial indexes.

        Args:
            predicate: SQL predicate (e.g., "active = true").
        """
        self._where = predicate
        return self

    def include(self, *cols: str) -> IndexBuilder:
        """Add INCLUDE columns (covered columns, backend-specific).

        Args:
            *cols: Column names to include in the index.
        """
        self._include = list(cols)
        return self

    def comment(self, text: str) -> IndexBuilder:
        """Add a comment to the index."""
        self._comment = text
        return self

    def to_ast(self) -> exp.Create:
        """Build and return SQLGlot exp.Create AST for INDEX."""
        if not self._table or not self._columns:
            raise ValueError("Missing .on(<table>, <columns>)")

        columns = [exp.Ordered(this=exp.to_identifier(col)) for col in self._columns]

        index = exp.Index(
            this=exp.to_identifier(self._name),
            table=exp.to_table(self._table),
            expressions=[exp.Ordered(this=exp.to_identifier(col)) for col in self._columns],
            unique=self._unique,
            params=exp.IndexParameters(
                using=exp.to_identifier(self._using) if self._using else None,
                columns=columns,
                where=exp.Where(this=exp.condition(self._where)) if self._where else None,
                include=[exp.to_identifier(c) for c in self._include] if self._include else None,
            ),
        )

        return exp.Create(
            this=index,
            kind="INDEX",
        )

    def sql(
        self,
        dialect: str | None = None,
        pretty: bool = False,
        indent: int = 2,
        pad: int = 2,
        max_text_width: int = 80,
    ) -> str:
        """Generate SQL CREATE INDEX string.

        Args:
            dialect: SQL dialect (e.g., "postgres", "mysql").
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

    def build(self) -> IndexDef:
        """Build and return an IndexDef for inspection.

        Returns:
            An IndexDef instance with all index properties.
        """
        return IndexDef(
            name=self._name,
            table=self._table,
            columns=tuple(self._columns),
            unique=self._unique,
            using=self._using,
            where=self._where,
            include=tuple(self._include),
            comment=self._comment,
        )
