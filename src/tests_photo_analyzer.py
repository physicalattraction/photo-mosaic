import os.path
from unittest import TestCase

from photo import Photo
from photo_analyzer import PhotoAnalyzer
from utils import Path


class PhotoAnalyzerTestCase(TestCase):
    def test_that_photos_are_properly_initialized(self):
        cats = os.path.join(Path.testdata, 'cats')
        analyzer = PhotoAnalyzer(src_dir=cats)
        photos = analyzer.photos
        self.assertListEqual(list(photos.keys()), [f'cat00{index}.jpg' for index in (1, 2, 3, 4, 5)])
        self.assertTrue(all(isinstance(value, Photo) for value in photos.values()))
