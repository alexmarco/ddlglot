# Arquitectura CI/CD de ddlglot

Este documento describe la arquitectura de integración continua y despliegue
(CI/CD) del proyecto ddlglot. Está pensado para que cualquier desarrollador,
incluso sin experiencia previa en CI/CD, pueda entender cómo funciona y
cuándo se ejecutan las diferentes partes del sistema.

---

## 1. Visión General

El proyecto ddlglot cuenta con **3 pipelines** (flujos de trabajo) que se
ejecutan de forma independiente:

| Pipeline | Propósito | Cuándo se ejecuta |
|----------|-----------|-------------------|
| **CI** | Validar código (tests, lint, type checking) | En cada push y PR |
| **Deploy Docs** | Construir y publicar la documentación | En cada push a main |
| **Release Please** | Gestionar releases y publicar a PyPI | Manual o en push a main |

---

## 2. Pipeline CI (Validación de Código)

El pipeline de CI es el más importante y se ejecuta **frecuentemente**. Su
objetivo es asegurar que el código cumple con los estándares de calidad
antes de ser mergeado.

### 2.1. Cuándo se ejecuta

| Evento | Se ejecuta |
|--------|-----------|
| Push a `main` o `develop` | Sí |
| Pull Request hacia `main` o `develop` | Sí |
| Ejecución manual | Sí |

### 2.2. Fases del Pipeline CI

El pipeline CI tiene **2 jobs** que se ejecutan en secuencia:

```
JOB 1: TEST (se ejecuta primero)
────────────────────────────────────────
  1. Checkout del código fuente
  2. Instalar Python 3.13
  3. Instalar uv (gestor de paquetes)
  4. Instalar todas las dependencias
  5. Ruff (linter)        → verifica estilo de código
  6. Ruff (formateador)   → verifica formato
  7. Commitlint           → verifica mensajes de commit
  8. Mypy                 → verificación de tipos (solo errores)
  9. Pytest               → ejecuta tests (151 tests)
 10. Codecov              → sube cobertura de código

Si alguna fase falla, el pipeline se detiene y marca el commit como
"failed" (rojo) en GitHub.

            │
            ▼ (solo si TEST pasa)

JOB 2: BUILD (se ejecuta después de TEST)
────────────────────────────────────────
  1. Checkout del código fuente
  2. Instalar Python 3.13
  3. Instalar herramientas de build (build, hatch)
  4. Construir el paquete Python (.whl y .tar.gz)
  5. Verificar que se puede importar correctamente
  6. Subir los archivos como "artifact" (disponibles 5 días)
```

### 2.3. Qué verifica cada herramienta

| Herramienta | Qué verifica | ¿Bloquea el merge? |
|-------------|--------------|-------------------|
| **Ruff** (check) | Estilo de código (imports, naming, etc.) | Sí |
| **Ruff** (format) | Formato del código | Sí |
| **Commitlint** | Mensajes de commit siguen Conventional Commits | Sí |
| **Mypy** | Errores de tipos (no warnings) | Solo errores |
| **Pytest** | Todos los tests pasan | Sí |

### 2.4. Ejemplo visual

```
Desarrollador hace push
         │
         ▼
┌──────────────────────────────────────────┐
│  CI Pipeline empieza                     │
├──────────────────────────────────────────┤
│  Job TEST                                │
│  ├─ Ruff (linter)      → ✅ pasa        │
│  ├─ Ruff (format)      → ✅ pasa        │
│  ├─ Commitlint         → ✅ pasa        │
│  ├─ Mypy               → ✅ pasa        │
│  ├─ Pytest             → ✅ pasa        │
│  └─ Codecov            → ✅ pasa        │
├──────────────────────────────────────────┤
│  Job BUILD                               │
│  ├─ Build package      → ✅ genera dist/ │
│  └─ Verify import      → ✅ importa OK   │
├──────────────────────────────────────────┤
│  ✓ CI completado (verde en GitHub)       │
└──────────────────────────────────────────┘
```

---

## 3. Pipeline Deploy Docs (Documentación)

Este pipeline construye la documentación Sphinx y la publica en GitHub Pages.

### 3.1. Cuándo se ejecuta

| Evento | Se ejecuta |
|--------|-----------|
| Push a `main` | Sí |
| Ejecución manual | Sí |
| PRs | No |
| Otras ramas | No |

**Importante**: Solo se ejecuta cuando se hace push a la rama `main`.

### 3.2. Fases

```
JOB 1: BUILD
────────────────────────────────────────
  1. Checkout del código
  2. Instalar Python 3.13
  3. Instalar uv
  4. Instalar dependencias de docs (sphinx, sphinx-autoapi)
  5. Construir documentación HTML con Sphinx
  6. Subir como "artifact" para GitHub Pages

            │
            ▼

JOB 2: DEPLOY
────────────────────────────────────────
  1. Desplegar a GitHub Pages
  2. URL: https://alexmarco.github.io/ddlglot/
```

### 3.3. Características

- **Concurrencia**: Si hay otro despliegue en curso, no se cancela.
- **Versión dinámica**: La versión se lee automáticamente de `pyproject.toml`.
- **sphinx-autoapi**: La API reference se genera automáticamente desde el
  código fuente.

---

## 4. Pipeline Release Please (Releases y PyPI)

Este pipeline gestiona las versiones semánticas y publica el paquete en PyPI.

### 4.1. Cuándo se ejecuta

| Evento | Se ejecuta |
|--------|-----------|
| Ejecución manual | Sí |
| Push a `main` | Sí |

### 4.2. Fases

```
JOB 1: RELEASE-PLEASE
────────────────────────────────────────
  1. Checkout del código
  2. Ejecutar Release Please
     ├─ Analiza commits desde la última versión
     ├─ Determina el tipo de cambio (major/minor/patch)
     └─ Crea o actualiza un "Release PR"

  SALIDAS (outputs):
  - releases_created: true/false
  - version: "0.2.0"
  - sha: commit hash

            │
            ▼ (solo si releases_created = true)

JOB 2: PUBLISH
────────────────────────────────────────
  1. Checkout en el commit del tag
  2. Instalar Python 3.13
  3. Instalar uv
  4. Construir el paquete
  5. Publicar en PyPI (Trusted Publisher)
```

### 4.3. Cómo funciona Release Please

Release Please automatiza el versionado semántico basándose en los
mensajes de commit.

**Flujo completo**:

```
1. Desarrollador hace commit conventional:
   "feat(builder): add DDL inspection"

2. Se hace push a main (o se ejecuta manualmente)

3. Release Please detecta el commit "feat:" (nueva feature)

4. Crea un PR de Release ("chore: release 0.2.0") con:
   - Changelog acumulado
   - Nueva versión calculada

5. Se mergea el PR de Release:
   - Se crea tag en GitHub (v0.2.0)
   - Se crea GitHub Release
   - Se publica en PyPI (job publish)
```

**Tipos de cambios según Conventional Commits**:

| Prefijo | Tipo de cambio | Ejemplo de versión |
|---------|----------------|-------------------|
| `feat:` | Nueva funcionalidad | 0.1.0 → 0.2.0 |
| `fix:` | Bug fix | 0.1.0 → 0.1.1 |
| `docs:` | Documentación | No cambia versión |
| `ci:` | Cambios en CI/CD | No cambia versión |

### 4.4. Importante: No hay releases automáticas

Release Please **no publica automáticamente**. Solo crea el PR de Release.
Tú decides cuándo mergear y publicar.

---

## 5. Resumen de Triggers

| Acción | CI | Deploy Docs | Release Please |
|--------|-----|-------------|-----------------|
| Push a `main` | Sí | Sí | Sí |
| Push a `develop` | Sí | No | No |
| Push a otra rama | No | No | No |
| PR a `main` | Sí | No | No |
| PR a `develop` | Sí | No | No |
| Ejecución manual | Sí | Sí | Sí |

---

## 6. Casos de Uso Comunes

### 6.1. Cambio normal (bugfix, feature, docs)

```
1. Crear rama desde main
2. Trabajar en la rama
3. Push → CI se ejecuta
4. Abrir PR → CI se ejecuta en el PR
5. Revisar y mergear
6. CI se ejecuta en main (post-merge)
7. Deploy Docs se ejecuta automáticamente
```

### 6.2. Actualizar documentación

```
1. Hacer cambios en docs/
2. Push a main
3. Deploy Docs se ejecuta automáticamente
4. Verificar en https://alexmarco.github.io/ddlglot/
```

### 6.3. Hacer una release

```
1. Asegurarse de que todos los cambios deseados están en main
2. Opciones para disparar Release Please:
   a. Ejecutar manual: gh workflow run release-please.yml
   b. Hacer push a main (se dispara automáticamente)
3. Release Please crea un PR con changelog y versión
4. Revisar el PR
5. Mergear el PR → tag + GitHub Release + PyPI publish
```

---

## 7. Diagrama General

```
                    PUSH A MAIN
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
       ┌─────────┐  ┌──────────┐  ┌──────────────┐
       │   CI    │  │  Deploy  │  │   Release    │
       │Pipeline │  │   Docs   │  │   Please     │
       └────┬────┘  └────┬─────┘  └──────┬───────┘
            │            │               │
            │        (build)        (create PR)
            │            │               │
            │            ▼            merge PR
            │      GitHub Pages          │
            │                            ▼
            │                      ┌──────────┐
            │                      │ Publish  │
            │                      │   to     │
            │                      │   PyPI   │
            │                      └──────────┘
            │
            ▼
       PR merge + Tests OK
```

---

## 8. Configuración de GitHub Pages

- **URL**: https://alexmarco.github.io/ddlglot/
- **Fuente**: Generado automáticamente por GitHub
- **Build tool**: Sphinx
- **Tema**: sphinx_book_theme
- **Versión**: Leída dinámicamente de `pyproject.toml`

---

## 9. Trusted Publisher (PyPI)

El proyecto usa Trusted Publisher de PyPI, lo que significa:

- No se necesita token API de PyPI en los secrets
- La publicación usa OIDC (OpenID Connect)
- Solo el workflow de Release Please puede publicar
- El entorno se llama `pypi`

---

## 10. Permisos y Seguridad

| Workflow | contents | pages | pull-requests | id-token |
|----------|----------|-------|---------------|----------|
| CI | read | - | - | - |
| Docs | read | write | - | write |
| Release | write | - | write | write |

- **contents**: Leer/editar contenido del repo
- **pages**: Desplegar a GitHub Pages
- **pull-requests**: Crear/editar PRs
- **id-token**: Autenticación OIDC para PyPI

---

## 11. Preguntas Frecuentes

### ¿Puedo ejecutar un workflow manualmente?

Sí, todos los workflows tienen `workflow_dispatch`. Puedes ejecutarlos
desde la pestaña "Actions" en GitHub.

### ¿Qué pasa si falla el CI?

El commit/PR se marca como fallido (rojo). No se puede hacer merge hasta
que todos los checks pasen.

### ¿Cuánto tiempo tarda el CI?

Aproximadamente 1-2 minutos.

### ¿Puedo hacer push directamente a main?

Técnicamente sí (porque eres owner), pero **no se debe hacer**. Siempre
se debe crear un PR.

### ¿Cuándo se publica a PyPI?

Solo cuando se hace merge del Release PR creado por Release Please.

### ¿Qué es el "Release PR"?

Es un PR especial creado por Release Please que contiene:
- Changelog de cambios desde la última versión
- Nueva versión calculada automáticamente
- Etiqueta `autorelease: pending`

### ¿Release Please publica automáticamente?

No. Solo crea el PR. Tú decides cuándo mergear.

---

## 12. Glosario

| Término | Significado |
|---------|-------------|
| **Pipeline** | Flujo automatizado de tareas en GitHub Actions |
| **Job** | Conjunto de steps que se ejecutan en una máquina |
| **Step** | Una tarea individual (ej: "Run tests") |
| **Artifact** | Archivos generados que se pueden descargar |
| **Workflow** | Archivo YAML que define un pipeline |
| **Trusted Publisher** | Autenticación en PyPI sin tokens |
| **Conventional Commits** | Formato de mensajes (feat:, fix:, etc.) |
| **Release PR** | PR especial que crea Release Please |
| **Semantic Versioning** | Versionado major.minor.patch |
| **OIDC** | Protocolo de autenticación para publicación |
