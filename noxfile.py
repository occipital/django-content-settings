import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"])
@nox.parametrize("django", ["3.2", "4.2", "5.0", "5.1"])
@nox.parametrize("pyyaml", [True, False])
def tests(session, django, pyyaml):
    if django in ["5.0", "5.1"] and session.python in (
        "3.8",
        "3.9",
    ):
        return
    session.install(f"django=={django}")
    if pyyaml:
        session.install("PyYAML")
    if session.python in ["3.12", "3.13"]:
        session.install("setuptools")
    session.install("pytest~=7.4.3")
    session.install("pytest-mock~=3.12.0")
    session.install("pytest-django~=4.7.0")
    session.install("django-webtest~=1.9.11")
    session.install("-e", ".")
    for testing_settings in ["min", "full", "normal"]:
        for precache in (True, False):
            session.run(
                "pytest",
                env={
                    "TESTING_SETTINGS": testing_settings,
                    **({"TESTING_PRECACHED_PY_VALUES": "1"} if precache else {}),
                },
            )
