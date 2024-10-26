FROM python:3.12

WORKDIR /app

COPY content_settings /app/content_settings
COPY cs_test /app/cs_test
COPY tests /app/tests

COPY Makefile /app/Makefile
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock


RUN pip install --no-cache-dir poetry
RUN touch README_SHORT.md
RUN make init
RUN poetry run pip install --no-cache-dir mysqlclient

EXPOSE 8000

