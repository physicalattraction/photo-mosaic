from unittest import TestCase

from utils.image_utils import is_image


class ImageUtilsTestCase(TestCase):
    def test_is_image_verifies_files_by_extension(self):
        self.assertTrue(is_image('photo.jpg'))
        self.assertTrue(is_image('photo.jpeg'))
        self.assertTrue(is_image('photo.bmp'))
        self.assertTrue(is_image('photo.gif'))
        self.assertTrue(is_image('photo.png'))

        self.assertTrue(is_image('photo.JPG'))
        self.assertTrue(is_image('./photo.jpg'))
        self.assertFalse(is_image('photo.txt'))
        self.assertFalse(is_image('photojpg'))
        self.assertFalse(is_image('photo.jpg.txt'))
