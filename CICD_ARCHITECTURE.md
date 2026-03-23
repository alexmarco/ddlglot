# CI/CD Architecture

This document describes the continuous integration and deployment (CI/CD) architecture of the ddlglot project. It is designed so that any developer, even without prior CI/CD experience, can understand how the system works and when each part is executed.

---

## 1. Overview

The ddlglot project has **3 pipelines** (workflows) that run independently:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Pipeline
     - Purpose
     - When it runs
   * - **CI**
     - Validate code (tests, lint, type checking)
     - On every push and PR
   * - **Deploy Docs**
     - Build and publish documentation
     - On every push to main
   * - **Release Please**
     - Manage releases and publish to PyPI
     - Manual or on push to main

---

## 2. CI Pipeline (Code Validation)

The CI pipeline is the most important one and runs **frequently**. Its goal is to ensure code meets quality standards before merging.

### 2.1. When it runs

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - Event
     - Runs
   * - Push to ``main`` or ``develop``
     - Yes
   * - Pull Request to ``main`` or ``develop``
     - Yes
   * - Manual execution
     - Yes

### 2.2. Pipeline phases

The CI pipeline has **2 jobs** that run sequentially:

.. plantuml::
   @startuml
   skinparam defaultTextAlignment center
   skinparam wrapWidth 300

   |**JOB 1: TEST**|
   start
   :Checkout source code;
   :Install Python 3.13;
   :Install uv package manager;
   :Install all dependencies;
   :Ruff (linter) — verifies code style;
   :Ruff (formatter) — verifies formatting;
   :Commitlint — verifies commit messages;
   :Mypy — type checking (errors only);
   :Pytest — runs tests (151 tests);
   :Codecov — uploads code coverage;
   note right
     If any step fails,
     the pipeline stops
     and marks the commit as **failed**.
   end note
   |**JOB 2: BUILD**|
   :Checkout source code;
   :Install Python 3.13;
   :Install build tools;
   :Build Python package (.whl and .tar.gz);
   :Verify the package imports correctly;
   :Upload artifacts (available 5 days);
   stop

   @enduml

### 2.3. What each tool checks

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Tool
     - What it checks
     - Blocks merge
   * - **Ruff** (check)
     - Code style (imports, naming, etc.)
     - Yes
   * - **Ruff** (format)
     - Code formatting
     - Yes
   * - **Commitlint**
     - Commit messages follow Conventional Commits
     - Yes
   * - **Mypy**
     - Type errors (not warnings)
     - Errors only
   * - **Pytest**
     - All tests pass
     - Yes

---

## 3. Deploy Docs Pipeline (Documentation)

This pipeline builds the Sphinx documentation and publishes it to GitHub Pages.

### 3.1. When it runs

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - Event
     - Runs
   * - Push to ``main``
     - Yes
   * - Manual execution
     - Yes
   * - PRs
     - No
   * - Other branches
     - No

**Important**: It only runs on pushes to the ``main`` branch.

### 3.2. Pipeline phases

.. plantuml::
   @startuml
   skinparam defaultTextAlignment center

   |**JOB 1: BUILD**|
   start
   :Checkout code;
   :Install Python 3.13;
   :Install uv;
   :Install docs dependencies (sphinx, sphinx-autoapi, sphinxcontrib-kroki);
   :Build HTML documentation with Sphinx;
   :Upload as artifact for GitHub Pages;
   |**JOB 2: DEPLOY**|
   :Deploy to GitHub Pages;
   stop

   note right
     URL: https://alexmarco.github.io/ddlglot/
   end note

   @enduml

### 3.3. Features

- **Concurrency**: If another deployment is in progress, it does not cancel.
- **Dynamic version**: The version is read automatically from ``pyproject.toml``.
- **sphinx-autoapi**: The API reference is generated automatically from the source code.
- **sphinxcontrib-kroki**: Diagrams are rendered via kroki.io at build time.

---

## 4. Release Please Pipeline (Releases and PyPI)

This pipeline manages semantic versions and publishes the package to PyPI.

### 4.1. When it runs

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - Event
     - Runs
   * - Manual execution
     - Yes
   * - Push to ``main``
     - Yes

### 4.2. Pipeline phases

.. plantuml::
   @startuml
   skinparam defaultTextAlignment center
   skinparam wrapWidth 300

   |**JOB 1: RELEASE-PLEASE**|
   start
   :Checkout code;
   :Run Release Please;
   :Analyze commits since last version;
   :Determine change type (major/minor/patch);
   :Create or update Release PR;
   stop

   detach

   (**releases_created = true**)

   |**JOB 2: PUBLISH**|
   :Checkout at tag commit;
   :Install Python 3.13;
   :Install uv;
   :Build the package;
   :Publish to PyPI (Trusted Publisher);
   stop

   @enduml

### 4.3. How Release Please works

Release Please automates semantic versioning based on commit messages.

**Complete flow**:

.. plantuml::
   @startuml
   skinparam defaultTextAlignment center
   skinparam wrapWidth 300

   start
   :Developer makes a Conventional Commit:\n"feat(builder): add DDL inspection";
   :Push to main (or run manually);
   :Release Please detects "feat:" (new feature);
   :Creates a Release PR ("chore: release 0.2.0") with:\n  - Accumulated changelog\n  - Calculated new version;
   :Review and merge the Release PR;
   :GitHub creates tag (v0.2.0);
   :GitHub creates GitHub Release;
   :Job PUBLISH publishes to PyPI;
   stop

   @enduml

**Change types based on Conventional Commits**:

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - Prefix
     - Change type
     - Version example
   * - ``feat:``
     - New functionality
     - 0.1.0 → 0.2.0
   * - ``fix:``
     - Bug fix
     - 0.1.0 → 0.1.1
   * - ``docs:``
     - Documentation
     - No version change
   * - ``ci:``
     - CI/CD changes
     - No version change

### 4.4. Important: No automatic releases

Release Please **does not publish automatically**. It only creates the Release PR. You decide when to merge and publish.

---

## 5. Trigger Summary

.. list-table::
   :header-rows: 1
   :widths: 30 15 20 25

   * - Action
     - CI
     - Deploy Docs
     - Release Please
   * - Push to ``main``
     - Yes
     - Yes
     - Yes
   * - Push to ``develop``
     - Yes
     - No
     - No
   * - Push to other branch
     - No
     - No
     - No
   * - PR to ``main``
     - Yes
     - No
     - No
   * - PR to ``develop``
     - Yes
     - No
     - No
   * - Manual execution
     - Yes
     - Yes
     - Yes

---

## 6. Common Use Cases

### 6.1. Normal change (bugfix, feature, docs)

1. Create branch from ``main``
2. Work on the branch
3. Push → CI runs
4. Open PR → CI runs on the PR
5. Review and merge
6. CI runs on ``main`` (post-merge)
7. Deploy Docs runs automatically

### 6.2. Update documentation

1. Make changes in ``docs/``
2. Push to ``main``
3. Deploy Docs runs automatically
4. Verify at https://alexmarco.github.io/ddlglot/

### 6.3. Make a release

1. Ensure all desired changes are on ``main``
2. Options to trigger Release Please:
   a. Run manually: ``gh workflow run release-please.yml``
   b. Push to ``main`` (runs automatically)
3. Release Please creates a PR with changelog and version
4. Review the PR
5. Merge the PR → tag + GitHub Release + PyPI publish

---

## 7. GitHub Pages Configuration

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Setting
     - Value
   * - URL
     - https://alexmarco.github.io/ddlglot/
   * - Source
     - Generated automatically by GitHub
   * - Build tool
     - Sphinx
   * - Theme
     - sphinx_book_theme
   * - Version
     - Read dynamically from ``pyproject.toml``

---

## 8. Trusted Publisher (PyPI)

The project uses PyPI Trusted Publisher, which means:

- No PyPI API token in secrets is needed
- Publishing uses OIDC (OpenID Connect)
- Only the Release Please workflow can publish
- The environment is named ``pypi``

---

## 9. Permissions and Security

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 20 30

   * - Workflow
     - contents
     - pages
     - pull-requests
     - id-token
   * - CI
     - read
     - -
     - -
     - -
   * - Docs
     - read
     - write
     - -
     - write
   * - Release
     - write
     - -
     - write
     - write

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Permission
     - Meaning
   * - **contents**
     - Read/edit repo content
   * - **pages**
     - Deploy to GitHub Pages
   * - **pull-requests**
     - Create/edit PRs
   * - **id-token**
     - OIDC authentication for PyPI

---

## 10. FAQ

**Can I run a workflow manually?**

Yes, all workflows have ``workflow_dispatch``. You can run them from the "Actions" tab on GitHub.

**What happens if CI fails?**

The commit/PR is marked as failed (red). Merge is blocked until all checks pass.

**How long does CI take?**

Approximately 1-2 minutes.

**Can I push directly to main?**

Technically yes (because you are the owner), but **you should not**. Always create a PR.

**When does PyPI publish happen?**

Only when the Release PR created by Release Please is merged.

**What is the "Release PR"?**

It is a special PR created by Release Please that contains:

- Changelog of changes since the last version
- Automatically calculated new version
- Label ``autorelease: pending``

**Does Release Please publish automatically?**

No. It only creates the PR. You decide when to merge.

---

## 11. Glossary

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Term
     - Meaning
   * - **Pipeline**
     - Automated flow of tasks in GitHub Actions
   * - **Job**
     - Set of steps that run on one machine
   * - **Step**
     - Individual task (e.g., "Run tests")
   * - **Artifact**
     - Generated files that can be downloaded
   * - **Workflow**
     - YAML file that defines a pipeline
   * - **Trusted Publisher**
     - PyPI authentication without tokens
   * - **Conventional Commits**
     - Commit message format (feat:, fix:, etc.)
   * - **Release PR**
     - Special PR created by Release Please
   * - **Semantic Versioning**
     - Versioning as major.minor.patch
   * - **OIDC**
     - Authentication protocol for publishing
   * - **Kroki**
     - Diagram rendering service (kroki.io)
