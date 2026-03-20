"""DDLGlot variants for specific SQL dialects."""

from __future__ import annotations

from .bigquery import BigQueryBuilder, create_bigquery
from .duckdb import DuckDBBuilder, create_duckdb
from .hive import HiveBuilder, create_hive
from .postgres import PostgresBuilder, create_postgres
from .spark_delta import SparkDeltaBuilder, create_spark_delta

__all__ = [
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
]
