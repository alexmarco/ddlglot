"""Tests for Hive variant."""

from __future__ import annotations

from sqlglot import expressions as exp

from ddlglot.variants.hive import HiveBuilder, create_hive


class TestHiveBuilder:
    """Tests for Hive builder."""

    def test_create_hive_table_basic(self) -> None:
        """Test basic Hive table creation."""
        sql = create_hive().name("default.events").columns(("id", "INT"), ("name", "STRING")).sql()
        assert "CREATE TABLE" in sql
        assert "default.events" in sql

    def test_stored_as_parquet(self) -> None:
        """Test STORED AS PARQUET."""
        sql = create_hive().name("default.events").column("id", "INT").stored_as("PARQUET").sql()
        assert "STORED AS PARQUET" in sql

    def test_stored_as_orc(self) -> None:
        """Test STORED AS ORC."""
        sql = create_hive().name("default.events").column("id", "INT").stored_as("ORC").sql()
        assert "STORED AS ORC" in sql

    def test_row_format_delimited(self) -> None:
        """Test ROW FORMAT DELIMITED."""
        sql = create_hive().name("default.events").column("id", "INT").row_format("DELIMITED").sql()
        assert "ROW FORMAT DELIMITED" in sql

    def test_row_format_serde(self) -> None:
        """Test ROW FORMAT SERDE."""
        sql = (
            create_hive()
            .name("default.events")
            .column("id", "INT")
            .row_format("SERDE", serde="org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe")
            .sql()
        )
        assert "ROW FORMAT SERDE" in sql

    def test_partitioned_by(self) -> None:
        """Test PARTITIONED BY."""
        sql = (
            create_hive()
            .name("default.events")
            .columns(("id", "INT"), ("event_date", "STRING"))
            .partitioned_by("event_date")
            .sql()
        )
        assert "PARTITIONED BY" in sql

    def test_location(self) -> None:
        """Test LOCATION."""
        sql = (
            create_hive()
            .name("default.events")
            .column("id", "INT")
            .location("/warehouse/events")
            .sql()
        )
        assert "LOCATION" in sql
        assert "/warehouse/events" in sql

    def test_tblproperties(self) -> None:
        """Test TBLPROPERTIES."""
        sql = (
            create_hive()
            .name("default.events")
            .column("id", "INT")
            .tblproperties({"serialization.null.format": "\\N"})
            .sql()
        )
        assert "TBLPROPERTIES" in sql

    def test_combined_hive_properties(self) -> None:
        """Test combining multiple Hive properties."""
        sql = (
            create_hive()
            .name("default.events")
            .columns(("id", "INT"), ("event_date", "STRING"))
            .partitioned_by("event_date")
            .stored_as("PARQUET")
            .location("/warehouse/events")
            .sql()
        )
        assert "PARTITIONED BY" in sql
        assert "STORED AS PARQUET" in sql
        assert "LOCATION" in sql

    def test_if_not_exists(self) -> None:
        """Test IF NOT EXISTS."""
        sql = create_hive().name("default.events").column("id", "INT").if_not_exists().sql()
        assert "IF NOT EXISTS" in sql

    def test_fluent_chaining(self) -> None:
        """Test fluent method chaining."""
        builder = create_hive().name("test").column("id", "INT")
        assert isinstance(builder, HiveBuilder)

    def test_to_ast(self) -> None:
        """Test to_ast returns exp.Create."""
        ast = create_hive().name("default.events").column("id", "INT").to_ast()
        assert isinstance(ast, exp.Create)
