import nox

# If using conda, then be sure to be in the nox environment different from "base" before running this file.

@nox.session(python=None)
def typecheck(session):
    session.install("-r", "requirements.txt", "mypy")
    session.run("mypy", "src/eclingo")

@nox.session(python=None)
def tests(session):
    omit = [
        "src/eclingo/__main__.py",
    ]
    tested_files_90 = []
    tested_files_80 = [
        "src/eclingo/literals.py",
        "src/eclingo/prefixes.py",
        "src/eclingo/parsing/transformers/theory_parser_epistemic.py",
    ]
    tested_files_70 = [
        "src/eclingo/parsing/transformers/parser_negations.py",
    ]
    tested_files_60 = [
        "src/eclingo/parsing/transformers/theory_parser_literals.py",
    ]
    # args = session.posargs or ["--cov"]
    # session.run("poetry", "install", external=True)
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    # session.run("pytest", *args)
    session.run("coverage", "run", "-m", "unittest")
    session.run("coverage", "report", "--sort=cover", "--fail-under=100", "--omit", ",".join(tested_files_90 + tested_files_80 + tested_files_70 + tested_files_60 + omit))
    # session.run("coverage", "report", "--sort=cover", "--fail-under=90", "--include", ",".join(tested_files_90))
    session.run("coverage", "report", "--sort=cover", "--fail-under=80", "--include", ",".join(tested_files_80))
    session.run("coverage", "report", "--sort=cover", "--fail-under=70", "--include", ",".join(tested_files_70))
    session.run("coverage", "report", "--sort=cover", "--fail-under=60", "--include", ",".join(tested_files_60))
    session.run("coverage", "report", "--sort=cover", "--omit", ",".join(omit))

        



