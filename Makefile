init:
	poetry install

test-min:
	TESTING_SETTINGS=min poetry run pytest

test-full:
	TESTING_SETTINGS=full poetry run pytest

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
	poetry run poetry run python cs_test/manage.py runserver

cs-test-migrate:
	poetry run poetry run python cs_test/manage.py migrate

cs-test-shell:
	poetry run poetry run python cs_test/manage.py shell