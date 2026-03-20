Perfecto, Alejandro.\
Con todas las decisiones cerradas, procedo a generar el **Documento de Arquitectura v1 de `ddlglot`**.

A partir de aquí estoy **fuera de modo preguntas** y entro en **modo entrega formal**, siguiendo tu instrucción y el estilo que solicitaste.

***

# 📘 **Documento de Arquitectura v1 — `ddlglot`**

*Autor: Arquitectura Técnica*\
*Estilo: Martin Fowler / Technical Narrative*\
*Fecha: 2026‑03*

***

# 1. **Visión general**

`ddlglot` es una librería Python cuyo propósito es proporcionar:

*   Un **builder fluido y extensible** para generar DDL portable a múltiples motores SQL.
*   Un sistema de **variantes por dialecto** (Spark+Delta, Hive, BigQuery, Postgres, DuckDB…).
*   Un mecanismo de **validación estricta** por dialecto para evitar generación de DDL inválido.
*   Un **núcleo agnóstico** basado en *SQLGlot*, usando su AST y generador.
*   Un interfaz pública clara y estable (`CreateBuilder` y variantes).
*   Un ecosistema reproducible: tests, CI/CD, publicación PyPI, documentación en Sphinx.

La librería se inspira en el patrón *Builder* y en DSLs de DDL ya existentes en ecosistemas como dbt, pero centrada en generación programática y validación dialéctica.

***

# 2. **Objetivos arquitectónicos**

## 2.1 Funcionales

*   Permitir construir ASTs de SQLGlot para operaciones de **CREATE TABLE**, **CREATE VIEW**, **CTAS**, incluyendo:
    *   Columnas
    *   Tipos y constraints
    *   Propiedades de tabla (`PARTITIONED BY`, `USING`, `OPTIONS`, `TBLPROPERTIES`, `LOCATION`)
    *   Comentarios
    *   Generated Columns

*   Proveer variantes específicas:
    *   **Spark+Delta** (v1)
    *   Hive
    *   BigQuery
    *   Postgres
    *   DuckDB

*   Permitir registro dinámico de variantes (plugin-like).

## 2.2 No funcionales

*   **Simplicidad**: API fluida, legible y extensible.
*   **Robustez**: validación estricta en cada dialecto.
*   **Portabilidad**: independencia del motor, delegando en SQLGlot la generación final.
*   **Trazabilidad**: jerarquía clara de excepciones.
*   **Mantenibilidad**: diseño modular + documentación completa.
*   **Versionado CalVer**: `YY.MM.XX`.

***

# 3. **Contexto del sistema**



***

# 4. **Arquitectura Lógica**

## 4.1 Módulos



***

# 5. **Diseño del Core**

## 5.1 CreateBuilder

Roles:

*   Mantener un **estado inmutable mutable** del DDL en construcción.
*   Proveer un DSL fluido para columnas, constraints y propiedades.
*   Producir un AST **exp.Create** de SQLGlot.
*   NO valida reglas de dialecto (lo hacen las variantes).



***

# 6. **Diseño del sistema de variantes**

Cada variante es un *wrapper* alrededor de `CreateBuilder` y:

*   Añade **validaciones estrictas**.
*   Añade **helpers específicos del dialecto** (p.ej. Delta generated columns, Hive SERDE, BigQuery cluster\_by, etc.).
*   Define el dialect por defecto para `sql()`.

## 6.1 Spark+Delta

Reglas:

*   `PARTITIONED BY (expr)` **prohibido**.
*   Se permite `GENERATED ALWAYS AS (…)` para particionar por derivadas.
*   Propiedades válidas: `delta.*`.



## 6.2 HiveBuilder

*   Añade soporte a SERDE, ROW FORMAT, STORED AS, LOCATION.
*   Validaciones: ciertos formatos incompatibles entre sí.

## 6.3 BigQueryBuilder

*   Añade `partition_by` y `cluster_by` de BigQuery.
*   Validación de modelos particionados por columna vs. pseudo-columnas.
*   Asegura que `OPTIONS(...)` usa `exp.OptionsProperty`.

## 6.4 PostgresBuilder

*   Foco en restricciones, tipos, `WITH (...)` opcionales.
*   No añade propiedades de formato.

## 6.5 DuckDBBuilder

*   Dialecto bastante cercano a Postgres.
*   Validaciones mínimas, pero incluir:
    *   `partition_by` no existe.
    *   ciertos tipos no soportados.

***

# 7. **Plugin Registry**

Permite registrar variantes:



***

# 8. **Jerarquía de Excepciones**



***

# 9. **Validación estricta por dialecto**

Ejemplos:

### Spark+Delta

*   ❌ `partitioned_by(exp("date(ts)"))` → `DialectValidationError`.
*   ✔ `generated_column("day", "DATE", "TO_DATE(ts)")` + `partitioned_by("day")`.

### BigQuery

*   ❌ `cluster_by` sin `partition_by` (según configuraciones específicas).
*   ❌ Partition por tipos no soportados.

***

# 10. **Testing**

### Enfoque principal: **Golden SQL Snapshot**

*   Para cada dialecto, una carpeta `tests/snapshots/spark/…`.
*   Cada builder produce SQL → se compara con el archivo snapshot.
*   Mantenemos compatibilidad con múltiples versiones de SQLGlot.

### Tests de invariantes mínimos

*   Generated Column siempre antes de `PARTITION BY`.
*   `LOCATION` siempre string literal.

***

# 11. **CI/CD**

### GitHub Actions

*   Matriz: Python 3.11–3.12.
*   Instala SQLGlot en rango amplio.
*   Ejecuta:
    *   `pytest`
    *   `ruff` (linter)
    *   `mypy` opcional futuro
*   Construye documentación Sphinx.
*   Publicación PyPI mediante:
    *   Release tags + acción de build
    *   OIDC si está disponible
    *   Alternativa: token PyPI en `PYPI_API_TOKEN` (secreto).

***

# 12. **Documentación (Sphinx + GitHub Pages)**

Estructura propuesta:

    docs/
      index.rst
      quickstart.rst
      core_builder.rst
      variants/
        spark_delta.rst
        hive.rst
        bigquery.rst
        postgres.rst
        duckdb.rst
      validation.rst
      plugin_registry.rst
      api_reference.rst
      changelog.rst

***

# 13. **Versionado CalVer**

Formato: `YY.MM.XX`

*   `26.03.00` primera versión de marzo 2026
*   Cambios incompatibles → **se documentan claramente en CHANGELOG**, no afectan numeración.

***

# 14. **Infraestructura y despliegue**

### Producción del paquete

*   Artefacto: rueda (`.whl`) y tarball (`.tar.gz`).
*   Hosted en PyPI.
*   Instalable en proyectos Databricks, Airflow, pipelines CI, etc.

### Documentación

*   GitHub Pages via `gh-pages`.
*   Actualización automática tras cada release.

***

# 15. **Riesgos y mitigaciones**

### Riesgo: cambio en el AST de SQLGlot

*   Mitigación:
    *   Golden tests por dialecto.
    *   CI probando contra varias versiones SQLGlot.

### Riesgo: usuarios externos añaden variantes incorrectas

*   Mitigación:
    *   Uso del plugin registry documentado.
    *   Jerarquía de excepciones clara.
    *   Validación estricta.

### Riesgo: DDL incorrecto para Spark+Delta (p. ej. particionado por expresión)

*   Mitigación:
    *   Validación en variante.
    *   Tests específicos para Delta.

***

# 16. **Ejemplo integrado**

```python
from ddlglot.variants.spark_delta import create_spark_delta

ddl = (
  create_spark_delta()
    .name("default.sales")
    .columns(("id","INT"), ("ts","TIMESTAMP"))
    .generated_column("day", "DATE", "TO_DATE(ts)")
    .partitioned_by("day")
    .enable_cdf(True)
    .sql(pretty=True)
)

print(ddl)
```

***

# 17. **Roadmap**

*   v1.0 (CalVer `26.03.00`):
    *   Core builder estable
    *   Variantes Spark+Delta, Hive, Postgres, DuckDB, BigQuery
    *   Registro de variantes
    *   CI/CD + Docs

*   v1.x:
    *   `ALTER TABLE` builder
    *   Validaciones avanzadas
    *   Más propiedades BigQuery & Hive

