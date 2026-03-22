project = "ddlglot"
copyright = "2026, alexmarco"
author = "alexmarco"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "autoapi.extension",
]

autoapi_dirs = ["../src"]
autoapi_type = "python"
autoapi_root = "api"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sqlglot": ("https://sqlglot.readthedocs.io/en/latest/", None),
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"
