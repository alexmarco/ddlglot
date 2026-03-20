"""Tests for Spark+Delta variant."""

from __future__ import annotations

from sqlglot import expressions as exp

from ddlglot.variants.spark_delta import SparkDeltaBuilder, create_spark_delta


class TestSparkDeltaBuilder:
    """Tests for Spark+Delta builder."""

    def test_create_delta_table_basic(self) -> None:
        """Test basic Delta table creation."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .columns(("id", "INT"), ("name", "STRING"))
            .sql()
        )
        assert "CREATE TABLE" in sql
        assert "default.events" in sql
        assert "USING DELTA" in sql

    def test_delta_table_with_partition(self) -> None:
        """Test Delta table with partitioning."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .columns(("id", "INT"), ("event_date", "DATE"))
            .partitioned_by("event_date")
            .sql()
        )
        assert "USING DELTA" in sql
        assert "PARTITIONED BY" in sql

    def test_delta_table_with_location(self) -> None:
        """Test Delta table with location."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .column("id", "INT")
            .location("s3://bucket/path/")
            .sql()
        )
        assert "LOCATION" in sql
        assert "s3://bucket/path/" in sql

    def test_enable_cdf(self) -> None:
        """Test enable CDF helper."""
        sql = create_spark_delta().name("default.events").column("id", "INT").enable_cdf(True).sql()
        assert "delta.enableChangeDataFeed" in sql

    def test_append_only(self) -> None:
        """Test append_only helper."""
        sql = (
            create_spark_delta().name("default.events").column("id", "INT").append_only(True).sql()
        )
        assert "delta.appendOnly" in sql

    def test_log_retention(self) -> None:
        """Test log_retention helper."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .column("id", "INT")
            .log_retention("30 days")
            .sql()
        )
        assert "delta.logRetentionDuration" in sql

    def test_deleted_file_retention(self) -> None:
        """Test deleted_file_retention helper."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .column("id", "INT")
            .deleted_file_retention("7 days")
            .sql()
        )
        assert "delta.deletedFileRetentionDuration" in sql

    def test_generated_column(self) -> None:
        """Test generated column helper."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .columns(("id", "INT"), ("ts", "TIMESTAMP"))
            .generated_column("event_date", "DATE", "CAST(ts AS DATE)")
            .sql()
        )
        assert "GENERATED ALWAYS AS" in sql or "GENERATED AS" in sql

    def test_combined_delta_properties(self) -> None:
        """Test combining multiple Delta properties."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .columns(("id", "INT"), ("event_date", "DATE"))
            .generated_column("event_date", "DATE", "CAST(ts AS DATE)")
            .partitioned_by("event_date")
            .enable_cdf(True)
            .append_only(False)
            .log_retention("30 days")
            .deleted_file_retention("7 days")
            .sql()
        )
        assert "USING DELTA" in sql
        assert "delta.enableChangeDataFeed" in sql
        assert "delta.appendOnly" in sql

    def test_if_not_exists(self) -> None:
        """Test IF NOT EXISTS."""
        sql = create_spark_delta().name("default.events").column("id", "INT").if_not_exists().sql()
        assert "IF NOT EXISTS" in sql

    def test_pretty_print(self) -> None:
        """Test pretty printing."""
        sql = (
            create_spark_delta()
            .name("default.events")
            .columns(("id", "INT"), ("name", "STRING"))
            .sql(pretty=True)
        )
        assert "\n" in sql

    def test_fluent_chaining(self) -> None:
        """Test fluent method chaining."""
        builder = create_spark_delta().name("test").column("id", "INT")
        assert isinstance(builder, SparkDeltaBuilder)

    def test_to_ast(self) -> None:
        """Test to_ast returns exp.Create."""
        ast = create_spark_delta().name("default.events").column("id", "INT").to_ast()
        assert isinstance(ast, exp.Create)
