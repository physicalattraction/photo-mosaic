import os.path


class Path:
    """
    Helper class to build paths within the project
    """

    src = os.path.dirname(__file__)
    root = os.path.dirname(src)
    photos = os.path.join(root, 'photos')
    testdata = os.path.join(root, 'testdata')

    @staticmethod
    def to_photo(name: str) -> str:
        """
        Return full path to the photo in directory testdata
        """

        base, ext = os.path.splitext(name)
        if not ext:
            name = f'{base}.jpg'
        return os.path.join(Path.testdata, name)

    @staticmethod
    def to_src_dir(name: str) -> str:
        """
        Return full path to the directory with photos to generate a mosaic from
        """

        return os.path.join(Path.photos, name)
