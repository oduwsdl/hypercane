ARG     PYTAG=3.7.3-stretch
￼FROM    python:${PYTAG}

LABEL   org.opencontainers.image.title="Hypercane" \
        org.opencontainers.image.description="A framework of algorithms for sampling mementos from a collection" \
        org.opencontainers.image.licenses="MIT License" \
        org.opencontainers.image.source="https://github.com/oduwsdl/hypercane" \
        org.opencontainers.image.documentation="https://hypercane.readthedocs.io/" \
        org.opencontainers.image.vendor="Web Science and Digital Libraries Research Group at Old Dominion University" \
        org.opencontainers.image.authors="Shawn M. Jones <https://github.com/shawnmjones>"

WORKDIR /app
COPY    requirements.txt ./
RUN     pip install -r /requirements.txt

COPY    . ./
RUN     pip install .

WORKDIR /hypercane-work
