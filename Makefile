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

exec:
	docker-compose exec api ${c}

bash:
	make exec c="bash"

migrate:
	make exec c="pipenv run python src/manage.py migrate ${c}"

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
