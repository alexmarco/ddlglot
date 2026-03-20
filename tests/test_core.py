"""Tests for core CreateBuilder."""

from __future__ import annotations

import pytest
from sqlglot import expressions as exp

from ddlglot import create
from ddlglot.builder import CreateBuilder
from ddlglot.exceptions import ASTBuildError


class TestCreateTable:
    """Tests for CREATE TABLE statements."""

    def test_create_table_basic(self) -> None:
        """Test basic CREATE TABLE."""
        sql = (
            create("table")
            .name("public.users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres")
        )
        assert "CREATE TABLE" in sql
        assert "public.users" in sql
        assert "id" in sql
        assert "INT" in sql
        assert "name" in sql

    def test_create_table_with_pk(self) -> None:
        """Test CREATE TABLE with primary key."""
        sql = (
            create("table")
            .name("t_facts")
            .column("key1", "INTEGER", pk=True, not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres")
        )
        assert "PRIMARY KEY" in sql

    def test_create_table_with_default(self) -> None:
        """Test CREATE TABLE with DEFAULT values."""
        sql = (
            create("table")
            .name("products")
            .column("id", "INT")
            .column("price", "DECIMAL(10,2)", default=0)
            .column("active", "BOOLEAN", default=True)
            .sql(dialect="postgres")
        )
        assert "DEFAULT" in sql

    def test_create_table_multiple_columns(self) -> None:
        """Test CREATE TABLE with multiple columns via .columns()."""
        sql = (
            create("table")
            .name("orders")
            .columns(("id", "INT"), ("amount", "DECIMAL(12,2)"), ("created_at", "TIMESTAMP"))
            .sql(dialect="postgres")
        )
        assert "id" in sql
        assert "amount" in sql
        assert "created_at" in sql

    def test_create_table_if_not_exists(self) -> None:
        """Test CREATE TABLE IF NOT EXISTS."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .if_not_exists()
            .sql(dialect="postgres")
        )
        assert "IF NOT EXISTS" in sql

    def test_create_table_temporary(self) -> None:
        """Test CREATE TEMPORARY TABLE."""
        sql = (
            create("table")
            .name("temp_data")
            .column("id", "INT")
            .temporary()
            .sql(dialect="postgres")
        )
        assert "TEMPORARY" in sql

    def test_create_table_with_comment(self) -> None:
        """Test CREATE TABLE with COMMENT."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .comment("User information table")
            .sql(dialect="mysql")
        )
        assert "COMMENT" in sql

    def test_create_table_with_primary_key_constraint(self) -> None:
        """Test CREATE TABLE with table-level PRIMARY KEY."""
        sql = (
            create("table")
            .name("order_items")
            .column("order_id", "INT")
            .column("product_id", "INT")
            .primary_key("order_id", "product_id")
            .sql(dialect="postgres")
        )
        assert "PRIMARY KEY" in sql

    def test_create_table_with_unique_constraint(self) -> None:
        """Test CREATE TABLE with UNIQUE constraint."""
        sql = (
            create("table")
            .name("users")
            .column("email", "VARCHAR(255)")
            .unique_key("email")
            .sql(dialect="postgres")
        )
        assert "UNIQUE" in sql

    def test_missing_name_raises_error(self) -> None:
        """Test that missing .name() raises ASTBuildError."""
        with pytest.raises(ASTBuildError):
            create("table").column("id", "INT").to_ast()


class TestCreateView:
    """Tests for CREATE VIEW statements."""

    def test_create_view_basic(self) -> None:
        """Test basic CREATE VIEW."""
        sql = (
            create("view")
            .name("active_users")
            .as_select(exp.select("*").from_("users").where("active = true"))
            .sql(dialect="postgres")
        )
        assert "CREATE VIEW" in sql
        assert "active_users" in sql
        assert "SELECT" in sql


class TestProperties:
    """Tests for DDL properties."""

    def test_using(self) -> None:
        """Test USING format property."""
        sql = create("table").name("events").column("id", "INT").using("delta").sql(dialect="spark")
        assert "USING DELTA" in sql

    def test_partitioned_by(self) -> None:
        """Test PARTITIONED BY property."""
        sql = (
            create("table")
            .name("events")
            .column("id", "INT")
            .column("event_date", "DATE")
            .partitioned_by("event_date")
            .sql(dialect="spark")
        )
        assert "PARTITIONED BY" in sql

    def test_location(self) -> None:
        """Test LOCATION property."""
        sql = (
            create("table")
            .name("external_data")
            .column("id", "INT")
            .location("s3://bucket/path/")
            .sql(dialect="spark")
        )
        assert "LOCATION" in sql
        assert "s3://bucket/path/" in sql

    def test_tblproperties(self) -> None:
        """Test TBLPROPERTIES."""
        sql = (
            create("table")
            .name("data")
            .column("id", "INT")
            .tblproperties({"delta.enableChangeDataFeed": True})
            .sql(dialect="spark")
        )
        assert "delta.enableChangeDataFeed" in sql or "WITH" in sql


class TestDialectOutput:
    """Tests for dialect-specific output."""

    def test_postgres_dialect(self) -> None:
        """Test Postgres dialect output."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres")
        )
        assert "CREATE TABLE" in sql

    def test_spark_dialect(self) -> None:
        """Test Spark dialect output."""
        sql = create("table").name("events").column("id", "INT").using("delta").sql(dialect="spark")
        assert "USING DELTA" in sql

    def test_pretty_print(self) -> None:
        """Test pretty printing."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres", pretty=True)
        )
        assert "\n" in sql

    def test_pretty_print_with_indent(self) -> None:
        """Test pretty printing with custom indent."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .sql(dialect="postgres", pretty=True, indent=4)
        )
        assert "\n" in sql

    def test_pretty_print_with_pad(self) -> None:
        """Test pretty printing with custom pad."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .sql(dialect="postgres", pretty=True, pad=4)
        )
        assert "\n" in sql

    def test_pretty_print_with_max_text_width(self) -> None:
        """Test pretty printing with custom max text width."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .column("name", "VARCHAR(100)")
            .column("email", "VARCHAR(255)")
            .column("active", "BOOLEAN")
            .column("created_at", "TIMESTAMP")
            .sql(dialect="postgres", pretty=True, max_text_width=40)
        )
        lines = sql.split("\n")
        for line in lines:
            assert len(line) <= 40, f"Line exceeds max width: {line}"


class TestFluentInterface:
    """Tests for fluent interface chaining."""

    def test_method_chaining(self) -> None:
        """Test that methods return self for chaining."""
        builder = create("table").name("test").column("id", "INT")
        assert isinstance(builder, CreateBuilder)

    def test_multiple_columns_chaining(self) -> None:
        """Test chaining with multiple columns."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .column("email", "VARCHAR(255)")
            .column("created_at", "TIMESTAMP")
            .sql(dialect="postgres")
        )
        assert sql.count("INT") == 1
        assert sql.count("VARCHAR(255)") == 1
        assert sql.count("TIMESTAMP") == 1


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_table_name(self) -> None:
        """Test that empty table name is handled."""
        with pytest.raises(ASTBuildError):
            create("table").column("id", "INT").to_ast()

    def test_to_ast_returns_exp_create(self) -> None:
        """Test that to_ast() returns exp.Create."""
        ast = create("table").name("users").column("id", "INT").to_ast()
        assert isinstance(ast, exp.Create)
