# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openspecy_python_interface', '_version.py')
with open(version_file) as f:
    exec(f.read())


project = 'OpenSpecy Python Interface'
copyright = '2024, Kristopher Heath'
author = 'Kristopher Heath'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# =============================================================================

extensions = ['sphinx.ext.napoleon', 'autoapi.extension']

autoapi_dirs = ['../openspecy_python_interface']

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'bizstyle'
html_theme_options = {'sidebarwidth': 200 }
html_static_path = ['_static']
