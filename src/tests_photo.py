from unittest import TestCase
from unittest.mock import patch

from PIL import Image

from photo import Photo
from utils.path import Path


class PhotoTestCase(TestCase):
    @property
    def equal_rgb_image(self) -> Photo:
        photo = Photo.new(size=(120, 40), mode='RGB')
        red_box = Image.new(size=(40, 40), color=(255, 0, 0), mode='RGB')
        green_box = Image.new(size=(40, 40), color=(0, 255, 0), mode='RGB')
        blue_box = Image.new(size=(40, 40), color=(0, 0, 255), mode='RGB')
        photo.paste(red_box, (0, 0))
        photo.paste(green_box, (40, 0))
        photo.paste(blue_box, (80, 0))
        return photo

    def test_that_uniform_image_returns_that_color(self):
        for color in [(0, 0, 0), (255, 255, 255), (255, 0, 0)]:
            photo = Photo.new(size=(100, 50), color=color, mode='RGB')
            self.assertTupleEqual(color, photo.avg_color)

    def test_that_equal_rgb_image_returns_dark_grey(self):
        photo = self.equal_rgb_image
        expected_avg_color = (85, 85, 85)
        self.assertTupleEqual(expected_avg_color, photo.avg_color)

    def test_that_real_photo_returns_correct_color(self):
        photo = Photo.open(Path.to_testphoto('wolf_low_res'))
        expected_avg_color = (127, 111, 102)
        self.assertTupleEqual(expected_avg_color, photo.avg_color)

    def test_that_avg_color_is_cached(self):
        photo = self.equal_rgb_image
        avg_color = photo.avg_color
        self.assertIsNotNone(photo._avg_color)
        self.assertTupleEqual(avg_color, photo._avg_color)
        with patch.object(Photo, '_determine_avg_color') as mock:
            _ = photo.avg_color
            mock.assert_not_called()

    def test_that_two_photos_are_not_equal_if_not_equal_in_size(self):
        photo_1 = Photo.new(size=(10, 10), color=(0, 0, 0), mode='RGB')
        photo_2 = Photo.new(size=(10, 10), color=(0, 0, 0), mode='RGB')
        self.assertEqual(photo_1, photo_2)
        photo_3 = Photo(photo_1.resize((5, 5)))
        self.assertNotEqual(photo_3, photo_2)

    def test_that_two_photos_are_not_equal_if_one_pixel_different(self):
        photo_1 = Photo.new(size=(10, 10), color=(0, 0, 0), mode='RGB')
        photo_2 = Photo.new(size=(10, 10), color=(0, 0, 0), mode='RGB')
        self.assertEqual(photo_1, photo_2)
        photo_2.img.putpixel((5, 5), (1, 0, 0))
        self.assertNotEqual(photo_1, photo_2)

    def test_representation_of_photo(self):
        photo = self.equal_rgb_image
        self.assertEqual('<Photo mode=RGB size=120x40>', repr(photo))
