ARG     PYTAG=3.7.3-stretch
￼FROM    python:${PYTAG}

WORKDIR /app
COPY    requirements.txt ./
RUN     pip install -r /requirements.txt

COPY    . ./
RUN     pip install .

WORKDIR /hypercane-work
