"""Tests for plugin registry."""

from __future__ import annotations

import pytest

from ddlglot.registry import (
    _get_registry,
    create_variant,
    get_variant,
    is_registered,
    list_variants,
    register_variant,
)
from ddlglot.variants import (
    BigQueryBuilder,
    DuckDBBuilder,
    HiveBuilder,
    PostgresBuilder,
    SparkDeltaBuilder,
)


class TestRegistry:
    """Tests for variant registry."""

    def test_register_variant_decorator(self) -> None:
        """Test registering a variant with decorator."""

        @register_variant("custom")
        class MyBuilder:
            pass

        try:
            assert is_registered("custom")
            assert get_variant("custom") is MyBuilder
        finally:
            _get_registry().pop("custom", None)

    def test_get_variant_not_registered(self) -> None:
        """Test that getting unregistered variant raises ValueError."""
        with pytest.raises(ValueError, match="not registered"):
            get_variant("nonexistent")

    def test_create_variant(self) -> None:
        """Test creating a variant instance."""

        @register_variant("test_builder")
        class TestBuilder:
            def __init__(self, kind: str) -> None:
                self.kind = kind

        try:
            builder = create_variant("test_builder")
            assert isinstance(builder, TestBuilder)
        finally:
            _get_registry().pop("test_builder", None)

    def test_create_variant_with_kind(self) -> None:
        """Test creating a variant with specific kind."""
        builder = create_variant("spark_delta", kind="VIEW")
        assert isinstance(builder, SparkDeltaBuilder)

    def test_list_variants(self) -> None:
        """Test listing registered variants."""

        @register_variant("variant1")
        class Variant1:
            pass

        @register_variant("variant2")
        class Variant2:
            pass

        try:
            variants = list_variants()
            assert "variant1" in variants
            assert "variant2" in variants
        finally:
            _get_registry().pop("variant1", None)
            _get_registry().pop("variant2", None)

    def test_is_registered(self) -> None:
        """Test checking if variant is registered."""

        @register_variant("my_variant")
        class MyVariant:
            pass

        try:
            assert is_registered("my_variant") is True
            assert is_registered("other_variant") is False
        finally:
            _get_registry().pop("my_variant", None)

    def test_duplicate_registration(self) -> None:
        """Test that registering same name twice overwrites."""

        @register_variant("dup")
        class First:
            pass

        @register_variant("dup")
        class Second:
            pass

        try:
            assert get_variant("dup") is Second
        finally:
            _get_registry().pop("dup", None)


class TestBuiltinVariants:
    """Tests for built-in registered variants."""

    def test_builtin_variants_registered(self) -> None:
        """Test that built-in variants are registered."""
        assert is_registered("spark_delta")
        assert is_registered("hive")
        assert is_registered("postgres")
        assert is_registered("duckdb")
        assert is_registered("bigquery")

    def test_get_builtin_variants(self) -> None:
        """Test getting built-in variant classes."""
        assert get_variant("spark_delta") is SparkDeltaBuilder
        assert get_variant("hive") is HiveBuilder
        assert get_variant("postgres") is PostgresBuilder
        assert get_variant("duckdb") is DuckDBBuilder
        assert get_variant("bigquery") is BigQueryBuilder

    def test_create_builtin_variants(self) -> None:
        """Test creating instances of built-in variants."""
        spark = create_variant("spark_delta")
        assert isinstance(spark, SparkDeltaBuilder)

        hive = create_variant("hive")
        assert isinstance(hive, HiveBuilder)

        pg = create_variant("postgres")
        assert isinstance(pg, PostgresBuilder)

        duckdb = create_variant("duckdb")
        assert isinstance(duckdb, DuckDBBuilder)

        bq = create_variant("bigquery")
        assert isinstance(bq, BigQueryBuilder)

    def test_list_builtin_variants(self) -> None:
        """Test that built-in variants are in list."""
        variants = list_variants()
        assert "spark_delta" in variants
        assert "hive" in variants
        assert "postgres" in variants
        assert "duckdb" in variants
        assert "bigquery" in variants
