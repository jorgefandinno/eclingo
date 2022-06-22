import eclingo.internal_states.internal_control as internal_control

from eclingo.util.logger import silent_logger
from . import helper



class ClingoTestHelper(helper.TestHelper):

    def setUp(self):
        super().setUp()
        self.clingo_control = internal_control.InternalStateControl(logger=silent_logger)
        self.program_added = False

    def add_program(self, program):
        self.clingo_control.add_program(program)
        self.program_added = True

    def assert_equal_clingo_ground_program(self, program, expected):
        if not self.program_added:
            self.add_program(program)
        self.clingo_control.ground([("base", [])])
        result = self.clingo_control.ground_program
        self._print(result)
        self.assertEqual(str(result), str(expected))


