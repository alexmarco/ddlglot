"""Tests for core CreateBuilder."""

from __future__ import annotations

from typing import NamedTuple

import pytest
from sqlglot import expressions as exp

from ddlglot import create
from ddlglot.builder import CreateBuilder
from ddlglot.exceptions import ASTBuildError


class DialectCase(NamedTuple):
    """Test case with dialect and expected SQL."""

    dialect: str
    expected: str


COMMON_DIALECTS = ["postgres", "spark", "bigquery", "duckdb", "sqlite", "hive"]


class TestCreateTable:
    """Tests for CREATE TABLE statements."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE users (id INT NOT NULL, name VARCHAR(100))",
            ),
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE users (id INT NOT NULL, name VARCHAR(100))",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE users (id INT64 NOT NULL, name STRING(100))",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE TABLE users (id INT NOT NULL, name TEXT(100))",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE users (id INTEGER NOT NULL, name TEXT(100))",
            ),
            DialectCase(
                dialect="hive",
                expected="CREATE TABLE users (id INT NOT NULL, name VARCHAR(100))",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_basic_table(self, case: DialectCase) -> None:
        """Test basic CREATE TABLE across dialects."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    def test_table_with_qualified_name(self) -> None:
        """Test CREATE TABLE with schema-qualified name."""
        sql = (
            create("table")
            .name("public.users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres")
        )
        expected = "CREATE TABLE public.users (id INT NOT NULL, name VARCHAR(100))"
        assert sql == expected

    def test_table_with_bq_qualified_name(self) -> None:
        """Test CREATE TABLE with BigQuery fully-qualified name."""
        sql = (
            create("table")
            .name("project.dataset.users")
            .column("id", "INT64")
            .column("name", "STRING")
            .sql(dialect="bigquery")
        )
        expected = "CREATE TABLE project.dataset.users (id INT64, name STRING)"
        assert sql == expected

    def test_table_with_pk_inline_constraint(self) -> None:
        """Test CREATE TABLE with inline PRIMARY KEY constraint."""
        sql = (
            create("table")
            .name("t_facts")
            .column("key1", "INTEGER", pk=True, not_null=True)
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres")
        )
        expected = "CREATE TABLE t_facts (key1 INT NOT NULL PRIMARY KEY (), name VARCHAR(100))"
        assert sql == expected

    def test_table_with_defaults(self) -> None:
        """Test CREATE TABLE with DEFAULT values."""
        sql = (
            create("table")
            .name("products")
            .column("id", "INT")
            .column("price", "DECIMAL(10,2)", default=0)
            .column("active", "BOOLEAN", default=True)
            .sql(dialect="postgres")
        )
        expected = "CREATE TABLE products (id INT, price DECIMAL(10, 2) DEFAULT 0, active BOOLEAN DEFAULT TRUE)"
        assert sql == expected

    def test_table_with_multiple_columns(self) -> None:
        """Test CREATE TABLE with multiple columns via .columns()."""
        sql = (
            create("table")
            .name("orders")
            .columns(
                ("id", "INT"),
                ("amount", "DECIMAL(12,2)"),
                ("created_at", "TIMESTAMP"),
            )
            .sql(dialect="postgres")
        )
        expected = "CREATE TABLE orders (id INT, amount DECIMAL(12, 2), created_at TIMESTAMP)"
        assert sql == expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE IF NOT EXISTS users (id INT)",
            ),
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE IF NOT EXISTS users (id INT)",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE IF NOT EXISTS users (id INT64)",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE TABLE IF NOT EXISTS users (id INT)",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE IF NOT EXISTS users (id INTEGER)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_table_if_not_exists(self, case: DialectCase) -> None:
        """Test CREATE TABLE IF NOT EXISTS across dialects."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .if_not_exists()
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    def test_table_temporary(self) -> None:
        """Test CREATE TEMPORARY TABLE."""
        sql = (
            create("table")
            .name("temp_data")
            .column("id", "INT")
            .temporary()
            .sql(dialect="postgres")
        )
        expected = "CREATE TEMPORARY TABLE temp_data (id INT)"
        assert sql == expected

    def test_table_with_comment(self) -> None:
        """Test CREATE TABLE with COMMENT."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .comment("User information table")
            .sql(dialect="mysql")
        )
        expected = "CREATE TABLE users (id INT) COMMENT='User information table'"
        assert sql == expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE order_items (order_id INT, product_id INT, PRIMARY KEY (order_id, product_id))",
            ),
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE order_items (order_id INT, product_id INT, PRIMARY KEY (order_id, product_id))",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE order_items (order_id INT64, product_id INT64, PRIMARY KEY (order_id, product_id))",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE TABLE order_items (order_id INT, product_id INT, PRIMARY KEY (order_id, product_id))",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE order_items (order_id INTEGER, product_id INTEGER, PRIMARY KEY (order_id, product_id))",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_table_with_table_level_pk(self, case: DialectCase) -> None:
        """Test CREATE TABLE with table-level PRIMARY KEY constraint."""
        sql = (
            create("table")
            .name("order_items")
            .column("order_id", "INT")
            .column("product_id", "INT")
            .primary_key("order_id", "product_id")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE users (email VARCHAR(100), UNIQUE (email))",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE users (email STRING(100), UNIQUE (email))",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE TABLE users (email TEXT(100), UNIQUE (email))",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE users (email TEXT(100), UNIQUE (email))",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_table_with_unique_constraint(self, case: DialectCase) -> None:
        """Test CREATE TABLE with UNIQUE constraint."""
        sql = (
            create("table")
            .name("users")
            .column("email", "VARCHAR(100)")
            .unique_key("email")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected


class TestCreateView:
    """Tests for CREATE VIEW statements."""

    def test_create_view(self) -> None:
        """Test basic CREATE VIEW."""
        sql = (
            create("view")
            .name("active_users")
            .as_select(exp.select("*").from_("users").where("active = true"))
            .sql(dialect="postgres")
        )
        expected = "CREATE VIEW active_users AS SELECT * FROM users WHERE active = TRUE"
        assert sql == expected


class TestProperties:
    """Tests for DDL properties."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE events (id INT) USING DELTA",
            ),
            DialectCase(
                dialect="hive",
                expected="CREATE TABLE events (id INT) STORED AS DELTA",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_using_delta(self, case: DialectCase) -> None:
        """Test USING DELTA translates to STORED AS DELTA in Hive."""
        sql = (
            create("table")
            .name("events")
            .column("id", "INT")
            .using("delta")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE data (id INT) USING PARQUET",
            ),
            DialectCase(
                dialect="hive",
                expected="CREATE TABLE data (id INT) STORED AS PARQUET",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_using_parquet(self, case: DialectCase) -> None:
        """Test USING PARQUET translates to STORED AS PARQUET in Hive."""
        sql = (
            create("table")
            .name("data")
            .column("id", "INT")
            .using("parquet")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE events (id INT, event_date DATE) PARTITIONED BY (event_date)",
            ),
            DialectCase(
                dialect="hive",
                expected="CREATE TABLE events (id INT, event_date DATE) PARTITIONED BY (event_date)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_partitioned_by(self, case: DialectCase) -> None:
        """Test PARTITIONED BY across dialects."""
        sql = (
            create("table")
            .name("events")
            .column("id", "INT")
            .column("event_date", "DATE")
            .partitioned_by("event_date")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE external_data (id INT) LOCATION 's3://bucket/path/'",
            ),
            DialectCase(
                dialect="hive",
                expected="CREATE TABLE external_data (id INT) LOCATION '/user/hive/warehouse/data'",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_location(self, case: DialectCase) -> None:
        """Test LOCATION across different file-based dialects."""
        path = "s3://bucket/path/" if case.dialect == "spark" else "/user/hive/warehouse/data"
        sql = (
            create("table")
            .name("external_data")
            .column("id", "INT")
            .location(path)
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE data (id INT) TBLPROPERTIES ('delta.enableChangeDataFeed'=TRUE)",
            ),
            DialectCase(
                dialect="hive",
                expected="CREATE TABLE data (id INT) TBLPROPERTIES ('delta.enableChangeDataFeed'=TRUE)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_tblproperties_delta(self, case: DialectCase) -> None:
        """Test TBLPROPERTIES with Delta properties."""
        sql = (
            create("table")
            .name("data")
            .column("id", "INT")
            .tblproperties({"delta.enableChangeDataFeed": True})
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected


class TestDialectTranslation:
    """Tests for dialect-specific type translation."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE users (id INT)",
            ),
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE users (id INT)",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE users (id INT64)",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE TABLE users (id INT)",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE users (id INTEGER)",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_int_translation(self, case: DialectCase) -> None:
        """Test INT type translation across dialects."""
        sql = create("table").name("users").column("id", "INT").sql(dialect=case.dialect)
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE users (name VARCHAR(100))",
            ),
            DialectCase(
                dialect="spark",
                expected="CREATE TABLE users (name VARCHAR(100))",
            ),
            DialectCase(
                dialect="bigquery",
                expected="CREATE TABLE users (name STRING(100))",
            ),
            DialectCase(
                dialect="duckdb",
                expected="CREATE TABLE users (name TEXT(100))",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE users (name TEXT(100))",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_varchar_translation(self, case: DialectCase) -> None:
        """Test VARCHAR type translation across dialects."""
        sql = create("table").name("users").column("name", "VARCHAR(100)").sql(dialect=case.dialect)
        assert sql == case.expected


class TestPrettyPrint:
    """Tests for pretty printing."""

    def test_pretty_print_basic(self) -> None:
        """Test basic pretty printing."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .column("name", "VARCHAR(100)")
            .sql(dialect="postgres", pretty=True)
        )
        expected = "CREATE TABLE users (\n  id INT,\n  name VARCHAR(100)\n)"
        assert sql == expected

    def test_pretty_print_with_indent(self) -> None:
        """Test pretty printing with custom indent (base indentation unchanged)."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .sql(dialect="postgres", pretty=True, indent=4)
        )
        expected = "CREATE TABLE users (\n  id INT\n)"
        assert sql == expected

    def test_pretty_print_with_pad(self) -> None:
        """Test pretty printing with custom pad."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT")
            .sql(dialect="postgres", pretty=True, pad=4)
        )
        expected = "CREATE TABLE users (\n    id INT\n)"
        assert sql == expected

    def test_pretty_print_with_max_text_width(self) -> None:
        """Test pretty printing respects max_text_width."""
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

    def test_method_chaining_returns_builder(self) -> None:
        """Test that methods return self for chaining."""
        builder = create("table").name("test").column("id", "INT")
        assert isinstance(builder, CreateBuilder)

    def test_full_fluent_chain(self) -> None:
        """Test complete fluent chain produces correct SQL."""
        sql = (
            create("table")
            .name("users")
            .column("id", "INT", not_null=True)
            .column("email", "VARCHAR(255)")
            .column("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP")
            .primary_key("id")
            .unique_key("email")
            .if_not_exists()
            .sql(dialect="postgres")
        )
        expected = (
            "CREATE TABLE IF NOT EXISTS users ("
            "id INT NOT NULL, "
            "email VARCHAR(255), "
            "created_at TIMESTAMP DEFAULT 'CURRENT_TIMESTAMP', "
            "PRIMARY KEY (id), "
            "UNIQUE (email)"
            ")"
        )
        assert sql == expected


class TestEdgeCases:
    """Tests for edge cases."""

    def test_missing_name_raises_error(self) -> None:
        """Test that missing .name() raises ASTBuildError."""
        with pytest.raises(ASTBuildError):
            create("table").column("id", "INT").to_ast()

    def test_to_ast_returns_exp_create(self) -> None:
        """Test that to_ast() returns exp.Create."""
        ast = create("table").name("users").column("id", "INT").to_ast()
        assert isinstance(ast, exp.Create)

    def test_empty_columns(self) -> None:
        """Test CREATE TABLE with no columns."""
        sql = create("table").name("empty_table").sql(dialect="postgres")
        expected = "CREATE TABLE empty_table"
        assert sql == expected
