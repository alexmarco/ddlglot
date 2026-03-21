"""Tests for validation and error handling."""

from __future__ import annotations

import pytest

from ddlglot import create
from ddlglot.exceptions import ASTBuildError


class TestBuilderValidation:
    """Tests for builder validation."""

    def test_missing_name_raises_ast_build_error(self) -> None:
        """Test that missing .name() raises ASTBuildError when calling to_ast()."""
        with pytest.raises(ASTBuildError) as exc_info:
            create("table").column("id", "INT").to_ast()
        assert "Missing .name" in str(exc_info.value)

    def test_invalid_kind(self) -> None:
        """Test that invalid kind is accepted (handled by SQLGlot at generation)."""
        sql = create("invalid_kind").name("test").column("id", "INT").sql(dialect="postgres")
        assert "INVALID_KIND" in sql


class TestDialectBehavior:
    """Tests for dialect-specific behavior."""

    def test_spark_delta_format(self) -> None:
        """Test Spark dialect uses USING DELTA."""
        sql = create("table").name("events").column("id", "INT").using("delta").sql(dialect="spark")
        assert "USING DELTA" in sql

    def test_hive_delta_format(self) -> None:
        """Test Hive dialect translates DELTA to STORED AS DELTA."""
        sql = create("table").name("events").column("id", "INT").using("delta").sql(dialect="hive")
        assert "STORED AS DELTA" in sql

    def test_bigquery_int64(self) -> None:
        """Test BigQuery uses INT64 instead of INT."""
        sql = create("table").name("users").column("id", "INT").sql(dialect="bigquery")
        assert "INT64" in sql

    def test_sqlite_integer(self) -> None:
        """Test SQLite uses INTEGER instead of INT."""
        sql = create("table").name("users").column("id", "INT").sql(dialect="sqlite")
        assert "INTEGER" in sql
