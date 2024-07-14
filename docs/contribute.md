[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# How to contribute to the project

## What can I do

* [List of opened tickets](https://github.com/occipital/django-content-settings/issues).
* testing and writing tests. Increasing test coverage. `make test-cov`

## How to setup env

```
pre-commit install
poetry install
make test

```

## How to setup cs_test project

For testing and checking front-end part of the project we have cs_test project/folder

After setting up the env you need `make cs-test-migrate` to create a db for the project, then you can `make cs-test` to start local runserver with content settings configured or `make cs-test-shell` to access to shell of the content settings.

## When you update documentation

Creating good documentation is hard, and there is always room for making it better. I would really appreciate you help here, but don't forget a couple of things:

* make sure using terms from our [Glossary](glossary.md), as the system itself introduce a lot of new terms
* when you update doc strings (documentation inside py-files), do `make mdsource` to collect it in [source.md](source.md)

## Tests

It is important not only creating test for new functionality or new code, but also improve tests for already written functionality. So it is good to have just new tests in a pull-request.

For creating tests we use the following modules:

```
pytest = "^7.4.3"
pytest-mock = "^3.12.0"
pytest-django = "^4.7.0"
django-webtest = "^1.9.11"
pytest-cov = "^4.1.0"
nox = "^2023.4.22"
```

Some of the make-commands that we have already can make your testing process more confortable:

* `make test` just run all of the tests in current poetry env
* `make test-cov` to check the corrent test covarage
* `make test-cov-xml` generate test covarage in `cov.xml` which can me later used for seing places with no tests
* `make test-nox` (will be long) - running tests under all supported python versions and Django versions
* `make test-nox-oldest` - just run all of the tests under the oldes combination


_PS: [the ticket](https://github.com/occipital/django-content-settings/issues/5)_