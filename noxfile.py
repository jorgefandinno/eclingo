import nox

# If using conda, then be sure to be in the nox environment different from "base" before running this file.

@nox.session(python=None)
def typecheck(session):
    session.install("-r", "requirements.txt", "mypy")
    session.run("mypy", "src/eclingo")

@nox.session(python=None)
def tests(session):
    args = session.posargs or ["--cov"]
    # session.run("poetry", "install", external=True)
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run("pytest", *args)