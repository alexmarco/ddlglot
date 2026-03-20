"""Tests for Postgres variant."""

from __future__ import annotations

from sqlglot import expressions as exp

from ddlglot.variants.postgres import PostgresBuilder, create_postgres


class TestPostgresBuilder:
    """Tests for PostgreSQL builder."""

    def test_create_table_basic(self) -> None:
        """Test basic table creation."""
        sql = (
            create_postgres()
            .name("public.users")
            .columns(("id", "INT"), ("name", "VARCHAR(100)"))
            .sql()
        )
        assert "CREATE TABLE" in sql
        assert "public.users" in sql

    def test_primary_key(self) -> None:
        """Test PRIMARY KEY."""
        sql = (
            create_postgres()
            .name("orders")
            .column("id", "INT", pk=True, not_null=True)
            .column("name", "VARCHAR(100)")
            .sql()
        )
        assert "PRIMARY KEY" in sql

    def test_unique_constraint(self) -> None:
        """Test UNIQUE constraint."""
        sql = (
            create_postgres()
            .name("users")
            .column("email", "VARCHAR(255)")
            .unique_key("email")
            .sql()
        )
        assert "UNIQUE" in sql

    def test_if_not_exists(self) -> None:
        """Test IF NOT EXISTS."""
        sql = create_postgres().name("users").column("id", "INT").if_not_exists().sql()
        assert "IF NOT EXISTS" in sql

    def test_temporary(self) -> None:
        """Test TEMPORARY table."""
        sql = create_postgres().name("temp_data").column("id", "INT").temporary().sql()
        assert "TEMPORARY" in sql

    def test_comment(self) -> None:
        """Test COMMENT (MySQL dialect supports table comments)."""
        from ddlglot import create

        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .comment("User table")
            .sql(dialect="mysql")
        )
        assert "COMMENT" in sql

    def test_fluent_chaining(self) -> None:
        """Test fluent method chaining."""
        builder = create_postgres().name("test").column("id", "INT")
        assert isinstance(builder, PostgresBuilder)

    def test_to_ast(self) -> None:
        """Test to_ast returns exp.Create."""
        ast = create_postgres().name("users").column("id", "INT").to_ast()
        assert isinstance(ast, exp.Create)

    def test_pretty_print(self) -> None:
        """Test pretty printing."""
        sql = (
            create_postgres()
            .name("users")
            .columns(("id", "INT"), ("name", "VARCHAR(100)"))
            .sql(pretty=True)
        )
        assert "\n" in sql
