"""ddlglot - Fluent DDL builder using SQLGlot AST."""

from __future__ import annotations

from ddlglot.builder import CreateBuilder, create
from ddlglot.exceptions import (
    ASTBuildError,
    DDLGlotError,
    DialectValidationError,
    InvalidPropertyError,
    PartitionByExpressionError,
    SchemaValidationError,
    UnsupportedDialectError,
    UnsupportedFeatureError,
    ValidationError,
)
from ddlglot.registry import (
    create_variant,
    get_variant,
    is_registered,
    list_variants,
    register_variant,
)
from ddlglot.variants import (
    BigQueryBuilder,
    DuckDBBuilder,
    HiveBuilder,
    PostgresBuilder,
    SparkDeltaBuilder,
    create_bigquery,
    create_duckdb,
    create_hive,
    create_postgres,
    create_spark_delta,
)

__all__ = [
    "create",
    "CreateBuilder",
    "DDLGlotError",
    "ValidationError",
    "DialectValidationError",
    "SchemaValidationError",
    "ASTBuildError",
    "UnsupportedDialectError",
    "PartitionByExpressionError",
    "UnsupportedFeatureError",
    "InvalidPropertyError",
    "create_spark_delta",
    "create_hive",
    "create_postgres",
    "create_duckdb",
    "create_bigquery",
    "SparkDeltaBuilder",
    "HiveBuilder",
    "PostgresBuilder",
    "DuckDBBuilder",
    "BigQueryBuilder",
    "register_variant",
    "get_variant",
    "create_variant",
    "list_variants",
    "is_registered",
]


def main() -> None:
    """Entry point for CLI usage."""
    print("Hello from ddlglot!")
