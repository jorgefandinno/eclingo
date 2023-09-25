"""
Main module providing the application logic.
"""

import sys
from typing import Sequence

from clingo.application import Flag, clingo_main

from eclingo.config import AppConfig
from eclingo.control import Control

from . import __version__

_FALSE = ["0", "no", "false"]
_TRUE = ["1", "yes", "true"]

reification_flag = Flag(True)


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

        self.config.eclingo_reification = reification_flag.flag

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
        print(sys.argv)
        if "--output=reify" in set(arg.replace(" ", "") for arg in sys.argv):
            return

        eclingo_control.preprocess()
        eclingo_control.prepare_solver()

        sys.stdout.write("Solving...\n")
        wv_number = 0
        for wv_number, world_view in enumerate(eclingo_control.solve(), 1):
            sys.stdout.write("World view: %d\n" % wv_number)
            sys.stdout.write(str(world_view))
            sys.stdout.write("\n")
        if wv_number > 1:
            sys.stdout.write("SATISFIABLE\n")
        else:
            sys.stdout.write("UNSATISFIABLE\n")


def main():
    sys.argv.append("--outf=3")
    application = Application()
    result = clingo_main(application, sys.argv[1:])
    return int(result)
