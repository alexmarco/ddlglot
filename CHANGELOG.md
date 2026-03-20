# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [26.4.0](https://github.com/alexmarco/ddlglot/compare/v26.3.2...v26.4.0) (2026-03-21)


### Features

* **ci:** add release-please and commitlint for automated versioning ([5fb6b81](https://github.com/alexmarco/ddlglot/commit/5fb6b8136da4cc9898783f3db3cfbbf8a8dbdf11))
* **ci:** add release-please and commitlint for automated versioning ([b8f3db1](https://github.com/alexmarco/ddlglot/commit/b8f3db16c430d7b9c3684a82adcf89d8e3739b31))


### Bug Fixes

* **docs:** remove tag trigger to avoid environment protection rules ([cb26ded](https://github.com/alexmarco/ddlglot/commit/cb26dedc10ac526b361403b86444770b2c62ae73))

## [26.3.2] - 2026-03-21

### Added

- `.sql()` now accepts `indent`, `pad`, and `max_text_width` parameters for fine-grained pretty printing control

## [26.3.1] - 2026-03-21

### Fixed

- CREATE TABLE now produces correct SQL without spurious `AS` clause

## [26.3.0] - 2026-03-20

### Added

- Core builder with fluent API for DDL generation
- Support for multiple SQL dialects:
  - Spark+Delta Lake with CDF support
  - Apache Hive with SERDE/ROW FORMAT
  - PostgreSQL
  - DuckDB
  - BigQuery
- Plugin registry system for custom variants
- Dialect-specific validation
- Comprehensive test suite (92 tests)
- GitHub Actions CI/CD
- Sphinx documentation
- Pre-commit hooks

### Features

- `create()` factory function for generic DDL
- `create_spark_delta()`, `create_hive()`, etc. for dialect-specific DDL
- Fluent method chaining for all DDL operations
- Type hints and validation
- SQLGlot-powered AST generation
