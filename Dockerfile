FROM python:3.7-slim-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY Pipfile.lock .
RUN apt-get update && \
    pip install pipenv && \
    pipenv sync --clear

EXPOSE 8000

COPY . .

CMD pipenv run python src/manage.py migrate && \
   (pipenv run python src/manage.py runserver 0.0.0.0:8000 & \
    pipenv run python src/manage.py runbot)
