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
    session.install("mypy")
    session.install("-r", "requirements.txt")
    session.run("mypy", "src/eclingo")


@nox.session(python=None)
def tests(session):
    session.install("coverage")
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run("coverage", "run", "-m", "unittest", "tests/test_reification4.py", "-v")
    session.notify("coverage")


@nox.session(python=None)
def coverage(session):
    session.install("coverage")
    omit = ["src/eclingo/__main__.py", "tests/*", "helper_test/*"]
    session.run(
        "coverage",
        "report",
        "--sort=cover",
        "--fail-under=100",
        "--omit",
        ",".join(omit),
    )


@nox.session
def pylint(session):
    session.install("-r", "requirements.txt", "pylint")
    session.run("pylint", "src/eclingo")


@nox.session
def lint_flake8(session):
    session.install("flake8", "flake8-black", "flake8-isort")
    session.run("flake8", "src/eclingo")
