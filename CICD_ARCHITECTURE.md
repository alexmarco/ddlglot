# CI/CD Architecture

This document describes the continuous integration and deployment (CI/CD) architecture of the ddlglot project. It is designed so that any developer, even without prior CI/CD experience, can understand how the system works and when each part is executed.

---

## 1. Overview

The ddlglot project has **3 pipelines** (workflows) that run independently:

| Pipeline | Purpose | When it runs |
|----------|---------|--------------|
| **CI** | Validate code (tests, lint, type checking) | On every push and PR |
| **Deploy Docs** | Build and publish documentation | On every push to main |
| **Release Please** | Manage releases and publish to PyPI | Manual only |

---

## 2. CI Pipeline (Code Validation)

The CI pipeline is the most important one and runs **frequently**. Its goal is to ensure code meets quality standards before merging.

### 2.1. When it runs

| Event | Runs |
|-------|------|
| Push to `main` or `develop` | Yes |
| Any Pull Request | Yes |
| Manual execution | Yes |

### 2.2. Pipeline phases

The CI pipeline has **2 jobs** that run sequentially:

```
JOB 1: TEST (runs first)
──────────────────────────────────────────────────────────────
  1. Checkout source code
  2. Install Python 3.13
  3. Install uv package manager
  4. Install all dependencies
  5. Ruff (linter)       — verifies code style
  6. Ruff (formatter)    — verifies formatting
  7. Commitlint          — verifies commit messages
  8. Mypy                — type checking (errors only)
  9. Pytest              — runs tests (151 tests)
 10. Codecov             — uploads code coverage

If any step fails, the pipeline stops and marks the commit as FAILED.

                    │ (only if TEST passes)
                    ▼

JOB 2: BUILD (runs after TEST)
──────────────────────────────────────────────────────────────
  1. Checkout source code
  2. Install Python 3.13
  3. Install build tools
  4. Build Python package (.whl and .tar.gz)
  5. Verify the package imports correctly
  6. Upload artifacts (available 5 days)
```

### 2.3. What each tool checks

| Tool | What it checks | Blocks merge |
|------|----------------|--------------|
| **Ruff** (check) | Code style (imports, naming, etc.) | Yes |
| **Ruff** (format) | Code formatting | Yes |
| **Commitlint** | Commit messages follow Conventional Commits | Yes |
| **Mypy** | Type errors (not warnings) | Errors only |
| **Pytest** | All tests pass | Yes |

---

## 3. Deploy Docs Pipeline (Documentation)

This pipeline builds the Sphinx documentation and publishes it to GitHub Pages.

### 3.1. When it runs

| Event | Runs |
|-------|------|
| Push to `main` | Yes |
| Manual execution | Yes |
| PRs | No |
| Other branches | No |

**Important**: It only runs on pushes to the `main` branch.

### 3.2. Pipeline phases

```
JOB 1: BUILD
──────────────────────────────────────────────────────────────
  1. Checkout code
  2. Install Python 3.13
  3. Install uv
  4. Install docs dependencies (sphinx, sphinx-autoapi, sphinxcontrib-kroki)
  5. Build HTML documentation with Sphinx
  6. Upload as artifact for GitHub Pages

                    │
                    ▼

JOB 2: DEPLOY
──────────────────────────────────────────────────────────────
  1. Deploy to GitHub Pages
     URL: https://alexmarco.github.io/ddlglot/
```

### 3.3. Features

- **Concurrency**: If another deployment is in progress, it does not cancel.
- **Dynamic version**: The version is read automatically from `pyproject.toml`.
- **sphinx-autoapi**: The API reference is generated automatically from the source code.
- **sphinxcontrib-kroki**: Diagrams are rendered via kroki.io at build time.

---

## 4. Release Please Pipeline (Releases and PyPI)

This pipeline manages semantic versions and publishes the package to PyPI.

### 4.1. When it runs

| Event | Runs |
|-------|------|
| Manual execution (`workflow_dispatch`) | Yes |
| Push to `main` | No (manual-only) |

### 4.2. Pipeline phases

```
JOB 1: RELEASE-PLEASE
──────────────────────────────────────────────────────────────
  1. Checkout code
  2. Run Release Please
  3. Analyze commits since last version
  4. Determine change type (major/minor/patch)
  5. Create or update Release PR

OUTPUTS:
  - releases_created: true/false
  - version: "0.3.0"
  - sha: commit hash

                    │ (only if releases_created = true)
                    ▼

JOB 2: PUBLISH
──────────────────────────────────────────────────────────────
  1. Checkout at tag commit
  2. Install Python 3.13
  3. Install uv
  4. Build the package
  5. Publish to PyPI (Trusted Publisher)
```

### 4.3. How Release Please works

Release Please automates semantic versioning based on commit messages.

**Complete flow**:

```
1. Developer makes a Conventional Commit:
   "feat(builder): add DDL inspection"

2. Push to main (via regular PR merge)

3. Run Release Please manually:
   gh workflow run release-please.yml

4. Release Please detects "feat:" (new feature)

5. Creates a Release PR ("chore: release 0.3.0") with:
   - Accumulated changelog
   - Calculated new version

6. CI runs automatically on the Release PR

7. Review and merge the Release PR

8. GitHub creates tag (v0.3.0)

9. GitHub creates GitHub Release

10. Job PUBLISH publishes to PyPI
```

**Change types based on Conventional Commits**:

| Prefix | Change type | Version example |
|--------|-------------|-----------------|
| `feat:` | New functionality | 0.1.0 → 0.2.0 |
| `fix:` | Bug fix | 0.1.0 → 0.1.1 |
| `docs:` | Documentation | No version change |
| `ci:` | CI/CD changes | No version change |

### 4.4. Important: No automatic releases

Release Please **does not publish automatically**. It only creates the Release PR. You decide when to merge and publish.

---

## 5. Trigger Summary

| Action | CI | Deploy Docs | Release Please |
|--------|----|------------|----------------|
| Push to `main` | Yes | Yes | No (manual-only) |
| Push to `develop` | Yes | No | No |
| Push to other branch | No | No | No |
| PR to `main` or `develop` | Yes | No | No |
| Any other PR | Yes | No | No |
| Manual execution | Yes | Yes | Yes |

---

## 6. Common Use Cases

### 6.1. Normal change (bugfix, feature, docs)

1. Create branch from `main`
2. Work on the branch
3. Push → CI runs
4. Open PR → CI runs on the PR
5. Review and merge
6. CI runs on `main` (post-merge)
7. Deploy Docs runs automatically

### 6.2. Update documentation

1. Make changes in `docs/`
2. Push to `main` (via PR)
3. Deploy Docs runs automatically
4. Verify at https://alexmarco.github.io/ddlglot/

### 6.3. Make a release

1. Ensure all desired changes are on `main`
2. Trigger Release Please manually:

   ```bash
   gh workflow run release-please.yml
   ```

3. Release Please creates a PR with changelog and version
4. CI runs automatically on the Release PR (no manual trigger needed)
5. Review the PR
6. Merge the PR → tag + GitHub Release + PyPI publish

---

## 7. GitHub Pages Configuration

| Setting | Value |
|---------|-------|
| URL | https://alexmarco.github.io/ddlglot/ |
| Source | Generated automatically by GitHub |
| Build tool | Sphinx |
| Theme | sphinx_book_theme |
| Version | Read dynamically from `pyproject.toml` |

---

## 8. Trusted Publisher (PyPI)

The project uses PyPI Trusted Publisher, which means:

- No PyPI API token in secrets is needed
- Publishing uses OIDC (OpenID Connect)
- Only the Release Please workflow can publish
- The environment is named `pypi`

---

## 9. Permissions and Security

| Workflow | contents | pages | pull-requests | id-token |
|----------|----------|-------|---------------|----------|
| CI | read | - | - | - |
| Docs | read | write | - | write |
| Release | write | - | write | write |

| Permission | Meaning |
|------------|---------|
| **contents** | Read/edit repo content |
| **pages** | Deploy to GitHub Pages |
| **pull-requests** | Create/edit PRs |
| **id-token** | OIDC authentication for PyPI |

---

## 10. FAQ

**Can I run a workflow manually?**

Yes, all workflows have `workflow_dispatch`. You can run them from the "Actions" tab on GitHub.

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
- Label `autorelease: pending`

**Does Release Please publish automatically?**

No. It only creates the PR. You decide when to merge.

---

## 11. Glossary

| Term | Meaning |
|------|---------|
| **Pipeline** | Automated flow of tasks in GitHub Actions |
| **Job** | Set of steps that run on one machine |
| **Step** | Individual task (e.g., "Run tests") |
| **Artifact** | Generated files that can be downloaded |
| **Workflow** | YAML file that defines a pipeline |
| **Trusted Publisher** | PyPI authentication without tokens |
| **Conventional Commits** | Commit message format (feat:, fix:, etc.) |
| **Release PR** | Special PR created by Release Please |
| **Semantic Versioning** | Versioning as major.minor.patch |
| **OIDC** | Authentication protocol for publishing |
| **Kroki** | Diagram rendering service (kroki.io) |
