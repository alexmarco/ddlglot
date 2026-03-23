"""ddlglot - Fluent DDL builder using SQLGlot AST."""

from __future__ import annotations

from ddlglot.builder import CreateBuilder, create
from ddlglot.exceptions import (
    ASTBuildError,
    DDLGlotError,
    SchemaValidationError,
    ValidationError,
)
from ddlglot.indexer import IndexBuilder, create_index
from ddlglot.types import (
    DDL,
    CheckDef,
    ColumnDef,
    ForeignKeyDef,
    IndexDef,
    UniqueDef,
)

__all__ = [
    "DDL",
    "ASTBuildError",
    "CheckDef",
    "ColumnDef",
    "CreateBuilder",
    "DDLGlotError",
    "ForeignKeyDef",
    "IndexBuilder",
    "IndexDef",
    "SchemaValidationError",
    "UniqueDef",
    "ValidationError",
    "create",
    "create_index",
]


def main() -> None:
    """Entry point for CLI usage."""
    print("Hello from ddlglot!")
