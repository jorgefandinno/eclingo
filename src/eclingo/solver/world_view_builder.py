from typing import Sequence

from clingo import Function, Symbol
from clingo.ast import Sign

import eclingo.internal_states.internal_control as internal_control
from eclingo.literals import Literal
from eclingo.solver.candidate import Candidate

from .candidate import Candidate
from .world_view import EpistemicLiteral, WorldView


class WorldWiewBuilderReification:
    def __init__(self):
        pass
    
    def __call__(self, candidate: Candidate):
        return self.world_view_from_candidate(candidate)

    def generate_k_symbol(self, epistemic_literal):
        ep_args = epistemic_literal.arguments[0]
        epistemic_name = ep_args.name  # not1, not2 or u

        # if symbol is of the form &k{not L} with L an explicit literal
        if epistemic_name == "not1":
            return None
        # if symbol is of the form &k{not not L} with L an explicit literal
        elif epistemic_name == "not2":
            literal_symbol = ep_args.arguments[0].arguments[0]
            sign = Sign.DoubleNegation
        # if symbol is of the form &k{L} with L an explicit literal
        else:
            literal_symbol = ep_args.arguments[0]  # literal symbol is L
            sign = Sign.NoSign

        # Check for explicit negation
        is_explicit = literal_symbol.positive

        # Check for arguments of literal
        arguments: Sequence[Symbol] = []
        if literal_symbol.arguments:
            for args in literal_symbol.arguments:
                arguments.append(args)

        # print("The args: ", literal_symbol.arguments[0])

        new_symbol = Function(literal_symbol.name, arguments, is_explicit)
        literal = Literal(new_symbol, sign)

        return EpistemicLiteral(literal, Sign.NoSign)

    def generate_m_symbol(self, epistemic_literal):
        ep_args = epistemic_literal.arguments[0]
        epistemic_name = ep_args.name  # not1, not2 or u

        # if symbol is of the form &k{not L} with L an explicit literal
        if epistemic_name == "not1":
            literal_symbol = ep_args.arguments[0].arguments[0]
            sign = Sign.NoSign
        # if symbol is of the form &k{not not L} with L an explicit literal
        else:
            return None
        # Check for explicit negation
        is_explicit = literal_symbol.positive

        arguments: Sequence[Symbol] = []
        if literal_symbol.arguments:
            for args in literal_symbol.arguments:
                arguments.append(args)

        new_symbol = Function(literal_symbol.name, arguments, is_explicit)
        literal = Literal(new_symbol, sign)

        return EpistemicLiteral(literal, Sign.NoSign, True)

    def world_view_from_candidate(self, candidate: Candidate):
        epistemic_literals = []
        k_symbols = []
        print(self.show_statements)

        for epistemic_literal in candidate.pos:
            print("\n The epistemic literal POS: ", epistemic_literal)
            show_literal = self.generate_k_symbol(epistemic_literal)
            if show_literal is not None:
                epistemic_literals.append(show_literal)
                k_symbols.append(show_literal.objective_literal)

        for epistemic_literal in candidate.neg:
            print("\n The epistemic literal NEG: ", epistemic_literal)
            show_literal = self.generate_m_symbol(epistemic_literal)

            if (
                show_literal is not None
                and show_literal.objective_literal not in k_symbols
            ):
                epistemic_literals.append(show_literal)

        return WorldView(epistemic_literals)


class WorldWiewBuilderReificationWithShow(WorldWiewBuilderReification):
    def __init__(self, reified_program):
        print("WORLD_VIEW_BUILDER")
        self.control = internal_control.InternalStateControl(["0"], message_limit=0)
        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "auto,3"
        self.reified_program = reified_program
        self.show_statements = []
        
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
                    
                                hold(L) :- k(A), output(k(A), B), literal_tuple(B, L).
                                :- hold(L) , not k(A), output(k(A), B), literal_tuple(B, L).
                                """

        self.control.add("base", [], self.reified_program)
        self.control.add("base", [], program_meta_encoding)
        self.control.ground([("base", [])])
        
        super().__init__()
        
        
    def world_view_from_candidate(self, candidate: Candidate):
        candidate_pos = []
        candidate_neg = []
        candidate_assumptions = []
        cand_show = []
        print("Receiving Tested Candidate: ", candidate)

        for literal in candidate[0]:
            assumption = (literal, True)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_pos.append(literal)
            cand_show.append(literal)

        for literal in candidate[1]:
            assumption = (literal, False)
            candidate_assumptions.append(assumption)
            literal = literal.arguments[0]
            candidate_neg.append(literal)
            cand_show.append(literal)

        self.control.configuration.solve.models = 0
        self.control.configuration.solve.project = "no"

        new_candidate_pos = []
        new_candidate_neg = []

        with self.control.solve(
            yield_=True, assumptions=candidate_assumptions
        ) as handle:
            model = None
            for model in handle:
                pass
            
            assert model is not None
            
            print("generated model:", model)
            self.epistemic_show_statements(model, cand_show)
            new_candidate_pos, new_candidate_neg = self.show_candidates(
                model, candidate_neg, candidate_pos
            )
            if new_candidate_neg != candidate_neg or new_candidate_pos != candidate_pos:
                candidate_pos = new_candidate_pos
                candidate_neg = new_candidate_neg


        return super().world_view_from_candidate(
            Candidate(new_candidate_pos, new_candidate_neg)
        )

    # """
    #     Generates show_statement(X) to check for in Wview based on a Control.py variable
    # """
    def epistemic_show_statements(self, model, candidates_show):
        show_name: str = "show_statement"

        for atom in candidates_show:
            arguments: Sequence[Symbol] = []
            arguments.append(Function(atom.arguments[0].name, [], atom.arguments[0].positive))
            show_stm = Function(show_name, arguments, True)
            if model.contains(show_stm) and show_stm not in self.show_statements:
                self.show_statements.append(show_stm)
                print("The show statement: ", show_stm)

    """
        Creates new list of candidates based on show_statements.
        Update new candidates based on given show_statements.
    """

    def show_candidates(self, model, cand_neg, cand_pos):
        show_name: str = "show_statement"
        c_pos = []
        c_neg = []

        print("Received candidates: ", cand_pos, cand_neg)
        for atom in cand_pos:  # Create show_statement(X) for comparison
            arguments: Sequence[Symbol] = []
            arguments.append(
                Function(atom.arguments[0].name, [], atom.arguments[0].positive)
            )
            show_stm = Function(show_name, arguments, True)
            if model.contains(show_stm):
                k_atom = Function("k", [atom], atom.arguments[0].positive)
                c_pos.append(k_atom)
                print("The show statement POS: ", show_stm)

        for atom in cand_neg:  # Create show_statement(X) for comparison
            arguments: Sequence[Symbol] = []
            arguments.append(
                Function(atom.arguments[0].name, [], atom.arguments[0].positive)
            )
            show_stm = Function(show_name, arguments, True)
            if model.contains(show_stm):
                k_atom = Function("k", [atom], atom.arguments[0].positive)
                c_neg.append(k_atom)
                print("The show statement NEG: ", show_stm)

        print("\nThe returning candidates are: ", c_pos, c_neg)
        return c_pos, c_neg
