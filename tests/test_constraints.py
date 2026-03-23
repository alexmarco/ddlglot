"""Tests for foreign_key() and check() constraints."""

from __future__ import annotations

from typing import NamedTuple

import pytest

from ddlglot import create


class DialectCase(NamedTuple):
    """Test case with dialect and expected SQL."""

    dialect: str
    expected: str


class TestForeignKeyConstraint:
    """Tests for foreign_key() in CREATE TABLE."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=(
                    "CREATE TABLE orders (user_id INT, FOREIGN KEY (user_id) REFERENCES users (id))"
                ),
            ),
            DialectCase(
                dialect="mysql",
                expected=(
                    "CREATE TABLE orders (user_id INT, FOREIGN KEY (user_id) REFERENCES users (id))"
                ),
            ),
            DialectCase(
                dialect="sqlite",
                expected=(
                    "CREATE TABLE orders ("
                    "user_id INTEGER, "
                    "FOREIGN KEY (user_id) REFERENCES users (id)"
                    ")"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_single_column_fk(self, case: DialectCase) -> None:
        """Test single-column foreign key."""
        sql = (
            create("table")
            .name("orders")
            .column("user_id", "INT")
            .foreign_key("user_id", references=("users", ("id",)))
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=(
                    "CREATE TABLE order_items ("
                    "order_id INT, "
                    "product_id INT, "
                    "FOREIGN KEY (order_id, product_id) REFERENCES order_products (order_id, product_id)"
                    ")"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_composite_fk(self, case: DialectCase) -> None:
        """Test composite foreign key."""
        sql = (
            create("table")
            .name("order_items")
            .column("order_id", "INT")
            .column("product_id", "INT")
            .foreign_key(
                "order_id", "product_id", references=("order_products", ("order_id", "product_id"))
            )
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=(
                    "CREATE TABLE orders ("
                    "user_id INT, "
                    "CONSTRAINT fk_orders_users FOREIGN KEY (user_id) REFERENCES users (id) "
                    "ON DELETE CASCADE ON UPDATE SET NULL"
                    ")"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_fk_with_actions_and_name(self, case: DialectCase) -> None:
        """Test FK with ON DELETE/UPDATE actions and named constraint."""
        sql = (
            create("table")
            .name("orders")
            .column("user_id", "INT")
            .foreign_key(
                "user_id",
                references=("users", ("id",)),
                on_delete="CASCADE",
                on_update="SET NULL",
                name="fk_orders_users",
            )
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    def test_fk_inspection(self) -> None:
        """Test foreign key inspection from builder."""
        builder = (
            create("table")
            .name("orders")
            .column("user_id", "INT")
            .foreign_key("user_id", references=("users", ("id",)), on_delete="CASCADE")
        )
        fks = builder.foreign_keys
        assert len(fks) == 1
        assert fks[0].columns == ("user_id",)
        assert fks[0].referenced_table == "users"
        assert fks[0].referenced_columns == ("id",)
        assert fks[0].on_delete == "CASCADE"

    def test_fk_ddl_inspection(self) -> None:
        """Test foreign key inspection from DDL."""
        ddl = (
            create("table")
            .name("orders")
            .column("user_id", "INT")
            .foreign_key("user_id", references=("users", ("id",)), on_delete="CASCADE")
            .build()
        )
        fks = ddl.foreign_keys
        assert len(fks) == 1
        assert fks[0].columns == ("user_id",)
        assert fks[0].referenced_table == "users"


class TestCheckConstraint:
    """Tests for check() in CREATE TABLE."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected="CREATE TABLE products (price DECIMAL(10, 2), CHECK (price > 0))",
            ),
            DialectCase(
                dialect="sqlite",
                expected="CREATE TABLE products (price REAL(10, 2), CHECK (price > 0))",
            ),
            DialectCase(
                dialect="mysql",
                expected="CREATE TABLE products (price DECIMAL(10, 2), CHECK (price > 0))",
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_check_simple(self, case: DialectCase) -> None:
        """Test simple CHECK constraint."""
        sql = (
            create("table")
            .name("products")
            .column("price", "DECIMAL(10,2)")
            .check("price > 0")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=(
                    "CREATE TABLE products ("
                    "price DECIMAL(10, 2), "
                    "CONSTRAINT chk_positive_price CHECK (price > 0)"
                    ")"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_check_named(self, case: DialectCase) -> None:
        """Test named CHECK constraint."""
        sql = (
            create("table")
            .name("products")
            .column("price", "DECIMAL(10,2)")
            .check("price > 0", name="chk_positive_price")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=(
                    "CREATE TABLE employees ("
                    "salary DECIMAL(10, 2), "
                    "CHECK (salary > 0 AND salary < 1000000)"
                    ")"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_check_complex_condition(self, case: DialectCase) -> None:
        """Test CHECK with complex AND condition."""
        sql = (
            create("table")
            .name("employees")
            .column("salary", "DECIMAL(10,2)")
            .check("salary > 0 AND salary < 1000000")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="spark",
                expected=(
                    "CREATE TABLE products (price DECIMAL(10, 2)) "
                    "USING DELTA TBLPROPERTIES ('delta.constraints.check'='price > 0')"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_check_spark_via_tblproperties(self, case: DialectCase) -> None:
        """Test CHECK constraint on Spark via TBLPROPERTIES."""
        sql = (
            create("table")
            .name("products")
            .column("price", "DECIMAL(10,2)")
            .using("delta")
            .check("price > 0")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected

    def test_check_inspection(self) -> None:
        """Test CHECK constraint inspection from builder."""
        builder = (
            create("table")
            .name("products")
            .column("price", "INT")
            .check("price > 0", name="chk_price")
        )
        checks = builder.checks
        assert len(checks) == 1
        assert checks[0].condition == "price > 0"
        assert checks[0].name == "chk_price"

    def test_check_ddl_inspection(self) -> None:
        """Test CHECK constraint inspection from DDL."""
        ddl = create("table").name("products").column("price", "INT").check("price > 0").build()
        checks = ddl.checks
        assert len(checks) == 1
        assert checks[0].condition == "price > 0"


class TestUniqueKeyNamed:
    """Tests for unique_key() with named constraint."""

    @pytest.mark.parametrize(
        "case",
        [
            DialectCase(
                dialect="postgres",
                expected=(
                    "CREATE TABLE users ("
                    "email VARCHAR(100), "
                    "CONSTRAINT uq_users_email UNIQUE (email)"
                    ")"
                ),
            ),
            DialectCase(
                dialect="sqlite",
                expected=(
                    "CREATE TABLE users (email TEXT(100), CONSTRAINT uq_users_email UNIQUE (email))"
                ),
            ),
        ],
        ids=lambda c: c.dialect,
    )
    def test_unique_key_named(self, case: DialectCase) -> None:
        """Test named UNIQUE constraint."""
        sql = (
            create("table")
            .name("users")
            .column("email", "VARCHAR(100)")
            .unique_key("email", name="uq_users_email")
            .sql(dialect=case.dialect)
        )
        assert sql == case.expected
