import nox

# If using conda, then be sure to be in the nox environment different from "base" before running this file.

@nox.session
def format(session):
    session.install("black", "isort")
    args = session.posargs if session.posargs else ["src/eclingo"]
    session.run("isort", "--profile", "black", "src/eclingo")
    session.run("black", *args)

@nox.session(python=None)
def typecheck(session):
    session.install("-r", "requirements.txt", "mypy")
    session.run("mypy", "src/eclingo")


@nox.session(python=None)
def tests(session):
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run("coverage", "run", "-m", "unittest")
    session.notify("coverage")


@nox.session(python=None)
def coverage(session):
    omit = ["src/eclingo/__main__.py", "tests/*", "helper_test/*"]
    session.run(
        "coverage",
        "report",
        "--sort=cover",
        "--fail-under=100",
        "--omit",
        ",".join(omit),
    )
