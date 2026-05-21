# SSc-MIM revision v1.1 container
#
# Built on micromamba so the conda environment.yml is the single source
# of truth for the Python stack. The image installs the sscmim env, sets
# the working directory to /workspace, and defaults to `make help` so
# that `docker run -it ghcr.io/nurtal/idt_ssc_map:v1.1` is self-describing.
#
# Build with the GHCR workflow (.github/workflows/docker.yml) on every
# vX.Y tag; reproduce locally via:
#
#   docker build -t idt_ssc_map:v1.1 .
#   docker run --rm -it -v "$(pwd)":/workspace idt_ssc_map:v1.1 make help
#
# The image does NOT bundle the four GEO source datasets (~1.2 GB raw);
# users are expected to mount or download them separately. See
# data/MIRROR.md for the Zenodo-mirrored SHA-256 manifest (E15).

ARG MAMBA_DIGEST=sha256:7dca8d0b6c2c8e5fc1ee2c41e89a8f9d5e6e96b1a2f04dba0a8c2e6e3a13a8d5
FROM mambaorg/micromamba:1.5.6

LABEL org.opencontainers.image.title="SSc-MIM"
LABEL org.opencontainers.image.description="Curated SBGN-compliant Molecular Interaction Map of dcSSc skin fibrosis + scRNA-seq overlay pipeline. Revision v1.1 (npj Syst Biol Appl)."
LABEL org.opencontainers.image.source="https://github.com/Nurtal/IDT_SSc_map"
LABEL org.opencontainers.image.licenses="MIT (code), CC-BY-4.0 (map content)"
LABEL org.opencontainers.image.authors="Nathan Foulquier <nathan.foulquier@inserm.fr>"

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    make \
    procps \
    && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER

WORKDIR /workspace

# Copy the env spec first so layer caching reuses the conda install
# across iterative source-only changes.
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml \
    && micromamba clean --all --yes \
    && rm /tmp/environment.yml

# Make the env available for non-interactive `make` invocations.
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ENV PATH=/opt/conda/bin:$PATH

# Copy the project tree.
COPY --chown=$MAMBA_USER:$MAMBA_USER . /workspace

# Smoke check during build — fails the image if the core stack is broken.
RUN python -c "import scanpy, statsmodels, networkx, libsbml; print('sscmim stack ok')"

CMD ["make", "help"]
