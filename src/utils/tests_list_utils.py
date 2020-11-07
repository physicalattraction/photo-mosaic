import random
from unittest import TestCase

from utils.list_utils import permutation_multiple_lists


class UtilsTestCase(TestCase):
    def test_that_permutation_multiple_lists_works(self):
        a = [1, 3, 5]
        b = ['A', 'C', 'E']
        c = [10, 30, 50]
        random.seed(1)
        output = permutation_multiple_lists(a, b, c)
        expected_output = [(1, 'A', 10), (5, 'E', 50), (3, 'C', 30)]
        self.assertListEqual(expected_output, output)
