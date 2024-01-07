import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("django", ["3.2", "4.2", "5.0"])
@nox.parametrize("pyyaml", [True, False])
def tests(session, django, pyyaml):
    if django == "5.0" and session.python in (
        "3.8",
        "3.9",
    ):
        return
    session.install(f"django=={django}")
    if pyyaml:
        session.install("pyyaml")
    session.run("pytest")
