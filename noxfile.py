import nox

# If using conda, then be sure to be in the nox environment different from "base" before running this file.

@nox.session(python=None)
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)