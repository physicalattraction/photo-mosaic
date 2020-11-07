import os.path

_image_extensions = {'.bmp', '.gif', '.jpeg', '.jpg', '.png'}


def is_image(filename: str) -> bool:
    """
    Return whether the filename is an image or not

    >>> is_image('photo.jpg')
    True
    >>> is_image('photo.txt')
    False

    :param filename: The filename to test
    :return: True if the filename is an image, False otherwise
    """

    _, ext = os.path.splitext(filename)
    return ext.lower() in _image_extensions
