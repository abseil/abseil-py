# Minimal makefile for Sphinx documentation
#
# To generate html docs locally:
#   Recommend doing this from a virtual environment:
#   $ sudo apt-get install virtualenv python3-venv
#   $ virtualenv myproject  # or python3 -m venv myproject
#   $ source myproject/bin/activate
#
#   Then install sphinx packages (if running locally)
#   $ pip install m2r2
#   $ pip install sphinxcontrib-apidoc
#   $ pip install sphinx-rtd-theme
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SOURCEDIR      = ../absl
RSTDIR         = source
HTMLDIR        = build
HTMLDIR      = build
# If you change the conf.py apidoc_excluded_paths, you need to update
# the excluded paths in APIDOC_EXCLUDE too.  The paths are relative
# to the docs/ directory (if you want to filter out absl/tests you need
# to use "../*/tests".)
APIDOC_EXCLUDE = ../*/*/tests/* ../*/tests/*
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc

# Build .rst files for all Python sources in SOURCEDIR.
# This rule isn't called by readthedocs, its only used for manual testing.
rstfiles:
	@$(SPHINXAPIDOC) -o $(RSTDIR) $(SOURCEDIR) $(APIDOC_EXCLUDE)

# Run after "make rstfiles"
# You can review sphinx generated files in docs/build directory.
htmlfiles:
	@$(SPHINXBUILD) -b html -c $(RSTDIR) $(RSTDIR) $(HTMLDIR)
