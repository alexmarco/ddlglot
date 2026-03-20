# Plan de Construcción — `ddlglot` v26.03.00

> **Fecha**: 2026-03-20  
> **Versión objetivo**: CalVer `26.03.00`  
> **Basado en**: `prd.md`

---

## Resumen

| Fase | Nombre | Días estimados | Entregable |
|------|--------|----------------|------------|
| 1 | Core Builder | 3-5 | `builder.py`, `properties.py` |
| 2 | Variantes | 5-7 | 5 dialectos (Spark+Delta, Hive, Postgres, DuckDB, BigQuery) |
| 3 | Plugin Registry | 2 | Sistema extensible de variantes |
| 4 | Validación | 3 | Errores específicos por dialecto |
| 5 | Testing | 3-4 | Golden SQL Snapshots |
| 6 | CI/CD | 1-2 | GitHub Actions |
| 7 | Documentación | 2 | Sphinx + GitHub Pages |
| **Total** | | **19-25 días** | |

---

## Fase 1: Core Builder

### 1.1 Estructura de archivos

```
src/ddlglot/
├── __init__.py          # Exports públicos
├── builder.py           # CreateBuilder (core)
├── properties.py        # Helpers de propiedades
├── exceptions.py        # Jerarquía de excepciones
├── registry.py          # Plugin registry base
└── variants/
    ├── __init__.py
    ├── spark_delta.py   # Spark+Delta builder
    ├── hive.py          # Hive builder
    ├── postgres.py      # Postgres builder
    ├── duckdb.py        # DuckDB builder
    └── bigquery.py      # BigQuery builder
```

### 1.2 API pública del Core

```python
# Factory
def create(kind: str) -> "CreateBuilder": ...

# Fluent API
class CreateBuilder:
    # Identificación
    def name(self, table: str) -> "CreateBuilder": ...
    def if_not_exists(self, flag: bool = True) -> "CreateBuilder": ...
    def temporary(self, flag: bool = True) -> "CreateBuilder": ...

    # Esquema
    def column(self, name: str, dtype: str, *, not_null=False, pk=False, 
               unique=False, default=None) -> "CreateBuilder": ...
    def columns(self, *pairs: Tuple[str, str]) -> "CreateBuilder": ...
    def primary_key(self, *cols: str) -> "CreateBuilder": ...
    def unique_key(self, *cols: str) -> "CreateBuilder": ...

    # CTAS / VIEW
    def as_select(self, select_expr: exp.Expression) -> "CreateBuilder": ...

    # Propiedades genéricas
    def using(self, fmt: str) -> "CreateBuilder": ...
    def partitioned_by(self, *cols) -> "CreateBuilder": ...
    def location(self, path: str) -> "CreateBuilder": ...
    def tblproperties(self, props: Dict[str, Lit]) -> "CreateBuilder": ...
    def options(self, opts: Dict[str, Lit]) -> "CreateBuilder": ...
    def comment(self, text: str) -> "CreateBuilder": ...

    # Salida
    def to_ast(self) -> exp.Create: ...
    def sql(self, dialect: Optional[str] = None, pretty: bool = False) -> str: ...
```

### 1.3 Criterios de aceptación

- [ ] `create("table").name("t").column("id", "INT").sql()` genera DDL válido
- [ ] `create("view").as_select(exp.select("*")).sql()` genera VIEW válido
- [ ] Todas las propiedades (USING, PARTITIONED BY, LOCATION, TBLPROPERTIES, OPTIONS, COMMENT) se generan correctamente
- [ ] Tests unitarios para cada método del builder

---

## Fase 2: Variantes

### 2.1 Spark+Delta (`spark_delta.py`)

**Factory**: `create_spark_delta(kind="TABLE")`

**Métodos adicionales**:
```python
def enable_cdf(self, flag: bool = True) -> "SparkDeltaBuilder": ...
def append_only(self, flag: bool = True) -> "SparkDeltaBuilder": ...
def log_retention(self, interval: str) -> "SparkDeltaBuilder": ...
def deleted_file_retention(self, interval: str) -> "SparkDeltaBuilder": ...
def generated_column(self, name: str, dtype: str, expression_sql: str) -> "SparkDeltaBuilder": ...
```

**Validaciones**:
- [ ] Prohibir `partitioned_by(exp)` → `DialectValidationError`
- [ ] Validar propiedades `delta.*` válidas

### 2.2 Hive (`hive.py`)

**Factory**: `create_hive(kind="TABLE")`

**Métodos adicionales**:
```python
def row_format(self, format_type: str, serde: Optional[str] = None) -> "HiveBuilder": ...
def stored_as(self, format_type: str) -> "HiveBuilder": ...
def stored_as_input_format(self, input: str, output: str) -> "HiveBuilder": ...
```

### 2.3 Postgres (`postgres.py`)

**Factory**: `create_postgres(kind="TABLE")`

**Notas**:
- Similar al core, mínimas adiciones
- Validar tipos específicos de Postgres

### 2.4 DuckDB (`duckdb.py`)

**Factory**: `create_duckdb(kind="TABLE")`

**Notas**:
- Similar a Postgres
- No soporta `partitioned_by`
- Validar tipos específicos

### 2.5 BigQuery (`bigquery.py`)

**Factory**: `create_bigquery(kind="TABLE")`

**Métodos adicionales**:
```python
def partition_by(self, expr_or_cols, clustering_cols: List[str] = None) -> "BigQueryBuilder": ...
def cluster_by(self, *cols: str) -> "BigQueryBuilder": ...
def options(self, opts: Dict[str, Any]) -> "BigQueryBuilder": ...
```

---

## Fase 3: Plugin Registry

### 3.1 API del registry

```python
def register_variant(name: str, builder_class: Type[CreateBuilder]): ...
def get_variant(name: str) -> Type[CreateBuilder]: ...
def list_variants() -> List[str]: ...
```

### 3.2 Decoradores

```python
@variant("spark_delta")
class SparkDeltaBuilder(CreateBuilder):
    ...
```

---

## Fase 4: Validación Estricta

### 4.1 Jerarquía de excepciones

```
DDLGlotError (base)
├── ValidationError
│   ├── DialectValidationError
│   └── SchemaValidationError
├── ASTBuildError
└── UnsupportedDialectError
```

### 4.2 Validaciones por dialecto

| Dialecto | Regla | Error |
|----------|-------|-------|
| Spark+Delta | `PARTITIONED BY (expr)` | `DialectValidationError` |
| Spark+Delta | `delta.*` inválido | `DialectValidationError` |
| BigQuery | `cluster_by` sin `partition_by` | `DialectValidationError` |
| DuckDB | `partitioned_by` | `DialectValidationError` |

---

## Fase 5: Testing

### 5.1 Estructura de tests

```
tests/
├── __init__.py
├── test_core.py
├── test_spark_delta.py
├── test_hive.py
├── test_postgres.py
├── test_duckdb.py
├── test_bigquery.py
├── test_validation.py
├── test_registry.py
└── snapshots/
    ├── spark_delta/
    │   ├── ctas.sql
    │   ├── partitioned.sql
    │   └── delta_table.sql
    ├── hive/
    └── ...
```

### 5.2 Tipos de tests

- **Unit tests**: Cada método del builder
- **Golden SQL snapshots**: Comparar SQL generado vs. esperado
- **Validation tests**: Verificar errores en casos inválidos

---

## Fase 6: CI/CD

### 6.1 GitHub Actions workflow

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    strategy:
      matrix:
        python: [3.11, 3.12, 3.13]
        sqlglot: [">=25.0.0"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: pytest --cov=ddlglot

  build:
    needs: test
    steps:
      - run: hatch build
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### 6.2 Secretos requeridos

- `PYPI_API_TOKEN`: Token para publicar en PyPI

---

## Fase 7: Documentación

### 7.1 Estructura Sphinx

```
docs/
├── conf.py
├── index.rst
├── quickstart.rst
├── core_builder.rst
├── variants/
│   ├── spark_delta.rst
│   ├── hive.rst
│   ├── bigquery.rst
│   ├── postgres.rst
│   └── duckdb.rst
├── validation.rst
├── plugin_registry.rst
├── api_reference.rst
└── changelog.rst
```

### 7.2 GitHub Pages

- Deploy automático tras release tag
- Usar `mike` para versionado de docs

---

## Roadmap Detallado

### Semana 1-2: Core + Spark+Delta

| Día | Tarea |
|-----|-------|
| 1 | Configurar pyproject.toml con dependencias (sqlglot, pytest, ruff) |
| 2 | Implementar `builder.py` - Identificación y esquema |
| 3 | Implementar `builder.py` - Propiedades y CTAS |
| 4 | Implementar `properties.py` |
| 5 | Tests del core |
| 6-7 | Implementar `spark_delta.py` |
| 8-9 | Validaciones Delta |
| 10 | Tests Spark+Delta |

### Semana 3-4: Variantes restantes

| Día | Tarea |
|-----|-------|
| 11-12 | Implementar `hive.py` |
| 13-14 | Implementar `postgres.py` + `duckdb.py` |
| 15-16 | Implementar `bigquery.py` |
| 17 | Plugin registry |
| 18-19 | Validaciones cruzadas |
| 20 | Tests integrados |

### Semana 5: CI/CD + Docs

| Día | Tarea |
|-----|-------|
| 21-22 | GitHub Actions CI/CD |
| 23 | Golden SQL snapshots |
| 24-25 | Sphinx docs + GitHub Pages |

---

## Dependencias

```toml
[project]
dependencies = [
    "sqlglot>=25.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.4.0",
    "mypy>=1.8",
]
```

---

## Checklist de Release

- [ ] Todos los tests pasan
- [ ] `ruff check .` sin errores
- [ ] `mypy src/ddlglot` sin errores
- [ ] Cobertura > 80%
- [ ] Documentación actualizada
- [ ] CHANGELOG.md completo
- [ ] Version bump a `26.03.00`
- [ ] Tag git `v26.03.00`
- [ ] Publish a PyPI
