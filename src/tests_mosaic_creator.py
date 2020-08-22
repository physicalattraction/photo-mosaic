from unittest import TestCase

from mosaic_creator import MosaicCreator
from utils import ImageComparingMixin, get_photo


class MosaicCreatorTestCase(ImageComparingMixin, TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.creator = MosaicCreator(get_photo('wolf'))

    # Public methods

    def test_that_pixelate_returns_pixelated_photo(self):
        pixelated_wolf = self.creator.pixelate(nr_pixels_in_x=50, nr_pixels_in_y=35)
        # Expected image is a bitmap, to prevent jpeg artefacts in comparison
        expected_pixelated_wolf = get_photo('wolf_pixelated_50_35.bmp')
        self.assertImageEqual(expected_pixelated_wolf, pixelated_wolf)

    # Helper methods

    def test_that_determine_box_borders_returns_correct_borders(self):
        box_borders = MosaicCreator._determine_box_borders(total_nr_pixels=774, nr_boxes=10)
        expected_box_borders = [(0, 77), (77, 155), (155, 232), (232, 310), (310, 387),
                                (387, 464), (464, 542), (542, 619), (619, 697), (697, 774)]
        self.assertListEqual(expected_box_borders, box_borders)
