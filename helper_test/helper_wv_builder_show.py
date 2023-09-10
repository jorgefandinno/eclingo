from pprint import pprint

from eclingo.solver.world_view_builder import WorldWiewBuilderReification
from helper_test.helper_eclingo import EclingoTestHelper


class WorldWiewBuilderWithShowTestHelper(EclingoTestHelper):
    def assert_equal_show_program(self, program, expected_show_program):
        self.eclingo_control = self._control_and_ground(program)
        wv_builder = WorldWiewBuilderReification(self.eclingo_control.control)
        ground_program = wv_builder.control.ground_program.pretty_str()
        if self.printing:
            print("\n--- program ---")
            pprint(ground_program)
        ground_program = sorted(
            map(str, list(filter(lambda x: x != "", ground_program.split("\n"))))
        )
        self.assert_equal_ordered(ground_program, expected_show_program)
