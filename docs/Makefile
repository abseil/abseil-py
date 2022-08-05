# Minimal makefile for Sphinx documentation
#
# To generate html docs locally:
#   Recommend doing this from a virtual environment:
#   $ sudo apt-get install virtualenv python3-venv
#   $ virtualenv myproject  # or python3 -m venv myproject
#   $ source myproject/bin/activate
#
#   Then install sphinx packages (if running locally)
#   $ pip install myst-parser
#   $ pip install sphinxcontrib-apidoc
#   $ pip install sphinx-rtd-theme
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SOURCEDIR     = ../absl
RSTDIR        = source
HTMLDIR      = build
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc

# Build .rst files for all Python sources in SOURCEDIR.
rstfiles:
	@$(SPHINXAPIDOC) -o $(RSTDIR) $(SOURCEDIR) tests

# Run after "make rstfiles"
# You can review sphinx generated files in docs/build directory.
htmlfiles:
	@$(SPHINXBUILD) -b html -c $(RSTDIR) $(RSTDIR) $(HTMLDIR)
