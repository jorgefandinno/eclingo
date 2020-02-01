from abc import ABC
import clingo


class Preprocessor(ABC):
    def __init__(self, candidates_gen, candidates_test):
        self._candidates_gen = candidates_gen
        self._candidates_test = candidates_test
        self.predicates = []
        self.show_signatures = set()

    def preprocess(self, program):
        clingo.parse_program(program, lambda ast: self._preprocess(ast))

    def _preprocess(self, ast):
        if ast.type == clingo.ast.ASTType.Rule:
            rule = self._preprocess_rule(ast)
            for control_object in [self._candidates_gen, self._candidates_test]:
                with control_object.builder() as builder:
                    builder.add(rule)
        elif ast.type == clingo.ast.ASTType.ShowSignature:
            self.show_signatures.add((ast.name, ast.arity, ast.positive))
        elif ast.type == clingo.ast.ASTType.Definition:
            for control_object in [self._candidates_gen, self._candidates_test]:
                with control_object.builder() as builder:
                    builder.add(ast)

    def _preprocess_rule(self, ast):
        preprocessed_body = []
        for body_literal in ast.body:
            if (body_literal.type == clingo.ast.ASTType.Literal) \
                    and (body_literal.atom.type == clingo.ast.ASTType.TheoryAtom):

                body_literal = self._get_preprocessed_literal(body_literal)
                preprocessed_body.append(body_literal)

                body_positive = []
                if 'not_' in body_literal.atom.term.name:
                    body_positive = self._get_body_positive(ast)
                self.predicates.append((body_literal, body_positive))

                preprocessed_body.extend(self._get_aux_body_literals(body_literal))
            else:
                preprocessed_body.append(body_literal)

        return clingo.ast.Rule(ast.location, ast.head, preprocessed_body)

    def _get_preprocessed_literal(self, literal):
        theory_term = literal.atom.elements[0].tuple[0]
        theory_element = theory_term.elements[0]
        aux_name = 'aux_'
        for operator in theory_element.operators:
            if operator == '~':
                aux_name += 'not_'
            elif operator == '-':
                aux_name += 'sn_'
        if theory_element.term.type == clingo.ast.ASTType.Symbol:
            symbol_name = theory_element.term.symbol.name
            symbol_arguments = theory_element.term.symbol.arguments
        elif theory_element.term.type == clingo.ast.ASTType.TheoryFunction:
            symbol_name = theory_element.term.name
            symbol_arguments = [symbol_argument.elements[0].term
                                for symbol_argument in theory_element.term.arguments]

        sign = self._get_literal_sign(literal)

        return clingo.ast.Literal(literal.location, sign,
                                  clingo.ast.SymbolicAtom(
                                      clingo.ast.Function(literal.location,
                                                          aux_name+symbol_name,
                                                          symbol_arguments, False)))

    def _get_literal_sign(self, literal):
        return clingo.ast.Sign.DoubleNegation \
            if (literal.sign == clingo.ast.Sign.NoSign) \
            else literal.sign

    def _get_body_positive(self, ast):
        body_positive = [literal for literal in ast.body
                         if (literal.atom.type != clingo.ast.ASTType.TheoryAtom)
                         and (literal.sign != clingo.ast.Sign.Negation)]
        return body_positive

    def _get_aux_body_literals(self, _body_literal):
        return []


class G91Preprocessor(Preprocessor):
    pass


class K14Preprocessor(Preprocessor):

    def _get_literal_sign(self, literal):
        return literal.sign

    def _get_aux_body_literals(self, body_literal):
        if ('not_' not in body_literal.atom.term.name) and \
            (body_literal.sign != clingo.ast.Sign.Negation):
            aux_body_literal_name = body_literal.atom.term.name.replace('aux_', '')
            if 'sn_' in body_literal.atom.term.name:
                aux_body_literal = clingo.ast.Literal(
                    body_literal.location, body_literal.sign,
                    clingo.ast.SymbolicAtom(
                        clingo.ast.UnaryOperation(
                            body_literal.location,
                            clingo.ast.UnaryOperator.Minus,
                            clingo.ast.Function(body_literal.location,
                                                aux_body_literal_name.replace('sn_', ''),
                                                body_literal.atom.term.arguments,
                                                False))))
            else:
                aux_body_literal = clingo.ast.Literal(
                    body_literal.location, body_literal.sign,
                    clingo.ast.SymbolicAtom(
                        clingo.ast.Function(body_literal.location,
                                            aux_body_literal_name,
                                            body_literal.atom.term.arguments,
                                            False)))
            return [aux_body_literal]
