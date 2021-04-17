# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from netlint.checks.checker import Checker

sys.path.insert(0, os.path.abspath("../../"))

# -- Project information -----------------------------------------------------

project = "netlint"
copyright = "2021, Leo Kirchner"
author = "Leo Kirchner"

# The full version, including alpha/beta/rc tags
release = "0.1.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_rtd_theme", "sphinx.ext.autodoc", "m2r2", "sphinx_click"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

source_suffix = [".rst", ".md"]

# Sort autodoc members by source to keep the numbering correct.
autodoc_member_order = "bysource"


def build_checker_docs(app) -> None:
    """Automatically build documentation from the available checker functions."""
    nos_dir = Path("./nos")
    env = Environment(loader=FileSystemLoader("."))
    for nos, checks in Checker.checks.items():
        nos_template_file = env.get_template("checks.j2")
        rendered_template = nos_template_file.render(nos=str(nos), checks=checks)

        with open(nos_dir / f"{str(nos)}.rst", "w") as f:
            f.write(rendered_template)

    index_template_file = env.get_template("checks_index.j2")
    rendered_index = index_template_file.render(nos_list=Checker.checks.keys())
    with open(nos_dir / "index.rst", "w") as f:
        f.write(rendered_index)


build_checker_docs(None)
