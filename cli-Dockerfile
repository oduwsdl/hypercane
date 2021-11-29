ARG     PYTAG=3.7.3-stretch
FROM    python:${PYTAG}

LABEL   org.opencontainers.image.title="Hypercane" \
        org.opencontainers.image.description="A framework of algorithms for sampling mementos from a collection" \
        org.opencontainers.image.licenses="MIT License" \
        org.opencontainers.image.source="https://github.com/oduwsdl/hypercane" \
        org.opencontainers.image.documentation="https://hypercane.readthedocs.io/" \
        org.opencontainers.image.vendor="Web Science and Digital Libraries Research Group at Old Dominion University" \
        org.opencontainers.image.authors="Shawn M. Jones <https://github.com/shawnmjones>"

WORKDIR /app
RUN     pip install --upgrade pip

COPY    requirements.txt ./
RUN     pip install -r requirements.txt
RUN     python -m spacy download en_core_web_sm

COPY    . ./
RUN pip install .  --use-feature=in-tree-build

WORKDIR /hypercane-work
