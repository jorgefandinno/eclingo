from dataclasses import dataclass
from typing import Union
from clingo import Symbol
from clingo.ast import Sign # pylint: disable=import-error

@dataclass(eq=True, unsafe_hash=True, order=True)
class Literal:
    atom: Symbol
    sign: Sign

    def __init__(self, atom: Symbol, sign: Union[Sign, bool]):
        self.atom = atom
        print("atom in literal: ", self.atom)
        print("sign in literal: ", sign)
        if isinstance(sign, bool):
            if sign:
                sign = Sign.NoSign
            else:
                sign = Sign.Negation

        self.sign = sign

    def __repr__(self):
        return repr(self.sign) + repr(self.atom)
    
    def __str__(self):

        if(self.sign==Sign.NoSign):
            return str(self.atom)
        
        elif(self.sign==Sign.DoubleNegation):
            return 'not not ' + str(self.atom)

        else:
            return 'not ' + str(self.atom)


@dataclass(eq=True, unsafe_hash=True, order=True)
class EpistemicLiteral:
    objective_literal: Literal
    sign: Sign = Sign.NoSign
    is_m: bool = False

    def __init__(self, objective_literal: Union[Literal, Symbol], sign: Sign = Sign.NoSign, is_m: bool = False):
        if isinstance(objective_literal, Symbol):
            objective_literal = Literal(objective_literal, Sign.NoSign)
        self.objective_literal = objective_literal
        self.sign = sign
        self.is_m = is_m

    def __str__(self):

        # if not self.is_m:
        #     return f'{self.sign}&k{{{self.objective_literal}}}'
        # else:
        #     return f'{self.sign}&m{{{self.objective_literal}}}'

        literal_sign = ''
        if (self.sign == Sign.Negation):
            literal_sign = 'not'
        elif (self.sign == Sign.DoubleNegation):
            literal_sign = 'not not '


        if not self.is_m:
            return f'{literal_sign}&k{{{self.objective_literal}}}'
        else:
            return f'{literal_sign}&m{{{self.objective_literal}}}'


