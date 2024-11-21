init:
	poetry install

test-min:
	TESTING_SETTINGS=min poetry run pytest

test-cache:
	TESTING_DISABLE_PRECACHED_PY_VALUES=1 poetry run pytest

test-full:
	TESTING_SETTINGS=full poetry run pytest

test-cache-full:
	TESTING_DISABLE_PRECACHED_PY_VALUES=1 TESTING_SETTINGS=full poetry run pytest

test-cache-min:
	TESTING_DISABLE_PRECACHED_PY_VALUES=1 TESTING_SETTINGS=min poetry run pytest

test:
	poetry run pytest

test-v:
	poetry run pytest -vv -s

test-cov:
	TESTING_SETTINGS=full poetry run pytest --cov=content_settings

test-cov-xml:
	TESTING_SETTINGS=full poetry run pytest --cov=content_settings --cov-report xml:cov.xml

test-nox:
	poetry run nox

test-nox-oldest:
	poetry run nox --session "tests-3.8(pyyaml=True, django='3.2')"

doc:
	poetry run mkdocs serve

mdsource:
	poetry run poetry run python mdsource.py

publish:
	poetry run python set_version.py
	poetry publish --build

cs-test:
	make cs-test-migrate
	poetry run poetry run python cs_test/manage.py runserver 0.0.0.0:8000

cs-test-migrate:
	poetry run poetry run python cs_test/manage.py migrate

cs-test-shell:
	poetry run poetry run python cs_test/manage.py shell

cs-test-docker-build:
	docker compose -f cs_test/docker-compose.yml build

cs-test-docker-up:
	docker compose -f cs_test/docker-compose.yml up