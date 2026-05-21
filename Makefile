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

integrate:  ## Merge harmonised XMLs into SSc_MIM_integrated.xml.
	$(PYTHON) scripts/integrate_modules.py

pmids:  ## Mine PMIDs from Reactome SBML; seed bib + reaction_evidence.tsv.
	$(PYTHON) scripts/extract_pmids_from_biopax.py

network:  ## Run network analysis (centrality + hubs + communities). Needs networkx.
	$(PYTHON) scripts/network_analysis.py

sink-check:  ## Sink-node connectivity audit on the integrated map.
	$(PYTHON) scripts/sink_connectivity.py

crosstalk:  ## Regenerate docs/crosstalk_matrix.md from module specs.
	$(PYTHON) scripts/generate_crosstalk_scaffold.py

phase3:  integrate pmids crosstalk network sink-check  ## Run the whole Phase 3 automation pipeline.
	@echo ">> Phase 3 AUTO lane complete."

bib-lookup:  ## Fill BibTeX entries via NCBI E-utils (needs network).
	$(PYTHON) scripts/bib_lookup.py

preflight:  ## MINERVA-readiness checklist for the integrated map.
	$(PYTHON) scripts/minerva_preflight.py

ssc-stubs:  ## Generate SSc-specific Tier-1 species stubs per module.
	$(PYTHON) scripts/ssc_additions_template.py

figures:  ## Render preview figures F2 / F3 (uses .venv if matplotlib not in PYTHON).
	@if $(PYTHON) -c "import matplotlib" 2>/dev/null; then \
	  $(PYTHON) scripts/render_figures.py; \
	elif [ -x .venv/bin/python ]; then \
	  .venv/bin/python scripts/render_figures.py; \
	else \
	  echo "matplotlib not installed in PYTHON or .venv; run: $(PYTHON) -m pip install matplotlib"; exit 2; \
	fi

abstract:  ## Draft the ACR abstract scaffold from analysis outputs.
	$(PYTHON) scripts/draft_abstract.py

wire:  ## Apply SSc-specific Tier-1 curation to the integrated map.
	$(PYTHON) scripts/wire_ssc_tier1.py

druggable:  ## Cross-reference top hubs with DGIdb (drug-target prioritisation).
	$(PYTHON) scripts/druggable_hubs.py

tabib-probe:  ## Check what's available on GEO for Tabib 2021 (GSE138669).
	$(PYTHON) scripts/fetch_tabib.py --probe

tabib-fetch:  ## Download the Tabib GSE138669 raw counts (594 MB).
	$(PYTHON) scripts/fetch_tabib.py --untar

overlay:  ## Build scRNAseq overlay (real if data present, synthetic-grounded otherwise).
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/build_overlay.py; \
	else $(PYTHON) scripts/build_overlay.py; fi

overlay-multi:  ## Multi-dataset overlay; v1.1 mixed-effects DEG + BH-FDR (--deg-backend wilcoxon-v10 for legacy).
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/build_overlay_multi.py; \
	else $(PYTHON) scripts/build_overlay_multi.py; fi

deg-test:  ## Smoke-test scripts/deg_mixed_effects.py (no data needed).
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/tests/test_deg_mixed_effects.py; \
	else $(PYTHON) scripts/tests/test_deg_mixed_effects.py; fi

pytest:  ## Run the full pytest suite (12 tests under scripts/tests/, no data needed).
	@if [ -x .venv/bin/python ]; then .venv/bin/python -m pytest -q; \
	else $(PYTHON) -m pytest -q; fi

novelty:  ## E18 — MIM vs Reactome/KEGG Jaccard; refresh analysis/network/novelty*.
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/compute_novelty.py; \
	else $(PYTHON) scripts/compute_novelty.py; fi

m3-vascular:  ## E8 — M3 panel × Gur vascular/pericyte clusters; F5 supplementary.
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/m3_vascular_subset.py; \
	else $(PYTHON) scripts/m3_vascular_subset.py; fi

aucell-test:  ## Smoke-test scripts/score_aucell.py (no data needed).
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/tests/test_score_aucell.py; \
	else $(PYTHON) scripts/tests/test_score_aucell.py; fi

aucell:  ## Score donors with AUCell + Z-score (needs a pseudobulk TSV).
	@if [ ! -f analysis/overlay/pseudobulk_multi.tsv ]; then \
	  echo "Missing analysis/overlay/pseudobulk_multi.tsv. Run 'make overlay-multi' first."; exit 2; \
	fi
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/score_aucell.py --pseudobulk analysis/overlay/pseudobulk_multi.tsv; \
	else $(PYTHON) scripts/score_aucell.py --pseudobulk analysis/overlay/pseudobulk_multi.tsv; fi

clinical-fetch:  ## Pull GEO series_matrix.txt for the 4 datasets; emit donor_metadata.tsv.
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/fetch_clinical_metadata.py; \
	else $(PYTHON) scripts/fetch_clinical_metadata.py; fi

clinical-correl:  ## Spearman ρ between AUCell scores and clinical vars (gap-aware).
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/clinical_correlation.py; \
	else $(PYTHON) scripts/clinical_correlation.py; fi

demographic-match:  ## Propensity matching SSc vs HC on age/sex (gap-aware).
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/demographic_match.py; \
	else $(PYTHON) scripts/demographic_match.py; fi

clinical-test:  ## Smoke-test clinical_correlation.py and demographic_match.py.
	@if [ -x .venv/bin/python ]; then .venv/bin/python scripts/tests/test_clinical_correlation.py; \
	else $(PYTHON) scripts/tests/test_clinical_correlation.py; fi

boolean:  ## CaSQ Boolean inference -> SBML-qual for GINsim/BioLQM/MaBoSS.
	@if [ -x .venv/bin/python ]; then PATH=".venv/bin:$$PATH" $(PYTHON) scripts/boolean_inference.py; \
	else $(PYTHON) scripts/boolean_inference.py; fi

release:  ## Pre-flight a v1.x release (checks + CHANGELOG; doesn't tag).
	$(PYTHON) scripts/release_prep.py

lint: specs-check bib-check  ## Run all repo-content linters (no SBML files needed).

auto:  lint validate harmonise seed integrate pmids crosstalk ssc-stubs wire network sink-check druggable overlay boolean preflight figures abstract  ## Run the entire AUTO lane end-to-end.
	@echo ">> Full AUTO pipeline complete."

all: lint validate  ## Lint + validate SBML (compatibility alias).

clean:  ## Remove transient files (Python caches, notebook checkpoints).
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} +
	@echo ">> cleaned."
