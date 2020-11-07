import random
from typing import List, Tuple


def permutation_multiple_lists(*args: List) -> List[Tuple]:
    """
    Return a list of tuples, where each element of the list contains
    an element from each input list with the same, randomized, index.

    Doctest

    >>> random.seed(1)
    >>> permutation_multiple_lists([1, 2, 3], ['a', 'b', 'c'], [10, 20, 30])
    [(1, 'a', 10), (3, 'c', 30), (2, 'b', 20)]
    """

    zipped = list(zip(*args))
    permutation = random.sample(zipped, len(zipped))
    return list(permutation)
