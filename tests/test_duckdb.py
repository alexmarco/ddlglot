"""Tests for DuckDB variant."""

from __future__ import annotations

from sqlglot import expressions as exp

from ddlglot.variants.duckdb import DuckDBBuilder, create_duckdb


class TestDuckDBBuilder:
    """Tests for DuckDB builder."""

    def test_create_table_basic(self) -> None:
        """Test basic table creation."""
        sql = create_duckdb().name("users").columns(("id", "INT"), ("name", "VARCHAR")).sql()
        assert "CREATE TABLE" in sql
        assert "users" in sql

    def test_primary_key(self) -> None:
        """Test PRIMARY KEY."""
        sql = create_duckdb().name("orders").column("id", "INT", pk=True, not_null=True).sql()
        assert "PRIMARY KEY" in sql

    def test_if_not_exists(self) -> None:
        """Test IF NOT EXISTS."""
        sql = create_duckdb().name("users").column("id", "INT").if_not_exists().sql()
        assert "IF NOT EXISTS" in sql

    def test_temporary(self) -> None:
        """Test TEMPORARY table."""
        sql = create_duckdb().name("temp_data").column("id", "INT").temporary().sql()
        assert "TEMPORARY" in sql

    def test_fluent_chaining(self) -> None:
        """Test fluent method chaining."""
        builder = create_duckdb().name("test").column("id", "INT")
        assert isinstance(builder, DuckDBBuilder)

    def test_to_ast(self) -> None:
        """Test to_ast returns exp.Create."""
        ast = create_duckdb().name("users").column("id", "INT").to_ast()
        assert isinstance(ast, exp.Create)

    def test_pretty_print(self) -> None:
        """Test pretty printing."""
        sql = (
            create_duckdb()
            .name("users")
            .columns(("id", "INT"), ("name", "VARCHAR"))
            .sql(pretty=True)
        )
        assert "\n" in sql
