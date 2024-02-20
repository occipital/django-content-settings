init:
	poetry install

test:
	poetry run pytest

test-v:
	poetry run pytest -vv -s

test-cov:
	poetry run pytest --cov=content_settings

test-cov-xml:
	poetry run pytest --cov=content_settings --cov-report xml:cov.xml

test-nox:
	poetry run nox

doc:
	poetry run mkdocs serve

publish:
	poetry run python set_version.py
	poetry publish --build

cs-test:
	poetry run poetry run python cs_test/manage.py runserver

cs-test-migrate:
	poetry run poetry run python cs_test/manage.py migrate

cs-test-shell:
	poetry run poetry run python cs_test/manage.py shell