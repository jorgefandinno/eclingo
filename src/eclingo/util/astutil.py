"""
Tools to work with ASTs.
"""
# pylint: disable=no-member

from copy import copy
from itertools import chain, product

import clingo # type: ignore
from clingo import ast as _ast
# pylint: disable=invalid-name

class Visitor(object):
    """
    Visit `clingo.ast.AST` objects by visiting all child nodes.

    Implement `visit_<type>` where `<type>` is the type of the nodes to be
    visited.
    """
    def visit_children(self, x, *args, **kwargs):
        """
        Visit all child nodes of the current node.
        """
        for key in x.child_keys:
            self.visit(getattr(x, key), *args, **kwargs)

    def visit_list(self, x, *args, **kwargs):
        """
        Visit a list of AST nodes.
        """
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_tuple(self, x, *args, **kwargs):
        """
        Visit a list of AST nodes.
        """
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_none(self, *args, **kwargs):
        """
        Visit none.

        This, is to handle optional arguments that do not have a visit method.
        """

    def visit(self, x, *args, **kwargs):
        """
        Default visit method to dispatch calls to child nodes.
        """
        if isinstance(x, _ast.AST):
            attr = "visit_" + str(x.type)
            if hasattr(self, attr):
                return getattr(self, attr)(x, *args, **kwargs)
            return self.visit_children(x, *args, **kwargs)
        if isinstance(x, list):
            return self.visit_list(x, *args, **kwargs)
        if isinstance(x, tuple):
            return self.visit_tuple(x, *args, **kwargs)
        if x is None:
            return self.visit_none(x, *args, **kwargs)
        raise TypeError("unexpected type: {}".format(x))


class Transformer(Visitor):
    """
    Transforms `clingo._ast.AST` objects by visiting all child nodes.

    Implement `visit_<type>` where `<type>` is the type of the nodes to be
    visited.
    """

    def visit_children(self, x, *args, **kwargs):
        """
        Visit all child nodes of the current node.
        """
        copied = False
        for key in x.child_keys:
            y = getattr(x, key)
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                if not copied:
                    copied = True
                    x = copy(x)
                setattr(x, key, z)
        return x

    def _seq(self, i, z, x, args, kwargs):
        for y in x[:i]:
            yield y
        yield z
        for y in x[i+1:]:
            yield self.visit(y, *args, **kwargs)

    def visit_list(self, x, *args, **kwargs):
        """
        Visit a list of AST nodes.
        """
        for i, y in enumerate(x):
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                return list(self._seq(i, z, x, args, kwargs))
        return x

    def visit_tuple(self, x, *args, **kwargs):
        """
        Visit a tuple of AST nodes.
        """
        for i, y in enumerate(x):
            z = self.visit(y, *args, **kwargs)
            if y is not z:
                return tuple(self._seq(i, z, x, args, kwargs))
        return x


class ASTInspector(object):
    """
    Visit `clingo.clingo._ast.AST` objects by visiting all child nodes.

    Implement `visit_<type>` where `<type>` is the type of the nodes to be
    visited.
    """
    def __init__(self):
        self.level = 0
        self.string = ""

    def _sign_repr(self, sign):
        if sign == _ast.Sign.NoSign:
            return "_ast.Sign.NoSign"
        elif sign == _ast.Sign.Negation:
            return "_ast.Sign.Negation"
        else: # sign == _ast.Sign.DoubleNegation:
            return "_ast.Sign.DoubleNegation"

    def visit_children(self, x, *args, **kwargs):
        """
        Visit all child nodes of the current node.
        """
        ident = 2*self.level*" "
        for key in x.keys():
            self.string += ident + key + " = "
            if key == "sign":
                self.string += self._sign_repr(getattr(x, key))
            if key in x.child_keys:
                self.visit(getattr(x, key), *args, **kwargs)
            else:
                self.string += repr(getattr(x, key))
            self.string += "\n"

    def visit_list(self, x, *args, **kwargs):
        """
        Visit a list of AST nodes.
        """
        ident = 2*self.level*" "
        if len(x) == 0:
            self.string += "[]"
        else:
            self.string += "[\n"
            for y in x:
                self.visit(y, *args, **kwargs)
            self.string += ident + "]\n"

    def visit_tuple(self, x, *args, **kwargs):
        """
        Visit a list of AST nodes.
        """
        for y in x:
            self.visit(y, *args, **kwargs)

    def visit_none(self, *args, **kwargs):
        """
        Visit none.

        This, is to handle optional arguments that do not have a visit method.
        """

    def visit(self, x, *args, **kwargs):
        """
        Default visit method to dispatch calls to child nodes.
        """
        if isinstance(x, _ast.AST):
            self.string += str(x.type) + "(    # " + str(x) + "\n"
            self.level += 1
            self.visit_children(x, *args, **kwargs)
            self.level -= 1
            ident = 2*self.level*" "
            self.string += ident + ")"
            return
        if isinstance(x, list):
            return self.visit_list(x, *args, **kwargs)
        if isinstance(x, tuple):
            return self.visit_tuple(x, *args, **kwargs)
        if x is None:
            return self.visit_none(x, *args, **kwargs)
        self.string += str(x)
        return

def ast_repr(stm):
    t = ASTInspector()
    t.visit(stm)
    return t.string
