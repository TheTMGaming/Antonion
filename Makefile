command:
	pipenv run python src/manage.py ${c}

run_api:
	make command c="runserver 0.0.0.0:8000"

run_bot:
	make command c="runbot"

migrate:
	make command c="migrate"

makemigrations:
	make command c="makemigrations"

createsuperuser:
	make command c="createsuperuser"

collectstatic:
	make command c="collectstatic --no-input"

shell:
	make command c="shell"

debug:
	make command c="debug"

piplock:
	pipenv install

lint:
	pipenv run isort .
	pipenv run flake8 --config setup.cfg
	pipenv run black --config pyproject.toml .

check_lint:
	pipenv run isort --check --diff .
	pipenv run flake8 --config setup.cfg
	pipenv run black --check --config pyproject.toml .

lint_build:
	docker run --rm "${IMAGE_NAME}" make check_lint

dev:
	docker-compose up --build

up:
	docker-compose up -d --build

build:
	docker-compose build

down:
	docker-compose down

stop:
	docker-compose rm -sf api
	docker-compose rm -sf bot

exec:
	docker-compose exec api ${c}

bash:
	make exec c="bash"

pull:
	docker pull ${IMAGE_NAME}

push:
	docker push ${IMAGE_NAME}

test:
	echo "test"