# SSc-MIM — top-level Makefile
#
# Self-documenting: `make` or `make help` prints all targets.

.DEFAULT_GOAL := help
SHELL := /bin/bash
PYTHON ?= python3
CONDA  ?= mamba

CELLDESIGNER_DIR := curation/celldesigner
SPECS_DIR        := docs/module_specs
BIB_FILE         := curation/pubmed_corpus.bib

.PHONY: help setup setup-conda validate specs-check bib-check pilot lint all clean

help:  ## Show this help.
	@awk 'BEGIN {FS = ":.*## "; printf "\nUsage: make \033[36m<target>\033[0m\n\nTargets:\n"} \
	  /^[a-zA-Z0-9_-]+:.*?## / { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf "\n"

setup: setup-conda  ## Create / update the conda env from environment.yml.

setup-conda:  ## Create or update the sscmim conda env.
	@if $(CONDA) env list | grep -q '^sscmim '; then \
	  echo ">> updating env sscmim"; \
	  $(CONDA) env update -n sscmim -f environment.yml --prune; \
	else \
	  echo ">> creating env sscmim"; \
	  $(CONDA) env create -f environment.yml; \
	fi
	@echo ">> done. Activate with: conda activate sscmim"

validate:  ## Run libSBML validation on every XML under curation/celldesigner/.
	$(PYTHON) scripts/validate_sbml.py $(CELLDESIGNER_DIR)

specs-check:  ## Lint docs/module_specs/M*.md (consistency + vocabulary).
	$(PYTHON) scripts/check_module_specs.py $(SPECS_DIR)

bib-check:  ## Lint curation/pubmed_corpus.bib for TODO PMIDs and missing fields.
	$(PYTHON) scripts/check_bib.py $(BIB_FILE)

pilot:  ## Run the Reactome import pilot for M2 (TGF-beta).
	$(PYTHON) scripts/reactome_pilot.py --pathway R-HSA-2173789 --module M2

harmonise:  ## Run post-process + harmonise on all *.celldesigner.xml imports.
	@for f in curation/imports/*/*/*.celldesigner.xml; do \
	  case "$$f" in *processed*|*harmonised*) continue;; esac; \
	  echo "==> $$f"; \
	  $(PYTHON) scripts/post_process_reactome.py "$$f"; \
	  $(PYTHON) scripts/harmonise_imports.py "$${f%.xml}.processed.xml"; \
	done

seed:  ## Re-seed curation/annotations/species_annotations.tsv from imports.
	$(PYTHON) scripts/seed_species_from_imports.py --rewrite

m3-fetch:  ## Fetch Notch1 signaling (R-HSA-1980143) for M3.
	$(PYTHON) scripts/reactome_pilot.py --pathway R-HSA-1980143 --module M3

lint: specs-check bib-check  ## Run all repo-content linters (no SBML files needed).

all: lint validate  ## Lint everything and validate SBML.

clean:  ## Remove transient files (Python caches, notebook checkpoints).
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} +
	@echo ">> cleaned."
