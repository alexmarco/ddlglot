"""ddlglot - Fluent DDL builder using SQLGlot AST."""

from __future__ import annotations

from ddlglot.builder import CreateBuilder, create
from ddlglot.exceptions import (
    ASTBuildError,
    DDLGlotError,
    SchemaValidationError,
    ValidationError,
)
from ddlglot.types import DDL, ColumnDef

__all__ = [
    "DDL",
    "ASTBuildError",
    "ColumnDef",
    "CreateBuilder",
    "DDLGlotError",
    "SchemaValidationError",
    "ValidationError",
    "create",
]


def main() -> None:
    """Entry point for CLI usage."""
    print("Hello from ddlglot!")
