"""Tests for IndexBuilder and create_index()."""

from __future__ import annotations

from typing import NamedTuple

import pytest

from ddlglot import IndexDef, create_index


class DialectCase(NamedTuple):
    """Test case with dialect and expected SQL."""

    dialect: str
    expected: str


class TestCreateIndex:
    """Tests for CREATE INDEX statements."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE INDEX idx_users_email ON users(email)",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE INDEX idx_users_email ON users(email)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_basic_index(self, case: DialectCase) -> None:
        """Test basic CREATE INDEX on single column."""
        sql = create_index("idx_users_email").on("users", "email").sql(dialect=case.dialect)
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE INDEX idx_users_name ON users(first_name, last_name)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_composite_index(self, case: DialectCase) -> None:
        """Test CREATE INDEX on multiple columns."""
        sql = (
            create_index("idx_users_name")
            .on("users", "first_name", "last_name")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE INDEX UNIQUE idx_users_email ON users(email)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_unique_index(self, case: DialectCase) -> None:
        """Test CREATE UNIQUE INDEX."""
        sql = (
            create_index("idx_users_email").on("users", "email").unique().sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE INDEX idx_users_email ON users(email) WHERE active = TRUE",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_where_clause(self, case: DialectCase) -> None:
        """Test CREATE INDEX with WHERE clause (partial index)."""
        sql = (
            create_index("idx_users_email")
            .on("users", "email")
            .where("active = TRUE")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE INDEX idx_users_email ON users USING btree(email)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_using(self, case: DialectCase) -> None:
        """Test CREATE INDEX with USING."""
        sql = (
            create_index("idx_users_email")
            .on("users", "email")
            .using("btree")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=("CREATE INDEX idx_users_email ON users(email) INCLUDE (created_at)"),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_include(self, case: DialectCase) -> None:
        """Test CREATE INDEX with INCLUDE columns."""
        sql = (
            create_index("idx_users_email")
            .on("users", "email")
            .include("created_at")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected


class TestIndexBuilderInspection:
    """Tests for IndexBuilder inspection methods."""

    def test_index_def_basic(self) -> None:
        """Test IndexDef construction from builder."""
        builder = create_index("idx_users_email").on("users", "email")
        index_def = builder.build()
        assert isinstance(index_def, IndexDef)
        assert index_def.name == "idx_users_email"
        assert index_def.table == "users"
        assert index_def.columns == ("email",)
        assert index_def.unique is False

    def test_index_def_unique(self) -> None:
        """Test IndexDef with unique flag."""
        builder = create_index("idx_users_email").on("users", "email").unique()
        index_def = builder.build()
        assert index_def.unique is True

    def test_index_def_all_options(self) -> None:
        """Test IndexDef with all options set."""
        builder = (
            create_index("idx_users_active")
            .on("users", "email")
            .unique()
            .using("btree")
            .where("active = TRUE")
            .include("created_at")
            .comment("Index for active users")
        )
        index_def = builder.build()
        assert index_def.name == "idx_users_active"
        assert index_def.table == "users"
        assert index_def.columns == ("email",)
        assert index_def.unique is True
        assert index_def.using == "btree"
        assert index_def.where == "active = TRUE"
        assert index_def.include == ("created_at",)
        assert index_def.comment == "Index for active users"

    def test_index_def_rebuild(self) -> None:
        """Test that IndexDef.build() returns an equivalent builder."""
        original = create_index("idx_users_email").on("users", "email").unique()
        original_def = original.build()
        rebuilt_def = original_def.build().build()
        assert rebuilt_def.name == original_def.name
        assert rebuilt_def.table == original_def.table
        assert rebuilt_def.columns == original_def.columns
        assert rebuilt_def.unique == original_def.unique


class TestIndexBuilderFluent:
    """Tests for IndexBuilder fluent API chaining."""

    def test_method_chaining(self) -> None:
        """Test that builder methods return self for chaining."""
        builder = create_index("idx")
        assert builder.on("t", "c") is builder
        assert builder.unique() is builder
        assert builder.using("btree") is builder
        assert builder.where("x > 0") is builder
        assert builder.include("y") is builder
        assert builder.comment("test") is builder
