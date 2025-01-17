command:
	pipenv run python src/manage.py ${c}

dev:
	make command c="runserver 127.0.0.1:8000"

run:
	cd src && pipenv run gunicorn -c config/gunicorn.conf.py config.wsgi:application

bot:
	make command c="runbot"

migrate:
	make command c="migrate ${o}"

migration:
	make command c="makemigrations -n ${n}"

superuser:
	make command c="createsuperuser"

collectstatic:
	make command c="collectstatic --no-input --clear"

shell:
	make command c="shell"

debug:
	make command c="debug"

sql:
	make command c="debugsqlshell"

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
	docker-compose run app make check_lint

up:
	docker-compose up -d

rm:
	docker-compose stop
	docker-compose rm -f

build:
	docker-compose build

down:
	docker-compose down

exec:
	docker-compose exec app ${c}

bash:
	make exec c="bash"

pull:
	docker-compose pull

push:
	docker-compose push

test_build:
	docker-compose run --rm app make test

test:
	cd src && pipenv run pytest --disable-warnings

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
