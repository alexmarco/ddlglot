"""Tests for dialect validation."""

from __future__ import annotations

import pytest
from sqlglot import expressions as exp

from ddlglot.exceptions import (
    DialectValidationError,
    PartitionByExpressionError,
    UnsupportedFeatureError,
)
from ddlglot.variants.bigquery import create_bigquery
from ddlglot.variants.duckdb import create_duckdb
from ddlglot.variants.spark_delta import create_spark_delta


class TestSparkDeltaValidation:
    """Tests for Spark+Delta validation."""

    def test_partitioned_by_with_expression_raises(self) -> None:
        """Test that partitioned_by with expression raises PartitionByExpressionError."""
        with pytest.raises(PartitionByExpressionError) as exc_info:
            create_spark_delta().partitioned_by(exp.column("DATE(ts)"))
        assert "Delta Lake" in str(exc_info.value)

    def test_partitioned_by_with_string_works(self) -> None:
        """Test that partitioned_by with string works."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .columns(("id", "INT"), ("event_date", "DATE"))
            .partitioned_by("event_date")
            .sql()
        )
        assert "PARTITIONED BY" in sql

    def test_non_delta_tblproperties_raises(self) -> None:
        """Test that non-delta TBLPROPERTIES raises UnsupportedFeatureError."""
        builder = create_spark_delta().name("test").tblproperties({"format": "parquet"})
        with pytest.raises(UnsupportedFeatureError) as exc_info:
            builder.sql()
        assert "delta." in str(exc_info.value)

    def test_delta_tblproperties_works(self) -> None:
        """Test that delta TBLPROPERTIES works."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .column("id", "INT")
            .tblproperties({"delta.enableChangeDataFeed": True})
            .sql()
        )
        assert "delta.enableChangeDataFeed" in sql


class TestDuckDBValidation:
    """Tests for DuckDB validation."""

    def test_partitioned_by_raises(self) -> None:
        """Test that partitioned_by raises UnsupportedFeatureError."""
        with pytest.raises(UnsupportedFeatureError) as exc_info:
            create_duckdb().name("test").partitioned_by("date_col")
        assert "DuckDB" in str(exc_info.value)
        assert "PARTITIONED BY" in str(exc_info.value)

    def test_location_raises(self) -> None:
        """Test that location raises UnsupportedFeatureError."""
        with pytest.raises(UnsupportedFeatureError) as exc_info:
            create_duckdb().name("test").location("/path/to/table")
        assert "DuckDB" in str(exc_info.value)
        assert "LOCATION" in str(exc_info.value)

    def test_tblproperties_raises(self) -> None:
        """Test that tblproperties raises UnsupportedFeatureError."""
        with pytest.raises(UnsupportedFeatureError) as exc_info:
            create_duckdb().name("test").tblproperties({"key": "value"})
        assert "DuckDB" in str(exc_info.value)
        assert "TBLPROPERTIES" in str(exc_info.value)

    def test_basic_table_works(self) -> None:
        """Test that basic table creation works."""
        sql = create_duckdb().name("users").columns(("id", "INT"), ("name", "VARCHAR")).sql()
        assert "CREATE TABLE" in sql
        assert "users" in sql


class TestBigQueryValidation:
    """Tests for BigQuery validation."""

    def test_cluster_by_without_partition_raises(self) -> None:
        """Test that cluster_by without partition_by raises DialectValidationError."""
        with pytest.raises(DialectValidationError) as exc_info:
            create_bigquery().name("test").cluster_by("user_id").sql()
        assert "BigQuery" in str(exc_info.value)
        assert "CLUSTER BY" in str(exc_info.value)
        assert "PARTITION BY" in str(exc_info.value)

    def test_cluster_by_with_partition_works(self) -> None:
        """Test that cluster_by with partition_by works."""
        sql = (
            create_bigquery()
            .name("project.dataset.events")
            .columns(("id", "INT64"), ("event_date", "DATE"), ("user_id", "INT64"))
            .partitioned_by("event_date")
            .cluster_by("user_id")
            .sql()
        )
        assert "CREATE TABLE" in sql

    def test_partition_by_only_works(self) -> None:
        """Test that partition_by without cluster_by works."""
        sql = (
            create_bigquery()
            .name("project.dataset.events")
            .columns(("id", "INT64"), ("event_date", "DATE"))
            .partitioned_by("event_date")
            .sql()
        )
        assert "CREATE TABLE" in sql

    def test_basic_table_works(self) -> None:
        """Test that basic table creation works."""
        sql = (
            create_bigquery()
            .name("project.dataset.users")
            .columns(("id", "INT64"), ("name", "STRING"))
            .sql()
        )
        assert "CREATE TABLE" in sql
