"""Tests for DDL inspection (build() and properties)."""

from __future__ import annotations

from typing import NamedTuple

import pytest

from ddlglot import DDL, UniqueDef, create


class DialectCase(NamedTuple):
    """Test case with dialect and expected SQL."""

    dialect: str
    expected: str


class TestBuildMethod:
    """Tests for .build() method."""

    def test_build_returns_ddl(self) -> None:
        """Test that .build() returns a DDL object."""
        ddl = create("table").name("users").column("id", "INT").build()
        assert isinstance(ddl, DDL)

    def test_build_kind(self) -> None:
        """Test that DDL.kind is set correctly."""
        assert create("table").name("t").build().kind == "TABLE"
        assert create("view").name("t").build().kind == "VIEW"

    def test_build_table_name(self) -> None:
        """Test that DDL.table_name is set correctly."""
        assert create("table").name("users").build().table_name == "users"
        assert create("table").name("schema.users").build().table_name == "schema.users"

    def test_build_columns(self) -> None:
        """Test that DDL.columns is set correctly."""
        ddl = (
            create("table").name("users").column("id", "INT").column("name", "VARCHAR(100)").build()
        )
        assert len(ddl.columns) == 2
        assert ddl.columns[0].name == "id"
        assert ddl.columns[0].dtype == "INT"
        assert ddl.columns[1].name == "name"
        assert ddl.columns[1].dtype == "VARCHAR(100)"

    def test_build_column_not_null(self) -> None:
        """Test that column not_null constraint is captured."""
        ddl = create("table").name("t").column("id", "INT", not_null=True).build()
        assert ddl.columns[0].not_null is True

    def test_build_column_pk(self) -> None:
        """Test that column pk constraint is captured."""
        ddl = create("table").name("t").column("id", "INT", pk=True).build()
        assert ddl.columns[0].pk is True

    def test_build_column_unique(self) -> None:
        """Test that column unique constraint is captured."""
        ddl = create("table").name("t").column("email", "VARCHAR(100)", unique=True).build()
        assert ddl.columns[0].unique is True

    def test_build_column_default(self) -> None:
        """Test that column default value is captured."""
        ddl = (
            create("table")
            .name("t")
            .column("active", "BOOLEAN", default=True)
            .column("score", "INT", default=0)
            .build()
        )
        assert ddl.columns[0].default is True
        assert ddl.columns[1].default == 0

    def test_build_primary_keys(self) -> None:
        """Test that primary key columns are captured."""
        ddl = (
            create("table")
            .name("t")
            .column("id", "INT")
            .column("name", "TEXT")
            .primary_key("id")
            .build()
        )
        assert ddl.primary_keys == ("id",)

    def test_build_composite_primary_key(self) -> None:
        """Test that composite primary key is captured."""
        ddl = (
            create("table")
            .name("t")
            .column("id", "INT")
            .column("tenant_id", "INT")
            .primary_key("id", "tenant_id")
            .build()
        )
        assert ddl.primary_keys == ("id", "tenant_id")

    def test_build_unique_keys(self) -> None:
        """Test that unique constraint columns are captured as grouped tuple."""
        ddl = (
            create("table")
            .name("t")
            .column("id", "INT")
            .column("email", "VARCHAR(100)")
            .column("phone", "VARCHAR(20)")
            .unique_key("email", "phone")
            .build()
        )
        assert ddl.unique_keys == (UniqueDef(columns=("email", "phone")),)

    def test_build_if_not_exists(self) -> None:
        """Test that if_not_exists flag is captured."""
        ddl = create("table").name("t").if_not_exists().build()
        assert ddl.if_not_exists is True
        ddl = create("table").name("t").build()
        assert ddl.if_not_exists is False

    def test_build_temporary(self) -> None:
        """Test that temporary flag is captured."""
        ddl = create("table").name("t").temporary().build()
        assert ddl.temporary is True

    def test_build_comment(self) -> None:
        """Test that table comment is captured."""
        ddl = create("table").name("t").comment("Test table").build()
        assert ddl.comment == "Test table"

    def test_build_partition_cols(self) -> None:
        """Test that partition columns are captured."""
        ddl = (
            create("table")
            .name("events")
            .column("id", "INT")
            .column("created_at", "TIMESTAMP")
            .partitioned_by("created_at", "id")
            .build()
        )
        assert ddl.partition_cols == ("created_at", "id")

    def test_build_location(self) -> None:
        """Test that location is captured."""
        ddl = create("table").name("t").location("s3://warehouse/data/").build()
        assert ddl.location == "s3://warehouse/data/"

    def test_build_file_format(self) -> None:
        """Test that file format is captured."""
        ddl = create("table").name("t").using("delta").build()
        assert ddl.file_format == "DELTA"
        ddl = create("table").name("t").using("parquet").build()
        assert ddl.file_format == "PARQUET"

    def test_build_tblproperties(self) -> None:
        """Test that table properties are captured."""
        ddl = create("table").name("t").tblproperties({"delta.autoOptimize": "true"}).build()
        assert ddl.tblproperties == {"delta.autoOptimize": "true"}

    def test_build_empty_columns(self) -> None:
        """Test that empty columns tuple is returned."""
        ddl = create("table").name("t").build()
        assert ddl.columns == ()


class TestDDLSql:
    """Tests for DDL.sql() method."""

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
        ],
        ids=lambda c: c.dialect,
    )
    def test_ddl_sql(self, case: DialectCase) -> None:
        """Test that DDL.sql() generates correct SQL."""
        ddl = (
            create("table")
            .name("users")
            .column("id", "INT", not_null=True)
            .column("name", "VARCHAR(100)")
            .build()
        )
        assert ddl.sql(dialect=case.dialect) == case.expected


class TestDDLToAst:
    """Tests for DDL.to_ast() method."""

    def test_ddl_to_ast_returns_exp_create(self) -> None:
        """Test that DDL.to_ast() returns exp.Create."""
        from sqlglot import expressions as exp

        ddl = create("table").name("t").column("id", "INT").build()
        ast = ddl.to_ast()
        assert isinstance(ast, exp.Create)


class TestBuilderProperties:
    """Tests for builder inspection properties."""

    def test_table_name_property(self) -> None:
        """Test table_name property."""
        builder = create("table").name("users")
        assert builder.table_name == "users"

    def test_columns_defs_property(self) -> None:
        """Test columns_defs property."""
        builder = create("table").name("t").column("id", "INT", pk=True).column("name", "TEXT")
        cols = builder.columns_defs
        assert len(cols) == 2
        assert cols[0].name == "id"
        assert cols[0].pk is True
        assert cols[1].name == "name"

    def test_primary_keys_property(self) -> None:
        """Test primary_keys property."""
        builder = create("table").name("t").column("id", "INT").primary_key("id")
        assert builder.primary_keys == ("id",)

    def test_unique_keys_property(self) -> None:
        """Test unique_keys property."""
        builder = create("table").name("t").unique_key("email", "phone")
        assert builder.unique_keys == (UniqueDef(columns=("email", "phone")),)

    def test_partition_columns_property(self) -> None:
        """Test partition_columns property."""
        builder = create("table").name("t").column("id", "INT").partitioned_by("id")
        assert builder.partition_columns == ("id",)


class TestDDLImmutability:
    """Tests for DDL immutability."""

    def test_ddl_is_frozen(self) -> None:
        """Test that DDL is a frozen dataclass."""
        ddl = create("table").name("t").build()
        with pytest.raises(AttributeError):
            ddl.table_name = "other"

    def test_column_def_is_frozen(self) -> None:
        """Test that ColumnDef is a frozen dataclass."""
        ddl = create("table").name("t").column("id", "INT").build()
        with pytest.raises(AttributeError):
            ddl.columns[0].name = "other"
