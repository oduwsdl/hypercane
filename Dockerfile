FROM python:3.7.3-stretch

COPY requirements.txt /

RUN pip install -r /requirements.txt

WORKDIR /app

COPY . /app

RUN pip install .

WORKDIR /hypercane-work
