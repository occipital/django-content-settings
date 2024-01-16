test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=content_settings

test-cov-xml:
	poetry run pytest --cov=content_settings --cov-report xml:cov.xml

test-nox:
	poetry run nox

doc:
	poetry run mkdocs serve

publish:
	poetry publish --build

cs-test:
	poetry run poetry run python cs_test/manage.py runserver