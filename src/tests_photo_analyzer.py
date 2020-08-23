import os.path
from unittest import TestCase

from photo import Photo
from photo_analyzer import PhotoAnalyzer
from utils import Path


class PhotoAnalyzerTestCase(TestCase):
    def test_that_photos_are_properly_initialized(self):
        cats = os.path.join(Path.testdata, 'cats')
        analyzer = PhotoAnalyzer(src_dir=cats, nr_photo_pixels=10)
        photos = analyzer.photos
        self.assertListEqual(list(photos.keys()), [f'cat00{index}.jpg' for index in (1, 2, 3, 4, 5)])
        self.assertTrue(all(isinstance(value, Photo) for value in photos.values()))

    def test_that_photos_to_choose_from_are_properly_initialized(self):
        cats = os.path.join(Path.testdata, 'cats')
        analyzer = PhotoAnalyzer(src_dir=cats, nr_photo_pixels=9)
        photos = analyzer.photos_to_choose_from
        self.assertListEqual(photos, [f'cat00{index}.jpg' for index in (1, 2, 3, 4, 5, 1, 2, 3, 4, 5)])

    def test_that_distance_is_calculated_properly(self):
        color_1 = (127, 127, 127)
        color_2 = (130, 127, 127)
        color_3 = (128, 128, 128)

        self.assertAlmostEqual(0, PhotoAnalyzer._distance(color_1, color_1))
        self.assertAlmostEqual(3, PhotoAnalyzer._distance(color_1, color_2))
        self.assertAlmostEqual(1.7320508075688772, PhotoAnalyzer._distance(color_1, color_3))
        self.assertAlmostEqual(2.449489742783178, PhotoAnalyzer._distance(color_2, color_3))
