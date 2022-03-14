dev:
	python src/manage.py runserver localhost:8000

bot:
	python src/manage.py runbot

dev_migrate:
	python src/manage.py migrate $(if $m, api $m,)

dev_makemigrations:
	python src/manage.py makemigrations

dev_createsuperuser:
	python src/manage.py createsuperuser

dev_collectstatic:
	python src/manage.py collectstatic --no-input

dev_command:
	python src/manage.py ${c}

dev_shell:
	python src/manage.py shell

dev_debug:
	python src/manage.py debug

dev_piplock:
	pipenv install

lint:
	isort .
	flake8 --config setup.cfg
	black --config pyproject.toml .

check_lint:
	isort --check --diff .
	flake8 --config setup.cfg
	black --check --config pyproject.toml .

up:
	docker-compose up -d --build

check_app:
	docker-compose up --build

build:
	docker-compose build

down:
	docker-compose down

exec:
	docker-compose exec app ${c}

bash:
	make exec c="bash"

migrate:
	make exec c="pipenv run python src/manage.py migrate $(if $m, api $m,)"

makemigrations:
	make exec c="pipenv run python src/manage.py makemigrations"

createsuperuser:
	make exec c="pipenv run python src/manage.py createsuperuser"

collectstatic:
	make exec c="pipenv run python src/manage.py collectstatic --no-input"

command:
	make exec c="pipenv run python src/manage.py ${c}"

shell:
	make exec c="pipenv run python src/manage.py shell"

debug:
	make exec c="pipenv run python src/manage.py debug"

piplock:
	make exec c="pipenv run app pipenv install"
