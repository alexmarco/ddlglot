# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0](https://github.com/alexmarco/ddlglot/compare/v0.1.0...v0.2.0) (2026-03-22)


### Features

* **docs:** add dialects reference page ([20ef8d3](https://github.com/alexmarco/ddlglot/commit/20ef8d370931ea3091c5f078975416fe6b7d0a7a))


### Bug Fixes

* **docs:** add sphinx-autoapi to docs dependencies ([19667f8](https://github.com/alexmarco/ddlglot/commit/19667f8ff5633447bc4c8dbe2d56975e95f848f8))
* **docs:** add sphinx-autoapi to docs dependencies ([f248ac0](https://github.com/alexmarco/ddlglot/commit/f248ac05de80f972d7ce131f68d9ce0637f1f0c2))
* **docs:** convert markdown alerts to RST directives in dialects.rst ([981beaa](https://github.com/alexmarco/ddlglot/commit/981beaa8e6aa160e90a51b9a7df5fb9df2dc74ee))
* **docs:** use list-table directive for dialects.rst tables ([951cfec](https://github.com/alexmarco/ddlglot/commit/951cfecf09bd434ed979290d35d332621f222411))
* **docs:** use RST simple table syntax in dialects.rst ([f3a8915](https://github.com/alexmarco/ddlglot/commit/f3a891587c88acb486f27125bb86d7177c76cf2d))


### Documentation

* **agents:** add documentation section with Sphinx guidelines ([12f5122](https://github.com/alexmarco/ddlglot/commit/12f512285278b3201c4b6467d3e9c6fdbaad2395))
* **agents:** expand Git Workflow section with step-by-step instructions ([5ae3605](https://github.com/alexmarco/ddlglot/commit/5ae3605f51fb3615be5a893da56a29405684ada7))
* **agents:** expand Git Workflow section with step-by-step instructions ([fed1ac7](https://github.com/alexmarco/ddlglot/commit/fed1ac7bd79488ba17282d30ef019c483528b4a3))
* **api:** use sphinx-autoapi for automatic API reference generation ([9624dde](https://github.com/alexmarco/ddlglot/commit/9624dde5fdaae972562a4e70be6daa0a8f00f0f0))
* **core_builder:** rewrite with method classification table and detailed flow ([9ba2c26](https://github.com/alexmarco/ddlglot/commit/9ba2c266511dac35495bca1ec9f9a7f2e5f2ccdc))
* update AGENTS.md to reflect current project state ([ddd9d64](https://github.com/alexmarco/ddlglot/commit/ddd9d6417d2ee4612dc7a17813c2caf38f9ee6a0))

## 0.1.0 (2026-03-21)


### Features

* initial commit with ddlglot v0.1.0 ([2d1eeff](https://github.com/alexmarco/ddlglot/commit/2d1eeffe16ffcbaf31bb1df5783ed40038a18b5b))


### Bug Fixes

* **ci:** use sha for publish checkout instead of tag ([605a168](https://github.com/alexmarco/ddlglot/commit/605a168f83ecfcaa944d9026ff58eef6f3efc3f3))

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
