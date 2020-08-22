import os.path
from statistics import mean

from PIL import Image

from type_hinting import Color


class PhotoAnalyzer:
    """
    Class responsible for determining the average color of a photo
    """

    @staticmethod
    def determine_avg_color(img: Image.Image) -> Color:
        """
        Determine the average color of a photo

        :param img: Image to analyze
        :return: Three-tuple of the RGB value of the average color
        """

        pixels = list(img.getdata())
        return tuple(int(round(mean([pixel[channel] for pixel in pixels])))
                     for channel in (0, 1, 2))
