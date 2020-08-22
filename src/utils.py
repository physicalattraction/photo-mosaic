import os.path
from unittest import TestCase

from PIL import Image


class Dir:
    src = os.path.dirname(__file__)
    root = os.path.dirname(src)
    photos = os.path.join(root, 'photos')
    testdata = os.path.join(root, 'testdata')


def get_photo(name: str) -> Image.Image:
    base, ext = os.path.splitext(name)
    if not ext:
        name = f'{base}.jpg'
    return Image.open(os.path.join(Dir.testdata, name))


class ImageComparingMixin(TestCase):
    """
    Behavior to assert that two Pillow Images are equal
    """

    def assertImageEqual(self, img_1: Image.Image, img_2: Image.Image):
        self.assertIsInstance(img_1, Image.Image, f'img_1 is not an Image: {type(img_1)}')
        self.assertIsInstance(img_2, Image.Image, f'img_2 is not an Image: {type(img_2)}')
        self.assertEqual(img_1.size, img_2.size, f'Size of img_1 {img_1.size} != size of img_2 {img_2.size}')
        for pixel_1, pixel_2 in zip(img_1.getdata(), img_2.getdata()):
            self.assertEqual(pixel_1, pixel_2)
