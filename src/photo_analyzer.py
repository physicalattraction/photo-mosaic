import math
import os.path
from typing import Dict, Optional

from photo import Photo
from type_hinting import Color


class PhotoAnalyzer:
    """
    Class responsible for determining which photo to pick to create a mosaic, based on average color
    """

    _photos: Optional[Dict[str, Photo]]

    def __init__(self, src_dir: str):
        self.src_dir = src_dir
        self._photos = None

    @property
    def photos(self) -> Dict[str, Photo]:
        if not self._photos:
            self._photos = {
                filename: Photo.open(os.path.join(self.src_dir, filename))
                for filename in sorted(os.listdir(self.src_dir))
            }
        return self._photos

    def select_best_photo(self, color: Color) -> Photo:
        """
        Select the photo that most closely matches the input color
        """

        return NotImplemented()

    @staticmethod
    def _distance(color_1: Color, color_2: Color) -> float:
        """
        Return the distance between two colors

        The distance is defined as the square of the 2-norm. Rationale: the s-norm penalizes
        large differences in a single channel, which for human eyes are less alike.
        Example: (128, 128, 128) looks more like (127, 127, 127) than (130, 127, 127) does.
        """

        quadratic_errors = (math.pow((color_1[index] - color_2[index]), 2) for index in range(3))
        return math.sqrt(sum(quadratic_errors))
