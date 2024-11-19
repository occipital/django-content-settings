# How to Contribute to the Project

## What Can I Do?

- Review the [List of Open Tickets](https://github.com/occipital/django-content-settings/issues) to find tasks or issues to work on.
- Test the project and write tests to increase test coverage. Use the command `make test-cov` to check coverage.

---

## How to Set Up the Environment

Follow these steps to set up your development environment:

```bash
pre-commit install
make init
make test
```

---

## How to Set Up the `cs_test` Project

The `cs_test` project/folder is used for testing and verifying the front-end portion of the project.

1. After setting up the environment, run:
   ```bash
   make cs-test-migrate
   ```
   This creates a database for the project.

2. To start a local runserver with content settings configured:
   ```bash
   make cs-test
   ```

3. To access the content settings shell:
   ```bash
   make cs-test-shell
   ```

---

### Docker Container for Testing Different Backends

To test and adjust the MySQL backend, a Docker Compose file is included for the current `cs_test` project.

- Build the Docker container:
  ```bash
  make cs-test-docker-build
  ```

- Start the container:
  ```bash
  make cs-test-docker-up
  ```

Feel free to modify the Docker setup to suit your testing needs.

---

## When Updating Documentation

Creating high-quality documentation is challenging, and improvements are always welcome! If you’re contributing to documentation, please keep the following in mind:

- Use terms consistently from the [Glossary](glossary.md), as the system introduces many new concepts.
- If you update docstrings (documentation inside Python files), run:
  ```bash
  make mdsource
  ```
  This collects the updated docstrings into [source.md](source.md).

---

## Tests

It's essential to create tests for new functionality and improve tests for existing functionality. Submitting a pull request with additional tests is highly encouraged.

### Testing Tools

We use the following modules for testing:

```
pytest = "^7.4.3"
pytest-mock = "^3.12.0"
pytest-django = "^4.7.0"
django-webtest = "^1.9.11"
pytest-cov = "^4.1.0"
nox = "^2023.4.22"
```

### Testing Commands

The following `make` commands can help streamline your testing process:

- `make test`: Runs all tests in the current Poetry environment.
- `make test-full`: Runs tests with extended settings.
- `make test-min`: Runs tests with minimal settings to limit functionality.
- `make test-cov`: Checks the current test coverage.
- `make test-cov-xml`: Generates test coverage in `cov.xml`, which can help identify untested areas.
- `make test-nox`: (Takes longer) Runs tests under all supported Python and Django versions.
- `make test-nox-oldest`: Runs tests under the oldest supported combination of Python and Django versions.

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
