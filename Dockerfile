FROM python:3.9.2-slim-buster

ADD . /python-flask
WORKDIR /python-flask
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY catalog ./catalog

