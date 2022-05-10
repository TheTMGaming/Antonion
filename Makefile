command:
	pipenv run python src/manage.py ${c}

run:
	make command c="runserver 0.0.0.0:8000"

bot:
	make command c="runbot"

migrate:
	make command c="migrate ${o}"

migration:
	make command c="makemigrations ${o}"

superuser:
	make command c="createsuperuser"

static:
	make command c="collectstatic --no-input --clear"

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

test_build:
	docker-compose run --rm app make test

test:
	cd src && pipenv run pytest --disable-warnings --no-summary

unit:
	cd src && pipenv run pytest -m unit --disable-warnings

smoke:
	cd src && pipenv run pytest -m smoke --disable-warnings

integration:
	cd src && pipenv run pytest -m integration --disable-warnings

performance:
	cd && \
	docker run \
    -v %cd%/src/tests/performance:/var/loadtest \
    --net host \
    -it \
    --entrypoint "/bin/bash" \
    direvius/yandex-tank
