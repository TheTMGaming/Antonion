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
	isort .
	flake8 --config setup.cfg
	black --config pyproject.toml .

check_lint:
	isort --check --diff .
	flake8 --config setup.cfg
	black --check --config pyproject.toml .

dev:
	docker-compose up --build

up:
	docker-compose up -d --build

build:
	docker-compose build --no-cache --force-rm

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
	docker-compose pull "${IMAGE_NAME}"

push:
	docker-compose push "${IMAGE_NAME}"

test:
	echo "stub"