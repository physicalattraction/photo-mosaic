import os.path
import random
from typing import List, Tuple


def permutation_multiple_lists(*args: List) -> List[Tuple]:
    """
    Return a list of tuples, where each element of the list contains an element from
    each input list with the same, randomized, index.
    """

    zipped = list(zip(*args))
    permutation = random.sample(zipped, len(zipped))
    return list(permutation)


class Path:
    """
    Helper class to build paths within the project
    """

    src = os.path.dirname(__file__)
    root = os.path.dirname(src)
    photos = os.path.join(root, 'photos')
    raw = os.path.join(root, 'raw')
    testdata = os.path.join(root, 'testdata')

    @staticmethod
    def to_photo(name: str) -> str:
        """
        Return full path to the photo in directory photos

        :param name: Filename of the photo. Extension is optional, default=.jpg
        """

        base, ext = os.path.splitext(name)
        if not ext:
            name = f'{base}.jpg'
        return os.path.join(Path.photos, name)

    @staticmethod
    def to_testphoto(name: str) -> str:
        """
        Return full path to the photo in directory testdata

        :param name: Filename of the testphoto. Extension is optional, default=.jpg
        """

        base, ext = os.path.splitext(name)
        if not ext:
            name = f'{base}.jpg'
        return os.path.join(Path.testdata, name)

    @staticmethod
    def to_src_photos_dir(name: str) -> str:
        """
        Return full path to the directory with photos to generate a mosaic from

        :param name: Directory name within the photos directory
        """

        return os.path.join(Path.photos, name)

    @staticmethod
    def to_raw_photos_dir(name: str) -> str:
        """
        Return full path to the directory with photos to collect

        :param name: Directory name within the raw directory
        """

        return os.path.join(Path.raw, name)
