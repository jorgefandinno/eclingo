"""
If using conda, then be sure to be in the nox environment different from "base" before running this file.

To run all tests: nox -Rs all_tests
The above also runs coverage.
The follwing only run a subset of tests and they do not run coverage.
To run only fast test: nox -Rs tests
To run only slow test: nox -Rs slow_tests
"""
import nox


@nox.session
def format(session: nox.Session):
    session.install("black", "isort")
    args = session.posargs if session.posargs else ["src/eclingo", "tests"]
    session.run("isort", "--profile", "black", "src/eclingo")
    session.run("black", *args)


@nox.session(python=None)
def typecheck(session: nox.Session):
    session.install("mypy")
    session.install("-r", "requirements.txt")
    session.run("mypy", "--implicit-optional", "src/eclingo")


@nox.session(python=None)
def all_tests(session: nox.Session):
    session.notify("tests")
    session.notify("slow_tests")
    session.notify("coverage")


@nox.session(python=None)
def tests(session: nox.Session):
    session.install("coverage")
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run(
        "coverage",
        "run",
        "--data-file",
        ".coverage_fast",
        "-m",
        "unittest",
        "tests/test_reification.py",
        "tests/test_reification2.py",
        "tests/test_reification3.py",
        "tests/test_reification4.py",
        "tests/test_reification5.py",
        # "tests/test_app.py",
        "tests/test_eclingo.py",
        # "tests/test_eclingo_examples.py",
        "tests/test_grounder.py",
        "tests/test_generator_reification.py",
        "tests/test_literals.py",
        "tests/test_internal_control_ground_program.py",
        "tests/test_parsing.py",
        "tests/test_show.py",
        "tests/test_solver_reification.py",
        "tests/test_worldview_builder_reification.py",
        "tests/test_tester_reification.py",
        "tests/test_theory_atom_parser.py",
        "tests/test_transformers.py",
        "tests/test_util.py",
        "-v",
    )


@nox.session(python=None)
def slow_tests(session: nox.Session):
    session.install("coverage")
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run(
        "coverage",
        "run",
        "--data-file",
        ".coverage_slow",
        "-m",
        "unittest",
        "tests/test_app.py",
        "tests/test_eclingo_examples.py",
        "-v",
    )


# Session for individual new test implementation
# @nox.session(python=None)
# def tests(session: nox.Session):
#     session.install("coverage")
#     session.install("-r", "requirements.txt")
#     session.install("-e", ".")
#     session.run("coverage", "run", "-m", "unittest",
#                 "tests/test_app_reification.py",
#                 "-v")
#     session.notify("coverage")


@nox.session(python=None)
def coverage(session: nox.Session):
    session.install("coverage")
    omit = ["src/eclingo/__main__.py", "tests/*", "helper_test/*"]
    session.run(
        "coverage",
        "combine",
        ".coverage_fast",
        ".coverage_slow",
    )
    session.run(
        "coverage",
        "report",
        "--sort=cover",
        "--fail-under=99",
        "--omit",
        ",".join(omit),
    )


@nox.session
def pylint(session: nox.Session):
    session.install("-r", "requirements.txt", "pylint")
    session.run("pylint", "src/eclingo")


@nox.session
def lint_flake8(session: nox.Session):
    session.install("flake8", "flake8-black", "flake8-isort")
    session.run("flake8", "src/eclingo")
