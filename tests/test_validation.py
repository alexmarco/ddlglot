"""Tests for validation and error handling."""

from __future__ import annotations

from typing import NamedTuple

import pytest

from ddlglot import create
from ddlglot.builder import CreateBuilder
from ddlglot.exceptions import ASTBuildError, DDLGlotError, ValidationError


class ValidationCase(NamedTuple):
    """Test case for validation tests."""

    description: str
    builder_setup: CreateBuilder
    expected_error: type[Exception]
    error_message_contains: str | None = None


class TestBuilderValidation:
    """Tests for builder validation errors."""

    def test_missing_name_raises_ast_build_error(self) -> None:
        """Test that missing .name() raises ASTBuildError with descriptive message."""
        with pytest.raises(ASTBuildError, match=r"Missing.*name"):
            create("table").column("id", "INT").to_ast()

    def test_missing_name_with_multiple_columns(self) -> None:
        """Test that missing .name() raises error even with multiple columns."""
        with pytest.raises(ASTBuildError, match=r"Missing.*name"):
            create("table").columns(
                ("id", "INT"),
                ("name", "VARCHAR(100)"),
                ("active", "BOOLEAN"),
            ).to_ast()

    def test_missing_name_with_properties(self) -> None:
        """Test that missing .name() raises error even with properties set."""
        with pytest.raises(ASTBuildError, match=r"Missing.*name"):
            create("table").column("id", "INT").using("delta").location("s3://bucket/").to_ast()

    def test_invalid_kind_accepted_by_sqlglot(self) -> None:
        """Test that invalid kind is accepted (handled by SQLGlot at generation)."""
        sql = create("invalid_kind").name("test").column("id", "INT").sql(dialect="postgres")
        assert "INVALID_KIND" in sql

    def test_empty_kind_string(self) -> None:
        """Test that empty kind string is handled."""
        sql = create("").name("users").column("id", "INT").sql(dialect="postgres")
        assert "CREATE TABLE" in sql or "CREATE" in sql

    def test_sql_without_to_ast_raises(self) -> None:
        """Test that calling .sql() without .name() raises ASTBuildError."""
        with pytest.raises(ASTBuildError, match=r"Missing.*name"):
            create("table").column("id", "INT").sql(dialect="postgres")

    def test_unknown_type_raises(self) -> None:
        """Test that unknown types raise an error (ParseError from SQLGlot)."""
        with pytest.raises(Exception, match=r"CUSTOM_TYPE"):
            create("table").name("users").column("custom", "CUSTOM_TYPE").sql(dialect="postgres")

    def test_case_insensitive_types(self) -> None:
        """Test that type names are case-insensitive."""
        sql_lower = create("table").name("users").column("id", "int").sql(dialect="postgres")
        sql_upper = create("table").name("users").column("id", "INT").sql(dialect="postgres")
        sql_mixed = create("table").name("users").column("id", "Int").sql(dialect="postgres")

        assert "INT" in sql_lower
        assert "INT" in sql_upper
        assert "INT" in sql_mixed

    def test_numeric_types(self) -> None:
        """Test various numeric types."""
        for dtype in [
            "INT",
            "INTEGER",
            "BIGINT",
            "SMALLINT",
            "TINYINT",
            "FLOAT",
            "DOUBLE",
            "DECIMAL(10,2)",
        ]:
            sql = create("table").name("t").column("c", dtype).sql(dialect="postgres")
            assert "CREATE TABLE" in sql

    def test_string_types(self) -> None:
        """Test various string types."""
        for dtype in ["VARCHAR(100)", "CHAR(10)", "TEXT", "STRING"]:
            sql = create("table").name("t").column("c", dtype).sql(dialect="postgres")
            assert "CREATE TABLE" in sql

    def test_temporal_types(self) -> None:
        """Test various temporal types."""
        for dtype in ["DATE", "TIME", "TIMESTAMP", "DATETIME"]:
            sql = create("table").name("t").column("c", dtype).sql(dialect="postgres")
            assert "CREATE TABLE" in sql

    def test_boolean_type(self) -> None:
        """Test boolean type."""
        sql = create("table").name("users").column("active", "BOOLEAN").sql(dialect="postgres")
        assert "active" in sql.lower()
        assert "BOOLEAN" in sql

    def test_blob_types(self) -> None:
        """Test blob/binary types."""
        for dtype in ["BLOB", "BINARY", "VARBINARY"]:
            sql = create("table").name("t").column("c", dtype).sql(dialect="postgres")
            assert "CREATE TABLE" in sql


class TestConstraintValidation:
    """Tests for constraint validation."""

    def test_pk_and_unique_together(self) -> None:
        """Test PRIMARY KEY and UNIQUE can coexist."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT", pk=True)
            .column("email", "VARCHAR(100)")
            .unique_key("email")
            .sql(dialect="postgres")
        )
        assert "PRIMARY KEY" in sql
        assert "UNIQUE" in sql

    def test_multiple_pk_columns(self) -> None:
        """Test composite PRIMARY KEY with multiple columns."""
        sql = (
            create("table")
            .name("order_items")
            .column("order_id", "INT")
            .column("product_id", "INT")
            .primary_key("order_id", "product_id")
            .sql(dialect="postgres")
        )
        assert "PRIMARY KEY (order_id, product_id)" in sql

    def test_not_null_without_pk(self) -> None:
        """Test NOT NULL without PRIMARY KEY."""
        sql = (
            create("table")
            .name("users")
            .column("name", "VARCHAR(100)", not_null=True)
            .sql(dialect="postgres")
        )
        assert "NOT NULL" in sql
        assert "PRIMARY KEY" not in sql

    def test_unique_constraint_only(self) -> None:
        """Test UNIQUE constraint without PRIMARY KEY."""
        sql = (
            create("table")
            .name("users")
            .column("email", "VARCHAR(100)")
            .unique_key("email")
            .sql(dialect="postgres")
        )
        assert "UNIQUE" in sql
        assert "PRIMARY KEY" not in sql

    def test_default_with_not_null(self) -> None:
        """Test DEFAULT value combined with NOT NULL."""
        sql = (
            create("table")
            .name("products")
            .column("name", "VARCHAR(100)", not_null=True, default="Unknown")
            .sql(dialect="postgres")
        )
        assert "NOT NULL" in sql
        assert "DEFAULT" in sql


class TestPropertiesValidation:
    """Tests for property validation."""

    def test_empty_using(self) -> None:
        """Test empty USING clause."""
        sql = create("table").name("t").column("id", "INT").using("").sql(dialect="spark")
        assert "CREATE TABLE" in sql

    def test_partitioned_by_empty(self) -> None:
        """Test empty PARTITIONED BY clause."""
        sql = create("table").name("t").column("id", "INT").partitioned_by().sql(dialect="spark")
        assert "CREATE TABLE" in sql

    def test_location_with_special_characters(self) -> None:
        """Test LOCATION with special characters in path."""
        sql = (
            create("table")
            .name("external")
            .column("id", "INT")
            .location("s3://bucket/path/with spaces/data")
            .sql(dialect="spark")
        )
        assert "external" in sql
        assert "LOCATION" in sql

    def test_multiple_tblproperties(self) -> None:
        """Test multiple TBLPROPERTIES."""
        sql = (
            create("table")
            .name("data")
            .column("id", "INT")
            .tblproperties({"key1": "value1", "key2": "value2"})
            .sql(dialect="spark")
        )
        assert "key1" in sql
        assert "key2" in sql

    def test_tblproperties_empty(self) -> None:
        """Test empty TBLPROPERTIES dict."""
        sql = create("table").name("t").column("id", "INT").tblproperties({}).sql(dialect="spark")
        assert "CREATE TABLE" in sql


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_ast_build_error_is_ddlglot_error(self) -> None:
        """Test that ASTBuildError inherits from DDLGlotError."""
        with pytest.raises(DDLGlotError, match=r".+"):
            create("table").to_ast()

    def test_validation_error_is_ddlglot_error(self) -> None:
        """Test that ValidationError inherits from DDLGlotError."""
        assert issubclass(ValidationError, DDLGlotError)

    def test_ast_build_error_message(self) -> None:
        """Test ASTBuildError message contains helpful information."""
        with pytest.raises(ASTBuildError, match=r".+"):
            create("table").to_ast()


class TestEdgeCaseValidation:
    """Tests for edge case validation."""

    def test_view_without_as_select(self) -> None:
        """Test VIEW without as_select generates valid SQL."""
        sql = create("view").name("v").sql(dialect="postgres")
        assert "CREATE VIEW" in sql

    def test_cte_with_complex_expression(self) -> None:
        """Test that complex expressions in defaults are handled."""
        sql = (
            create("table")
            .name("events")
            .column("id", "INT")
            .column("created", "TIMESTAMP", default="NOW()")
            .sql(dialect="postgres")
        )
        assert "CREATE TABLE" in sql
        assert "created" in sql.lower()

    def test_chained_builder_methods(self) -> None:
        """Test that all builder methods can be chained."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT", pk=True, not_null=True)
            .column("name", "VARCHAR(100)")
            .column("active", "BOOLEAN", default=True)
            .if_not_exists()
            .temporary()
            .comment("User table")
            .sql(dialect="postgres")
        )
        assert "CREATE TEMPORARY TABLE IF NOT EXISTS" in sql
        assert "users" in sql
        assert "PRIMARY KEY" in sql

    def test_all_dialects_handle_basic_table(self) -> None:
        """Test that all supported dialects can generate basic tables."""
        dialects = ["postgres", "spark", "bigquery", "duckdb", "sqlite", "hive"]
        for dialect in dialects:
            sql = create("table").name("t").column("id", "INT").sql(dialect=dialect)
            assert "CREATE TABLE" in sql, f"Failed for dialect: {dialect}"
