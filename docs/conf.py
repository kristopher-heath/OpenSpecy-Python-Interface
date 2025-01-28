# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OpenSpecy Python Interface'
copyright = '2024, Kristopher Heath'
author = 'Kristopher Heath'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# =============================================================================
import sys
import os
# from pathlib import Path
#
# sys.path.insert(0, str(Path('', 'src').resolve()))
# =============================================================================
# sys.path.insert(0, os.path.abspath(r"C:\Users\kheath\.spyder-py3\Scripts\For GitHub"))

extensions = ['sphinx.ext.napoleon', 'autoapi.extension']

autoapi_dirs = ['../openspecy']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
