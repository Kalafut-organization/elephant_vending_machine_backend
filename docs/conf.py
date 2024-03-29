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
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'Elephant Vending Machine'
copyright = '2021, Katie Kalafut, Sam Baker, Greta Noeth, Ben Rogers, Issac Wiita, Megan Knox, Riya Lengade, Nick Male, Alex Waibel'
author = 'Sam Baker, Greta Noeth, Ben Rogers, Issac Wiita'

# The full version, including alpha/beta/rc tags
release = '0.2'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinxcontrib.apidoc',
    'sphinx.ext.todo'
]

napoleon_numpy_docstring = False
apidoc_module_dir = '../elephant_vending_machine'
apidoc_output_dir = 'source'
apidoc_separate_modules = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_context = {
    "display_github": True, # Integrate Gitlab
    "github_user": "Kalafut-organization", # Username
    "github_repo": "elephants_cse5911", # Repo name
    "github_version": "master", # Version
    "conf_py_path": "/source/", # Path in the checkout to the docs root
}

# Enable TODOs to show in the documentation
todo_include_todos=True

# Setup function for custom CSS
def setup(app):
    app.add_stylesheet('theme_overrides.css')
