from typing import Tuple

Color = Tuple[int, int, int]  # Three-tuple: RGB
Size = Tuple[int, int]  # Two-tuple: width, height
Box = Tuple[int, int, int, int]  # Four-tuple: left, upper, right, lower


def size_as_string(size: Size) -> str:
    """
    >>> size_as_string((25, 40))
    '25x40'
    """

    return f'{size[0]}x{size[1]}'
