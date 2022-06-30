import unittest

from eclingo.util.astutil import ast_repr as _ast_repr

class TestHelper(unittest.TestCase):

    def setUp(self):
        self.printing = False
        self.printing_ast_repr = False

    def assert_equal_ordered(self, obj1, obj2):
        obj1 = sorted(obj1)
        obj2 = sorted(obj2)
        self.assertEqual(obj1, obj2)