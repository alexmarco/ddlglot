# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0](https://github.com/alexmarco/ddlglot/compare/v0.3.0...v1.0.0) (2026-03-23)


### ⚠ BREAKING CHANGES

* **core:** unique_keys inspection now returns tuple[UniqueDef, ...] instead of tuple[tuple[str, ...], ...

### Features

* **core:** add foreign_key(), check() constraints and IndexBuilder ([#16](https://github.com/alexmarco/ddlglot/issues/16)) ([161ca65](https://github.com/alexmarco/ddlglot/commit/161ca653872de0516eff98977f10db0bb2705f1b))
* **docs:** add dual-mode logo for Sphinx documentation ([a6cc2f3](https://github.com/alexmarco/ddlglot/commit/a6cc2f3e3d87fd5a87de70dbb791251742cc6e33))
* **docs:** add logo title and custom fonts to Sphinx theme ([bd72ea7](https://github.com/alexmarco/ddlglot/commit/bd72ea73d5bf42e5bbd14623e42eefc606d48124))
* **docs:** add sphinx-copybutton for code block copy buttons ([e6363c5](https://github.com/alexmarco/ddlglot/commit/e6363c57517d462c2db8f459928f9d8b4f4f5f14))
* **docs:** increase logo size to 128px ([12675c6](https://github.com/alexmarco/ddlglot/commit/12675c64a717dc9755d62b1e686560211f3922a2))
* **docs:** show version badge in navbar using standard template approach ([87c3378](https://github.com/alexmarco/ddlglot/commit/87c33784e921d21b6a0c2b6cd4c8d852529e6e59))
* **docs:** show version below logo using logo.text option ([fb8d7dc](https://github.com/alexmarco/ddlglot/commit/fb8d7dc643bb1b5d9f7bea1c53951b76cba6f153))
* **docs:** unify logo to Designer (3) across docs and README ([b91c053](https://github.com/alexmarco/ddlglot/commit/b91c053b6d13898dfc43c282587ba1adba1c42b8))


### Bug Fixes

* **docs:** correct Mermaid syntax for GitHub rendering ([048cd2e](https://github.com/alexmarco/ddlglot/commit/048cd2e0cd20ee037855be96f4eb5ac999af306c))
* **readme:** update logo reference to renamed image ([66721e9](https://github.com/alexmarco/ddlglot/commit/66721e94baf7a7125fd68f6496fa527eb29c3412))


### Documentation

* add Mermaid diagrams to CICD_ARCHITECTURE.md ([be81f11](https://github.com/alexmarco/ddlglot/commit/be81f11406131942a8c04b952c2ea1e62a05ca04))
* rewrite README to reflect current API ([215f2e2](https://github.com/alexmarco/ddlglot/commit/215f2e2d014581b315265a82ad0a45075cbe1de9))

## [0.3.0](https://github.com/alexmarco/ddlglot/compare/v0.2.0...v0.3.0) (2026-03-23)


### Features

* **builder:** add DDL inspection with .build() method and public types ([ab3848c](https://github.com/alexmarco/ddlglot/commit/ab3848c9e210afdc83070a7ce4418cffcf95d511))
* **builder:** add DDL inspection with .build() method and public types ([a40e904](https://github.com/alexmarco/ddlglot/commit/a40e904173eb650c16e639206a9a33fd94728d4b))


### Bug Fixes

* **builder:** handle boolean defaults in type extraction ([e01ea5f](https://github.com/alexmarco/ddlglot/commit/e01ea5f191a2b9663104d4628a3827ac9fea9497))
* **docs:** add setuptools&lt;71 dependency for sphinxcontrib-kroki ([dd2c31b](https://github.com/alexmarco/ddlglot/commit/dd2c31b3b567165ed458bb946a27ced2e3e89181))
* **docs:** read version dynamically from pyproject.toml ([4d14979](https://github.com/alexmarco/ddlglot/commit/4d14979b242dafc8391ece4a5bb6937118e55e6b))
* **docs:** read version dynamically from pyproject.toml ([95476a1](https://github.com/alexmarco/ddlglot/commit/95476a1ac2641a71cc650f695df9c747fd3959a1))


### Documentation

* add CI/CD architecture document and remove release schedule ([78970a0](https://github.com/alexmarco/ddlglot/commit/78970a0d000d4e014440a4a2ca028948036059f3))
* add CI/CD architecture document and remove release schedule ([482cfca](https://github.com/alexmarco/ddlglot/commit/482cfca7958661391f969ab23ca038935a00a064))
* add motivation page explaining origin, use cases, and comparison with ORMs ([b88a091](https://github.com/alexmarco/ddlglot/commit/b88a091940f2199c16e93ac30a428a2b61427571))
* add motivation page explaining origin, use cases, and comparison with ORMs ([8745c1b](https://github.com/alexmarco/ddlglot/commit/8745c1b2cb93a0e65fdde656b0a2a226112d25ce))
* rewrite CICD_ARCHITECTURE.md in English with PlantUML diagrams ([99efe72](https://github.com/alexmarco/ddlglot/commit/99efe72080c02cf842e8548a81f1d4abc5a2f26b))

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
* **agents:** add manual release process section ([014990c](https://github.com/alexmarco/ddlglot/commit/014990c7e851f1b026470037b17fb77254af421c))
* **agents:** add manual release process section ([92cdc93](https://github.com/alexmarco/ddlglot/commit/92cdc938dd76943ae5e4f95fa2a0fe6f195fc6d1))
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
