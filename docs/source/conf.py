"""Sphinx config file for https://github.com/abseil/abseil-py."""

import os
import sys

# -- Project information
project = 'Abseil Python Common Libraries'
copyright = '2022, Abseil'  # pylint: disable=redefined-builtin
author = 'The Abseil Authors'

release = ''
version = ''

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.coverage',
    'sphinxcontrib.apidoc',  # convert .py sources to .rst docs.
    'm2r2',                  # for .md files
]

# sphinxcontrib.apidoc vars
apidoc_module_dir = '../../absl'
apidoc_output_dir = '.'
apidoc_toc_file = False
apidoc_excluded_paths = [
    '*/tests/*',
    'tests/*',
]
apidoc_separate_modules = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

sys.path.insert(0, os.path.abspath('../..'))       # access to README.md
sys.path.insert(0, os.path.abspath('../../absl'))  # access to python sources
