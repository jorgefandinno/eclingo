"""
Main module providing the application logic.
"""

import sys
from typing import Sequence

import clingo

from eclingo.config import AppConfig
from eclingo.control import Control
from eclingo.internal_states import internal_control
from eclingo.internal_states.internal_control import InternalStateControl

from . import __version__

# from clingo.application import Flag

_FALSE = ["0", "no", "false"]
_TRUE = ["1", "yes", "true"]


class Application(internal_control.Application):
    """
    Application class that can be used with `clingo.clingo_main` to solve CSP
    problems.
    """

    def __init__(self):
        self.program_name = "eclingo"
        self.version = __version__
        self.config = AppConfig()

    def _parse_int(self, config, attr, min_value=None, max_value=None):
        """
        Parse integer and store result in `config.attr`.

        Here `attr` has to be the name of an attribute. Optionally, a minimum
        and maximum value can be given for the integer.
        """

        def parse(value):
            num = int(value)
            if min_value is not None and num < min_value:
                return False
            if max_value is not None and num > max_value:
                return False
            setattr(config, attr, num)
            return True

        return parse

    def _parse_string(self, config, attr):
        def parse(value):
            setattr(config, attr, value)
            return True

        return parse

    def register_options(self, options) -> None:
        """
        Register eclingo related options.
        """
        group = "Eclingo Options"

        # Copy-Pasted Example
        # Commented out as parse_int was left out too.
        options.add(
            group,
            "eclingo-verbose@2",
            "Set verbosity level of eclingo to <n>",
            self._parse_int(self.config, "eclingo_verbose"),
            argument="<n>",
        )

        group = "App Options"
        options.add(
            group,
            "output-file",
            "Write output to <file>",
            self._parse_string(self.config, "outputfile"),
            argument="<file>",
        )

        # TESTING Help level with @2
        # options.add(group, "example, @2", "TEST")

        # Option 2, Add just a flag -> If flag passed, sets to true and reification is enabled,
        # then needs to be sent as input for solver.
        # options.add_flag(
        #     group=group,
        #     option="ereification",
        #     description="Reification TESTING",
        #     target=Flag(True),
        # )

    def _read(self, path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as file_:
            return file_.read()

    def main(self, control: InternalStateControl, files: Sequence[str]) -> None:
        """
        Entry point of the application registering the propagator and
        implementing the standard ground and solve functionality.
        """
        if not files:
            files = ["-"]

        eclingo_control = Control(control, self.config)

        for path in files:
            eclingo_control.add_program(self._read(path))

        eclingo_control.ground()
        eclingo_control.preprocess()
        eclingo_control.prepare_solver()

        sys.stdout.write("Solving...\n")
        wv_number = 1
        for world_view in eclingo_control.solve():
            sys.stdout.write("World view: %d\n" % wv_number)
            sys.stdout.write(str(world_view))
            sys.stdout.write("\n")
            wv_number += 1
        if wv_number > 1:
            sys.stdout.write("SATISFIABLE\n")
        else:
            sys.stdout.write("UNSATISFIABLE\n")


def main():
    sys.argv.append("--outf=3")
    application = Application()
    result = internal_control.clingo_main(application, sys.argv[1:])
    return int(result)
