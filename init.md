## 1) Estructura del paquete

    ddlglot/
    ├─ pyproject.toml
    ├─ README.md
    ├─ src/
    │  └─ ddlglot/
    │     ├─ __init__.py
    │     ├─ builder.py              # Core fluent builder (agnóstico de dialecto)
    │     ├─ properties.py           # Helpers para PROPERTIES/OPTIONS/LOCATION/etc.
    │     └─ variants/
    │        ├─ __init__.py
    │        └─ spark_delta.py       # Preset para Spark + Delta Lake
    └─ tests/
       ├─ test_core.py
       └─ test_spark_delta.py

> SQLGlot ya incluye el dialecto Spark (clase `sqlglot.dialects.spark.Spark`), con tokenizer/parser/generator y transformaciones específicas (por ejemplo, mover `PARTITIONED BY` a columnas de schema cuando corresponda). Esto nos permite generar DDL correcto para Spark/Databricks directamente desde el AST. [\[sqlglot.com\]](https://sqlglot.com/sqlglot/dialects/spark.html), [\[deepwiki.com\]](https://deepwiki.com/tobymao/sqlglot/4.5-hive-presto-and-spark-dialects)

***

## 2) API pública (fluida)

*   `create(kind: str)` → `CreateBuilder`
*   `CreateBuilder.name(table: str)`
*   `CreateBuilder.if_not_exists(flag=True)`
*   `CreateBuilder.temporary(flag=True)`
*   **Esquema**:
    *   `.column(name, dtype, *, not_null=False, pk=False, unique=False, default=None)`
    *   `.columns(("c1","INT"), ("c2","STRING"))`
    *   `.primary_key(*cols)`, `.unique_key(*cols)`
*   **CTAS/VIEW**: `.as_select(select_expr)` *(recibe un `exp.Select`)*
*   **Propiedades de tabla** (genéricas):
    *   `.using(format: str)` *(p. ej. `"delta"` en Spark)*
    *   `.partitioned_by(*cols)`
    *   `.location(path: str)`
    *   `.tblproperties(dict[str, Any])`
    *   `.options(dict[str, Any])` *(Spark: `OPTIONS(...)`)*
    *   `.comment(text)`
*   **Salida**:
    *   `.to_ast()` devuelve `exp.Create`
    *   `.sql(dialect="...")` genera el SQL final

> `PROPERTY_PARSERS` + `Generator` del dialecto determinan cómo se imprimen `PARTITIONED BY`, `TBLPROPERTIES`, `LOCATION`, `USING`, `OPTIONS`, etc. Nosotros sólo construimos los nodos correctos (p. ej., `PartitionedByProperty`, `Properties` con `Property` k/v, etc.). [\[deepwiki.com\]](https://deepwiki.com/tobymao/sqlglot/2.2-expressions), [\[sqlglot.com\]](https://sqlglot.com/sqlglot/generator.html)

***

## 3) Código — **core** (`src/ddlglot/builder.py`)

> Es la versión extendida del prototipo que ya te mostré, ahora con `USING`, `PARTITIONED BY`, `LOCATION`, `TBLPROPERTIES`, `OPTIONS` y `COMMENT`. Usa expresiones estándar de SQLGlot (propiedades y schema). Donde SQLGlot exige cierta estructura (por ejemplo, `Schema(this=Table, expressions=[...])` para evitar `AS` espurio), la aplicamos. [\[github.com\]](https://github.com/tobymao/sqlglot/issues/5389)

```python
# src/ddlglot/builder.py
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from sqlglot import expressions as exp

Lit = Union[str, int, float, bool]

def create(kind: str) -> "CreateBuilder":
    return CreateBuilder(kind)

class CreateBuilder:
    def __init__(self, kind: str):
        self.kind = kind.upper()  # "TABLE", "VIEW", ...
        self._table: Optional[str] = None
        self._columns: List[exp.ColumnDef] = []
        self._table_constraints: List[exp.Expression] = []

        # DDL features:
        self._if_not_exists = False
        self._temporary: Optional[bool] = None
        self._comment: Optional[str] = None

        # CTAS / VIEW AS
        self._ctas_select: Optional[exp.Expression] = None

        # Table properties (Spark/Hive-like)
        self._using: Optional[str] = None
        self._partition_cols: List[exp.Expression] = []
        self._location: Optional[str] = None
        self._tblprops: Dict[str, Lit] = {}
        self._options: Dict[str, Lit] = {}

    # Básicos
    def name(self, table: str) -> "CreateBuilder":
        self._table = table
        return self

    def if_not_exists(self, flag: bool = True) -> "CreateBuilder":
        self._if_not_exists = flag
        return self

    def temporary(self, flag: bool = True) -> "CreateBuilder":
        self._temporary = flag
        return self

    def comment(self, text: str) -> "CreateBuilder":
        self._comment = text
        return self

    # Esquema
    def column(
        self,
        name: str,
        dtype: str,
        *,
        not_null: bool = False,
        pk: bool = False,
        unique: bool = False,
        default: Optional[Lit] = None,
    ) -> "CreateBuilder":
        constraints: List[exp.Expression] = []
        if not_null:
            constraints.append(exp.NotNull())
        if pk:
            constraints.append(exp.PrimaryKey())
        if unique:
            constraints.append(exp.Unique())
        if default is not None:
            lit = (
                exp.Literal.string(default)
                if isinstance(default, str)
                else exp.Literal.number(default) if isinstance(default, (int, float)) else
                exp.Boolean(this=default)
            )
            constraints.append(exp.Default(this=lit))

        self._columns.append(
            exp.ColumnDef(
                this=exp.to_identifier(name),
                kind=exp.DataType.build(dtype),
                constraints=constraints or None,
            )
        )
        return self

    def columns(self, *pairs: Tuple[str, str]) -> "CreateBuilder":
        for n, t in pairs:
            self.column(n, t)
        return self

    def primary_key(self, *cols: str) -> "CreateBuilder":
        self._table_constraints.append(
            exp.PrimaryKey(expressions=[exp.to_identifier(c) for c in cols])
        )
        return self

    def unique_key(self, *cols: str) -> "CreateBuilder":
        self._table_constraints.append(
            exp.Unique(expressions=[exp.to_identifier(c) for c in cols])
        )
        return self

    # CTAS / VIEW AS
    def as_select(self, select_expr: exp.Expression) -> "CreateBuilder":
        self._ctas_select = select_expr
        return self

    # PROPERTIES (Spark/Hive style)
    def using(self, fmt: str) -> "CreateBuilder":
        self._using = fmt
        return self

    def partitioned_by(self, *cols: Union[str, exp.Expression]) -> "CreateBuilder":
        for c in cols:
            self._partition_cols.append(
                exp.to_identifier(c) if isinstance(c, str) else c
            )
        return self

    def location(self, path: str) -> "CreateBuilder":
        self._location = path
        return self

    def tblproperties(self, props: Dict[str, Lit]) -> "CreateBuilder":
        self._tblprops.update(props or {})
        return self

    def options(self, opts: Dict[str, Lit]) -> "CreateBuilder":
        self._options.update(opts or {})
        return self

    # --- helpers internos ---
    @staticmethod
    def _lit(v: Lit) -> exp.Expression:
        if isinstance(v, bool):
            return exp.Boolean(this=v)
        if isinstance(v, (int, float)):
            return exp.Literal.number(v)
        return exp.Literal.string(v)

    def _build_properties(self) -> Optional[exp.Properties]:
        exprs: List[exp.Expression] = []

        # PARTITIONED BY (...)
        if self._partition_cols:
            exprs.append(
                exp.PartitionedByProperty(
                    this=exp.Schema(expressions=self._partition_cols)
                )
            )

        # USING <format>
        if self._using:
            # Algunos dialectos usan "USING delta" (Spark)
            exprs.append(exp.FileFormatProperty(this=exp.to_identifier(self._using.upper())))

        # LOCATION '...'
        if self._location:
            exprs.append(exp.LocationProperty(this=exp.Literal.string(self._location)))

        # OPTIONS (k=v, ...)  (Spark)
        if self._options:
            exprs.append(
                exp.OptionsProperty(
                    expressions=[
                        exp.Property(
                            this=exp.to_identifier(k),
                            value=self._lit(v),
                        )
                        for k, v in self._options.items()
                    ]
                )
            )

        # TBLPROPERTIES ('k' = v, ...)
        if self._tblprops:
            exprs.append(
                exp.Properties(
                    expressions=[
                        exp.Property(
                            this=exp.to_identifier(k) if "." not in k else exp.Identifier(this=k),
                            value=self._lit(v),
                        )
                        for k, v in self._tblprops.items()
                    ]
                )
            )

        # COMMENT
        if self._comment:
            exprs.append(exp.CommentProperty(this=exp.Literal.string(self._comment)))

        return exp.Properties(expressions=exprs) if exprs else None

    def to_ast(self) -> exp.Create:
        if not self._table:
            raise ValueError("Falta .name(<tabla>)")

        table = exp.to_table(self._table)
        props = self._build_properties()

        # Si hay SELECT (CTAS) o es VIEW, usamos expression=Select
        if self._ctas_select is not None or self.kind == "VIEW":
            expr = self._ctas_select or exp.select("*")
            return exp.Create(
                kind=self.kind,
                this=table,
                expression=expr,
                properties=props,
                exists=self._if_not_exists,
                temporary=self._temporary,
            )

        # CREATE TABLE con columnas explícitas
        schema = exp.Schema(this=table, expressions=[*self._columns, *self._table_constraints])
        return exp.Create(
            kind=self.kind,
            this=table,
            expression=schema,
            properties=props,
            exists=self._if_not_exists,
            temporary=self._temporary,
        )

    def sql(self, dialect: Optional[str] = None, pretty: bool = False) -> str:
        return self.to_ast().sql(dialect=dialect, pretty=pretty)
```

> Notas técnicas:
>
> *   El `Schema(this=Table, expressions=[...])` evita que el generador imprima un `AS` accidental tras `CREATE TABLE`, tal como comenta la discusión en GitHub. [\[github.com\]](https://github.com/tobymao/sqlglot/issues/5389)
> *   `PartitionedByProperty`, `LocationProperty`, `OptionsProperty`, `Properties`, `Property`, `CommentProperty` y `FileFormatProperty` son nodos de propiedades que el `Generator` conoce por dialecto (Spark, Hive, etc.). SQLGlot resuelve la **colocación** e impresión final acorde a reglas del generador (p. ej., cuándo poner `PARTITIONED BY` fuera/tras el schema). [\[sqlglot.com\]](https://sqlglot.com/sqlglot/generator.html), [\[deepwiki.com\]](https://deepwiki.com/tobymao/sqlglot/2.2-expressions)

***

## 4) Variante **Spark + Delta** (`src/ddlglot/variants/spark_delta.py`)

### ¿Qué añade?

*   Atajos para `USING DELTA`
*   `TBLPROPERTIES delta.*` (CDF, retention, appendOnly, etc.)
*   `LOCATION` (tablas externas)
*   `PARTITIONED BY`
*   Helpers para **Generated Columns** (patrón recomendado cuando se quiere particionar por expresión: crear una columna generada y particionar por esa columna, ya que particionar “por expresión” no está soportado en Delta). [\[stackoverflow.com\]](https://stackoverflow.com/questions/73568992/using-an-expression-in-a-partitioned-by-definition-in-delta-table), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/databricks/delta/generated-columns)

```python
# src/ddlglot/variants/spark_delta.py
from __future__ import annotations
from typing import Any, Dict, Optional
from sqlglot import expressions as exp
from ..builder import CreateBuilder, create

DELTA_FORMAT = "delta"

class SparkDeltaBuilder:
    """
    Fluent preset para Spark+Delta sobre CreateBuilder.
    """
    def __init__(self, kind: str = "TABLE"):
        self._core = create(kind).using(DELTA_FORMAT)

    # --- proxy de la API base ---
    def name(self, table: str) -> "SparkDeltaBuilder":
        self._core.name(table)
        return self

    def if_not_exists(self, flag: bool = True) -> "SparkDeltaBuilder":
        self._core.if_not_exists(flag)
        return self

    def temporary(self, flag: bool = True) -> "SparkDeltaBuilder":
        self._core.temporary(flag)
        return self

    def comment(self, text: str) -> "SparkDeltaBuilder":
        self._core.comment(text)
        return self

    def column(self, *args, **kwargs) -> "SparkDeltaBuilder":
        self._core.column(*args, **kwargs)
        return self

    def columns(self, *pairs) -> "SparkDeltaBuilder":
        self._core.columns(*pairs)
        return self

    def primary_key(self, *cols: str) -> "SparkDeltaBuilder":
        self._core.primary_key(*cols)
        return self

    def unique_key(self, *cols: str) -> "SparkDeltaBuilder":
        self._core.unique_key(*cols)
        return self

    def partitioned_by(self, *cols) -> "SparkDeltaBuilder":
        self._core.partitioned_by(*cols)
        return self

    def location(self, path: str) -> "SparkDeltaBuilder":
        self._core.location(path)
        return self

    def options(self, opts: Dict[str, Any]) -> "SparkDeltaBuilder":
        self._core.options(opts)
        return self

    def tblproperties(self, props: Dict[str, Any]) -> "SparkDeltaBuilder":
        self._core.tblproperties(props)
        return self

    def as_select(self, select_expr: exp.Expression) -> "SparkDeltaBuilder":
        self._core.as_select(select_expr)
        return self

    # --- atajos Delta ---
    def enable_cdf(self, flag: bool = True) -> "SparkDeltaBuilder":
        # delta.enableChangeDataFeed
        return self.tblproperties({"delta.enableChangeDataFeed": flag})

    def append_only(self, flag: bool = True) -> "SparkDeltaBuilder":
        return self.tblproperties({"delta.appendOnly": flag})

    def log_retention(self, interval: str) -> "SparkDeltaBuilder":
        # p.ej. "30 days"
        return self.tblproperties({"delta.logRetentionDuration": interval})

    def deleted_file_retention(self, interval: str) -> "SparkDeltaBuilder":
        return self.tblproperties({"delta.deletedFileRetentionDuration": interval})

    # Generated Column helper (para particionar por fecha derivada de timestamp)
    def generated_column(self, name: str, dtype: str, expression_sql: str) -> "SparkDeltaBuilder":
        """
        Crea una columna 'GENERATED ALWAYS AS (<expr>)'.
        Útil para particionar por una derivada de otra columna (Delta no permite PARTITIONED BY con expresiones).
        """
        gen = exp.GeneratedAs(this=exp.Anonymous(this=expression_sql))
        self._core._columns.append(
            exp.ColumnDef(
                this=exp.to_identifier(name),
                kind=exp.DataType.build(dtype),
                constraints=[gen],
            )
        )
        return self

    def to_ast(self) -> exp.Create:
        return self._core.to_ast()

    def sql(self, pretty: bool = False) -> str:
        # Dialecto Spark; Databricks comparte sintaxis base + extensiones
        return self._core.sql(dialect="spark", pretty=pretty)

def create_spark_delta(kind: str = "TABLE") -> SparkDeltaBuilder:
    return SparkDeltaBuilder(kind)
```

**Por qué estos atajos**:

*   `USING delta`, `TBLPROPERTIES(...)`, `LOCATION`, `PARTITIONED BY` son sintaxis estándar de Spark/Databricks para tablas Delta. [\[sqlglot.com\]](https://sqlglot.com/sqlglot/dialects/spark.html), [\[docs.databricks.com\]](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-tblproperties)
*   Propiedades `delta.*` como `enableChangeDataFeed`, `appendOnly`, `logRetentionDuration`, `deletedFileRetentionDuration`, etc., están documentadas en **Delta Lake** y **Databricks**. [\[docs.delta.io\]](https://docs.delta.io/table-properties/), [\[docs.databricks.com\]](https://docs.databricks.com/aws/en/delta/table-properties)
*   Delta **no permite** `PARTITIONED BY (expresión)`. Si necesitas particionar por día a partir de un `TIMESTAMP`, la pauta oficial es crear una **generated column** y particionar por **esa columna**. [\[stackoverflow.com\]](https://stackoverflow.com/questions/73568992/using-an-expression-in-a-partitioned-by-definition-in-delta-table), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/databricks/delta/generated-columns)

***

## 5) Ejemplos de uso

### 5.1 Core (agnóstico de dialecto)

```python
from ddlglot import create

sql = (
    create("table")
    .name("public.t_facts")
    .if_not_exists()
    .column("key1", "INTEGER", pk=True, not_null=True)
    .column("name", "VARCHAR(100)", not_null=True)
    .column("amount", "DECIMAL(12,2)", default=0)
    .primary_key("key1")
    .comment("tabla de hechos")
    .sql(dialect="postgres", pretty=True)
)
print(sql)
# CREATE TABLE IF NOT EXISTS public.t_facts (
#   key1 INTEGER NOT NULL PRIMARY KEY,
#   name VARCHAR(100) NOT NULL,
#   amount DECIMAL(12, 2) DEFAULT 0
# )
```

> La impresión final depende del `Generator` del dialecto (`postgres`, `sqlite`, `duckdb`, `spark`, etc.). SQLGlot gestiona comillas, tipos y palabras clave específicas por dialecto. [\[sqlglot.com\]](https://sqlglot.com/sqlglot/generator.html), [\[github.com\]](https://github.com/tobymao/sqlglot)

### 5.2 Spark + Delta (tabla particionada, CDF y ubicación)

```python
from ddlglot.variants.spark_delta import create_spark_delta

ddl = (
    create_spark_delta("TABLE")
    .name("default.sales_delta")
    .if_not_exists()
    .columns(("id","INT"), ("event_time","TIMESTAMP"), ("amount","DECIMAL(12,2)"))
    # Columna generada para particionar por fecha (ver notas abajo)
    .generated_column("event_date", "DATE", "TO_DATE(event_time)")
    .partitioned_by("event_date")
    .enable_cdf(True)
    .append_only(False)
    .log_retention("30 days")
    .deleted_file_retention("7 days")
    .location("s3://my-bucket/delta/sales/")
    .tblproperties({"delta.dataSkippingNumIndexedCols": 8})
    .sql(pretty=True)
)
print(ddl)
# CREATE TABLE IF NOT EXISTS default.sales_delta (
#   id INT,
#   event_time TIMESTAMP,
#   amount DECIMAL(12, 2),
#   event_date DATE GENERATED ALWAYS AS (TO_DATE(event_time))
# )
# USING DELTA
# PARTITIONED BY (event_date)
# LOCATION 's3://my-bucket/delta/sales/'
# TBLPROPERTIES (delta.enableChangeDataFeed = true,
#                 delta.appendOnly = false,
#                 delta.logRetentionDuration = '30 days',
#                 delta.deletedFileRetentionDuration = '7 days',
#                 delta.dataSkippingNumIndexedCols = 8)
```

> *Notas Delta*:  
> • `TBLPROPERTIES` y `LOCATION` forman parte del DDL de Spark/Databricks.   
> • Propiedades `delta.*` están documentadas por Delta Lake / Databricks.   
> • Delta **no** permite `PARTITIONED BY (expresión)`; la alternativa es **generated column** + `PARTITIONED BY (columna)`. [\[docs.databricks.com\]](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-tblproperties), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-tblproperties) [\[docs.delta.io\]](https://docs.delta.io/table-properties/), [\[docs.databricks.com\]](https://docs.databricks.com/aws/en/delta/table-properties) [\[stackoverflow.com\]](https://stackoverflow.com/questions/73568992/using-an-expression-in-a-partitioned-by-definition-in-delta-table), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/databricks/delta/generated-columns)

### 5.3 `CREATE VIEW AS (SELECT ...)` con builder anidado

```python
from sqlglot import expressions as exp
from ddlglot import create

view_sql = (
    create("view")
    .name("default.v_recent")
    .as_select(
        exp.select("id", "amount")
          .from_("default.sales_delta")
          .where("event_date >= DATE '2026-01-01'")
    )
    .sql(dialect="spark", pretty=True)
)
print(view_sql)
# CREATE VIEW default.v_recent AS
# SELECT id, amount FROM default.sales_delta WHERE event_date >= DATE '2026-01-01'
```

> SQLGlot implementa la generación de `CREATE VIEW ... AS <select>` y, en general, la fase de generación se encarga de imprimir cada nodo del AST conforme al dialecto elegido. [\[sqlglot.com\]](https://sqlglot.com/sqlglot/generator.html)

***

## 6) Publicación y *roadmap*

**Publicación**

*   `pyproject.toml`: `name = "ddlglot"`, `requires-python = ">=3.9"`, `dependencies = ["sqlglot>=30"]` (ajustar versión mínima según tus requisitos).
*   Licencia: MIT.
*   CI: tests con `pytest` sobre múltiples dialectos (`postgres`, `sqlite`, `duckdb`, `spark`).

**Roadmap inmediato**

1.  **Variantes**:
    *   `SparkDeltaBuilder` (ya incluido).
    *   `HiveBuilder` (SERDE/`ROW FORMAT`, `STORED AS`, `LOCATION`, `TBLPROPERTIES`).
    *   `BigQueryBuilder` (partitioning/clustering específico). *(Para referencia, muchas herramientas exponen `partition_by`/`cluster_by` específicos; lo documenta dbt con bastante detalle).* [\[docs.getdbt.com\]](https://docs.getdbt.com/reference/resource-configs/bigquery-configs)
2.  **Cobertura DDL adicional**:
    *   `ALTER TABLE` fluido (add/drop column, rename, set/unset tblproperties, etc.).
    *   `CREATE TABLE LIKE` / `CLONE` (donde aplique).
3.  **Validación dialéctica**:
    *   Validadores ligeros para impedir combinaciones no compatibles por dialecto (p. ej., evitar `PARTITIONED BY (expr)` en Delta). [\[stackoverflow.com\]](https://stackoverflow.com/questions/73568992/using-an-expression-in-a-partitioned-by-definition-in-delta-table)

***

## 7) ¿Por qué SQLGlot es buena base?

* Soporta los dialectos principales (Spark/Databricks incluido) con *Tokenizer/Parser/Generator* propios. Podemos construir AST 
con expresiones estándar y delegar la impresión final a cada dialecto. [\[github.com\]](https://github.com/tobymao/sqlglot), 
[\[sqlglot.com\]](https://sqlglot.com/sqlglot/dialects/spark.html)
* Tiene **parsers de propiedades** y un `Generator` rico en *flags* para decidir cómo y dónde se imprimen las propiedades; esto facilita mucho soportar `PARTITIONED BY`, `TBLPROPERTIES`, 
`LOCATION`, `USING`, `OPTIONS`, etc. [\[deepwiki.com\]](https://deepwiki.com/tobymao/sqlglot/2.2-expressions), 
[\[sqlglot.com\]](https://sqlglot.com/sqlglot/generator.html) * Hay precedentes en issues mostrando el uso de 
`PartitionedByProperty`, lo que nos orienta sobre la construcción de propiedades de particionado. 
[\[github.com\]](https://github.com/tobymao/sqlglot/issues/6803)
