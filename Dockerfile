FROM python:3.10-slim-buster

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

EXPOSE 8000

COPY Pipfile .
RUN apt-get update && \
    apt-get install make && \
    pip install pipenv && \
    pipenv install --clear

COPY . .
