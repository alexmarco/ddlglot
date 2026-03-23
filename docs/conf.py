project = "ddlglot"
copyright = "2026, alexmarco"
author = "alexmarco"

with open("../pyproject.toml", "rb") as f:
    import tomllib

    pyproject = tomllib.load(f)
    release = pyproject["project"]["version"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "autoapi.extension",
    "sphinxcontrib.kroki",
]

autoapi_dirs = ["../src"]
autoapi_type = "python"
autoapi_root = "api"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["fonts.css"]
html_theme_options = {
    "logo": {
        "image_light": "_static/logo.png",
        "image_dark": "_static/logo.png",
        "text": f"ddlglot v{release}",
    },
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sqlglot": ("https://sqlglot.readthedocs.io/en/latest/", None),
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"
