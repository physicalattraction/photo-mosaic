import os.path


class Path:
    """
    Helper class to build paths within the project
    """

    utils = os.path.dirname(__file__)
    src = os.path.dirname(utils)
    root = os.path.dirname(src)
    photos = os.path.join(root, 'photos')
    raw = os.path.join(root, 'raw')
    testdata = os.path.join(root, 'testdata')

    assert os.path.exists(utils)
    assert os.path.exists(src)
    assert os.path.exists(root)
    assert os.path.exists(photos)
    assert os.path.exists(raw)
    assert os.path.exists(testdata)

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

        # TODO: Replace with mocking to_photo()

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
