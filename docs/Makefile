# Minimal makefile for Sphinx documentation
#

SPHINXOPTS ?=
SPHINXBUILD ?= uv run --group docs sphinx-build
SOURCEDIR = .
BUILDDIR = _build

.PHONY: help clean html

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	@rm -rf "$(BUILDDIR)"

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
