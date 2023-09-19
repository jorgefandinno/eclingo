from unittest import TestCase

from eclingo import util


class TestPartition(TestCase):
    def test_size_1(self):
        self.assertEqual(
            util.partition(list(x for x in range(1, 10)), lambda x: x % 2 == 0),
            ([2, 4, 6, 8], [1, 3, 5, 7, 9]),
        )

    def test_size_2(self):
        self.assertEqual(
            util.partition(
                list(x for x in range(1, 10)),
                lambda x: x % 2 == 0,
                lambda x: x % 5 == 0,
            ),
            ([2, 4, 6, 8], [5], [1, 3, 7, 9]),
        )

    def test_size_3(self):
        self.assertEqual(
            util.partition(
                list(x for x in range(1, 10)),
                lambda x: x % 2 == 0,
                lambda x: x % 5 == 0,
                lambda x: x % 7 == 0,
            ),
            ([2, 4, 6, 8], [5], [7], [1, 3, 9]),
        )

    def test_size_4(self):
        self.assertEqual(
            util.partition(
                list(x for x in range(1, 10)),
                lambda x: x % 2 == 0,
                lambda x: x % 5 == 0,
                lambda x: x % 7 == 0,
                lambda x: x % 9 == 0,
            ),
            ([2, 4, 6, 8], [5], [7], [9], [1, 3]),
        )

    def test_size_more(self):
        self.assertEqual(
            util.partition(
                list(x for x in range(1, 14)),
                lambda x: x % 2 == 0,
                lambda x: x % 7 == 0,
                lambda x: x % 9 == 0,
                lambda x: x % 11 == 0,
                lambda x: x % 13 == 0,
            ),
            ([2, 4, 6, 8, 10, 12], [7], [9], [11], [13], [1, 3, 5]),
        )
