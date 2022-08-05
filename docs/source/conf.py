# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'abseil/abseil-py'
copyright = '2022, abseil/abseil-py authors'
author = 'abseil/abseil-py authors'

release = '1.2'
version = '1.2.0'

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
    'sphinxcontrib.apidoc', # automatically convert .py sources to .rst docs. 
    'm2r2',                 # for .md files
]

# sphinxcontrib.apidoc vars
apidoc_module_dir = '../../absl'
apidoc_output_dir = '.'
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

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))       # access to README.md
sys.path.insert(0, os.path.abspath('../../absl'))  # access to python source code
