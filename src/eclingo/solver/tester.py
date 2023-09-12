import eclingo.internal_states.internal_control as internal_control
from eclingo.config import AppConfig
from clingo.symbol import Symbol, Function
from typing import Sequence
from clingox.program import Fact

from .candidate import Candidate

# echo "a. b :- &k{a}. #show b/0. #show a/0." | eclingo
# echo "a. #show a/0." | eclingo

#TODO: Fix for literal_tuple(L) where L is only argument
# Then, for model if contains show_statement -> Create world_builder of only that one atom.
# Create copy of tester that calculates that for shows.

# TODO:
# Init create facts. Then check if there are show_statement, if there are call super.tester with new candidates
# Create those as assumptions
class CandidateTesterReification:
    def __init__(self, config: AppConfig, reified_program: str):
        self._config = config
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)
        self.reified_program = reified_program
        # self.show_statements: Sequence[Symbol] = []
        self.control.control.configuration.solve.enum_mode = "cautious"  # type: ignore

        program_meta_encoding = """conjunction(B) :- literal_tuple(B),
                                                        hold(L) : literal_tuple(B,  L), L > 0;
                                                    not hold(L) : literal_tuple(B, -L), L > 0.

                                body(normal(B)) :- rule(_, normal(B)), conjunction (B).

                                body(sum(B, G)) :- rule (_sum(B,G)),
                                #sum {
                                    W,L : hold(L), weighted_literal_tuple(B, L,W), L>0;
                                    W,L : not hold(L), weighted_literal_tuple(B, -L,W), L>0} >= G.

                                hold(A) : atom_tuple(H,A) :- rule(disjunction(H), B), body(B).

                                {hold(A) : atom_tuple(H,A)} :- rule(choice(H), B), body(B).

                                u(A)    :- output(u(A), B), conjunction(B).
                                not1(A) :- output(not1(A), B), conjunction(B).
                                not2(A) :- output(not2(A), B), conjunction(B).
                                
                                
                                symbolic_atom(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
                                epistemic_atom_info(SKA, KA, SA, A) :- symbolic_atom(SA, A), SKA=k(SA), symbolic_atom(SKA, KA).
                                show_statement(SA) :- symbolic_atom(show_statement(SA), _).
                                
                                {k(A)} :- output(k(A), _).
                    
                                hold(L) :- k(A), output(k(A), B), show_statement(SA), literal_tuple(B, L).
                                :- hold(L) , not k(A), output(k(A), B), literal_tuple(B, L).
                            
                                %%symbolic_atom(SA, A) :- output(SA,LT), #count{LL : literal_tuple(LT, LL)} = 1, literal_tuple(LT, A).
                                %%epistemic_atom_info(SKA, KA, SA, A) :- symbolic_atom(SA, A), SKA=k(SA), symbolic_atom(SKA, KA).
                                %%show_statement(SA) :- symbolic_atom(show_statement(SA), _).
                                %%hold(L) :  show_statment(SA), output(k(A), B), literal_tuple(B, L).
                                %% #project hold(L) :  output(k(A), B), literal_tuple(B, L).
                                %% #project hold(L) :  show_statment(SA), output(k(A), B), literal_tuple(B, L).
                                """

        self.control.add("base", [], self.reified_program)
        self.control.add("base", [], program_meta_encoding)
        self.control.ground([("base", [])])
             
    def __call__(self, candidate: Candidate) -> bool:
        return self.candidate_tester(candidate)
    
    def candidate_tester(self, candidate: Candidate) -> bool:
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        for literal in candidate[0]:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_pos.append(literal)

        for literal in candidate[1]:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_neg.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        print("\nTESTER")
        print("Candidate assumptions:\n", candidate_assumptions)
        print(
            "Candidate assumptions:\n",
            "\n".join(str((str(a), v)) for a, v in candidate_assumptions),
        )
        
        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                for atom in candidate_pos:
                    if not model.contains(atom):
                        return False

            assert model is not None

            for atom in candidate_neg:
                if model.contains(atom):
                    return False
        return True
       
class CandidateTesterReificationWithShow(CandidateTesterReification):
    
    def __init__(self, config: AppConfig, reified_program: str):
        super().__init__(config, reified_program)
        
    def __call__(self, candidate: Candidate) -> bool:
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []

        for literal in candidate[0]:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_pos.append(literal)

        for literal in candidate[1]:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_neg.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"
          
        with self.control.solve(yield_=True) as handle:
            for model in handle:
                #print("Generated Model: ", model)
                # self.epistemic_show_statements(model, candidates_show)
                new_candidate_pos, new_candidate_neg = self.show_candidates(model, candidate_neg, candidate_pos)
                if new_candidate_neg != candidate_neg or new_candidate_pos != candidate_pos:
                    candidate_pos = new_candidate_pos
                    candidate_neg = new_candidate_neg
                
        return super().candidate_tester(Candidate(candidate_pos, candidate_neg))
       
    # """
    #     Generates show_statement(X) to check for in Wview
    # """
    # def epistemic_show_statements(self, model, candidates_show):
    #     show_name: str = "show_statement"
        
    #     for atom in candidates_show:
    #         arguments: Sequence[Symbol] = []
    #         arguments.append(Function(atom.arguments[0].name, [], atom.arguments[0].positive))
    #         show_stm = Function(show_name, arguments, True)
    #         if model.contains(show_stm) and show_stm not in self.control.show_statements:
    #             self.control.show_statements.append(show_stm)
    #             print("The show statement: ", show_stm)
                
    #     # for atom in candidates_show:
    #     #     arguments: Sequence[Symbol] = []
    #     #     arguments.append(Function(atom.arguments[0].name, [], atom.arguments[0].positive))
    #     #     show_stm = Function(show_name, arguments, True)
    #     #     show_fact = Fact(show_stm)
    #     #     if show_fact in self.control.ground_program.facts:
    #     #         print("Premio")
    #     #     # for i in range(len(self.control.ground_program.facts)):
    #     #     #     print(self.control.ground_program.facts[i])
                
    """
        Creates new list of candidates based on show_statements
    """
    def show_candidates(self, model, cand_neg, cand_pos):
        show_name: str = "show_statement"
        c_pos = []
        c_neg = []
        
        for atom in cand_pos:
            arguments: Sequence[Symbol] = []
            arguments.append(Function(atom.arguments[0].name, [], atom.arguments[0].positive))
            show_stm = Function(show_name, arguments, True)
            if model.contains(show_stm) and show_stm not in c_pos:
                c_pos.append(atom)
                print("The show statement POS: ", show_stm)
                
        for atom in cand_neg:
            arguments: Sequence[Symbol] = []
            arguments.append(Function(atom.arguments[0].name, [], atom.arguments[0].positive))
            show_stm = Function(show_name, arguments, True)
            if model.contains(show_stm) and show_stm not in c_neg:
                c_neg.append(atom)
                print("The show statement NEG: ", show_stm)
                
        return c_pos, c_neg
        
        
