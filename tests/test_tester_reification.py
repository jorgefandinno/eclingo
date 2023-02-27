import unittest

import clingo
from clingox.program import Program, ProgramObserver, Remapping

import eclingo.internal_states.internal_control as internal_control
from eclingo.solver.tester import CandidateTester


class TesterCase(unittest.TestCase):
    def assertEqualPrograms(self, expected_program, program):
        expected_program = [f"{s.strip()}." for s in program.split(".") if s]
        expected_program.sort()
        program = [s.strip() for s in str(program).split("\n")]
        program.sort()
        return self.assertListEqual(expected_program, program)



    def assertReification(self, program):
        program = [
            function_transformer.rule_to_symbolic_term_adapter(stm)
            for stm in program
        ]
        
        program = program_pr(program, expected)
        
        ctl_a = Control()
        
        temp = []
        ctl_a.register_observer(Reifier(temp.append))
    
        ctl_a.add('base', [], program)
        ctl_a.ground([('base', [])])
        
        temp = [str(e) for e in temp]
        
    def assertInitControl(self, program):
        control_gen = internal_control.InternalStateControl()
        program1 = Program()
        control_gen.register_observer(ProgramObserver(program1))
        control_gen.add("base", [], program)
        control_gen.ground([("base", [])])
        self.assertEqualPrograms(program, str(program1))
        control_test = internal_control.InternalStateControl(["0"], message_limit=0)
        program2 = Program()
        control_test.register_observer(ProgramObserver(program2))
        CandidateTester._init_control_test(control_test, control_gen)
        self.assertEqualPrograms(program, str(program2))

    def test_init_control(self):
        self.assertInitControl("{u_a}.")
        self.assertInitControl("u_b :- k_a. {k_a}. {u_a}.")
        self.assertInitControl("u_a; u_b. u_c :- u_a. u_c :- u_b. u_d :- k_c. {k_c}.")
