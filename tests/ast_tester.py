from typing import MutableSequence
from unittest import TestCase
from pprint import pformat

from clingo.ast import AST
from clingox.ast import ast_to_dict

def remove_location_from_dict(d: dict) -> None:
    if 'location' in d:
        del d['location']
    for key, value in d.items():
        if isinstance(value, MutableSequence):
            for element in value:
                if isinstance(element, dict):
                    remove_location_from_dict(element)


class ASTTestCase(TestCase):

    def assertASTEqual(self, first, second, msg=None):
        first_dict = ast_to_dict(first)
        second_dict = ast_to_dict(second)
        remove_location_from_dict(first_dict)
        remove_location_from_dict(second_dict)
        ast_msg = f"""\n
{str(first)} != {str(second)}

{str(pformat(first_dict, sort_dicts=True,))}
{str(pformat(second_dict, sort_dicts=True,))}
        """
        super().assertEqual(first_dict, second_dict, ast_msg)
        super().assertEqual(first, second, ast_msg)

    def assertEqual(self, first, second, msg=None):
        if isinstance(first, AST) and isinstance(second, AST):
            return self.assertASTEqual(first, second, msg)
        return super().assertEqual(first, second, msg)
