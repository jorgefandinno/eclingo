"""
Main module providing the application logic.
"""

import sys
import time
from typing import Sequence

from clingo.application import clingo_main

from eclingo.config import AppConfig
from eclingo.control import Control

from . import __version__

_FALSE = ["0", "no", "false"]
_TRUE = ["1", "yes", "true"]


class Application:
    """
    Application class that can be used with `clingo.clingo_main` to solve CSP
    problems.
    """

    def __init__(self):
        self.program_name = "eclingo"
        self.version = __version__
        self.config = AppConfig()

    def _parse_string(self, config, attr):
        def parse(value):
            setattr(config, attr, value)  # pragma: no cover
            return True  # pragma: no cover

        return parse

    def register_options(self, options) -> None:
        """
        Register eclingo related options.
        """
        group = "Eclingo Options"

        options.add(
            group=group,
            option="semantics",
            description="Sets eclingo to use an specified semantics",
            parser=self._parse_string(self.config, "eclingo_semantics"),
            argument="<ELP_semantics>",
        )

        options.add(
            group=group,
            option="output-e",
            description="Rewrites the program using reification",
            parser=self._parse_string(self.config, "eclingo_rewritten"),
            argument="<rewritten>",
        )

    def _read(self, path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as file_:
            return file_.read()

    def main(self, control: Control, files: Sequence[str]) -> None:
        """
        Entry point of the application registering the propagator and
        implementing the standard ground and solve functionality.
        """
        if not files:
            files = ["-"]

        eclingo_control = Control(control, self.config)

        for path in files:
            eclingo_control.add_program(self._read(path))

        if self.config.eclingo_rewritten == "rewritten":
            for stm in eclingo_control.rewritten_program[1:]:
                sys.stdout.write(str(stm))
                sys.stdout.write("\n")
            return

        eclingo_control.ground()

        # Command check
        try:
            output_index = sys.argv.index("--output=")
        except ValueError:
            output_index = -1
        if "--output=reify" in sys.argv or (
            output_index >= 0 and sys.argv[output_index + 1] == "reify"
        ):
            return  # pragma: no cover

        eclingo_control.preprocess()
        eclingo_control.prepare_solver()

        sys.stdout.write("Solving...\n")
        wv_number = 0
        for wv_number, world_view in enumerate(eclingo_control.solve(), 1):
            sys.stdout.write("World view: %d\n" % wv_number)
            sys.stdout.write(str(world_view))
            sys.stdout.write("\n")
        if wv_number >= 1:
            sys.stdout.write("SATISFIABLE\n")
        else:
            sys.stdout.write("UNSATISFIABLE\n")

        if int(eclingo_control.control.configuration.stats) > 0:
            sys.stdout.write("\n")  # pragma: no cover
            sys.stdout.write(
                f"Number of candidates: {eclingo_control.solver.number_of_candidates()}\n"
            )  # pragma: no cover


def secondary_main(argv):
    start = time.time()
    sys.argv.append("--outf=3")
    application = Application()
    result = clingo_main(application, argv[1:])
    end = time.time()
    sys.stderr.write(f"\nElapsed time: {end - start}")
    return int(result)


def main():
    return secondary_main(sys.argv)
