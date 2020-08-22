import os.path
from unittest import TestCase

from PIL import Image

from photo_analyzer import PhotoAnalyzer
from utils import get_photo


class PhotoAnalyzerTestCase(TestCase):
    def test_that_uniform_image_returns_that_color(self):
        for color in [(0, 0, 0), (255, 255, 255), (255, 0, 0)]:
            img = Image.new(size=(100, 50), color=color, mode='RGB')
            avg_color = PhotoAnalyzer.determine_avg_color(img)
            self.assertTupleEqual(color, avg_color)

    def test_that_equal_rgb_image_returns_dark_grey(self):
        img = Image.new(size=(120, 40), mode='RGB')
        red_box = Image.new(size=(40, 40), color=(255, 0, 0), mode='RGB')
        green_box = Image.new(size=(40, 40), color=(0, 255, 0), mode='RGB')
        blue_box = Image.new(size=(40, 40), color=(0, 0, 255), mode='RGB')
        img.paste(red_box, (0, 0))
        img.paste(green_box, (40, 0))
        img.paste(blue_box, (80, 0))
        avg_color = PhotoAnalyzer.determine_avg_color(img)
        expected_avg_color = (85, 85, 85)
        self.assertTupleEqual(expected_avg_color, avg_color)

    def test_that_photo_returns_correct_color(self):
        avg_color = PhotoAnalyzer.determine_avg_color(get_photo('wolf'))
        expected_avg_color = (126, 109, 100)
        self.assertTupleEqual(expected_avg_color, avg_color)
