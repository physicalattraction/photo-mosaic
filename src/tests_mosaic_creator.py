import random
from unittest import TestCase

from mosaic_creator import MosaicCreator
from photo import Photo
from utils import Path


class MosaicCreatorTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.creator = MosaicCreator(Path.to_photo('wolf_high_res'))

    # Public methods

    def test_that_pixelate_returns_pixelated_photo(self):
        pixelated_wolf = self.creator.pixelate(nr_pixels_in_x=50, nr_pixels_in_y=35)
        # Expected image is a bitmap, to prevent jpeg artefacts in comparison
        expected_pixelated_wolf = Photo.open(Path.to_photo('wolf_pixelated_50_35.bmp'))
        self.assertEqual(expected_pixelated_wolf, pixelated_wolf)

    # Private methods

    def test_that_determine_boxes_returns_correct_boxes(self):
        self.assertEqual(774, self.creator.width)
        self.assertEqual(774, self.creator.height)
        random.seed(654)  # With this seed, the ordering of boxes is reversed from the original input before randomizing
        boxes = self.creator._determine_boxes(nr_pixels_in_x=2, nr_pixels_in_y=3)
        expected_boxes = [(387, 516, 774, 774), (387, 258, 774, 516), (387, 0, 774, 258),
                          (0, 516, 387, 774), (0, 258, 387, 516), (0, 0, 387, 258)]
        self.assertListEqual(expected_boxes, boxes)

    def test_that_determine_box_borders_returns_correct_borders(self):
        box_borders = MosaicCreator._determine_box_borders(total_nr_pixels=774, nr_boxes=10)
        expected_box_borders = [(0, 77), (77, 155), (155, 232), (232, 310), (310, 387),
                                (387, 464), (464, 542), (542, 619), (619, 697), (697, 774)]
        self.assertListEqual(expected_box_borders, box_borders)
