command:
	pipenv run python src/manage.py ${c}

run:
	make command c="runserver 0.0.0.0:8000"

bot:
	make command c="runbot"

migrate:
	make command c="migrate" ${o}

migrations:
	make command c="makemigrations"

superuser:
	make command c="createsuperuser"

static:
	make command c="collectstatic --no-input"

shell:
	make command c="shell"

debug:
	make command c="debug"

piplock:
	pipenv install

lint:
	pipenv run isort . & \
	pipenv run flake8 --config setup.cfg & \
	pipenv run black --config pyproject.toml .

check_lint:
	pipenv run isort --check --diff . & \
	pipenv run flake8 --config setup.cfg & \
	pipenv run black --check --config pyproject.toml .

lint_build:
	docker run --rm "${IMAGE_NAME}" make check_lint

dev:
	docker-compose -f docker-compose.local.yml up -d --build

up:
	docker-compose up -d --build

restart:
	docker-compose rm -sf app
	make up

build:
	docker-compose build

down:
	docker-compose down

exec:
	docker-compose exec app ${c}

bash:
	make exec c="bash"

pull:
	docker pull ${IMAGE_NAME}

push:
	docker push ${IMAGE_NAME}

test:
	echo "test"