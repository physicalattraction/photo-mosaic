from typing import List, Tuple

from PIL import Image

from photo_analyzer import PhotoAnalyzer
from utils import get_photo


class MosaicCreator:
    """
    Class responsible for creating a mosaic in the shape of a given photo
    """

    def __init__(self, img: Image.Image):
        """
        :param img: The photo to recreate
        """

        self.img = img
        self.pixels = list(img.getdata())
        self.width, self.height = img.size

    def pixelate(self, nr_pixels_in_x: int, nr_pixels_in_y: int) -> Image.Image:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its average color
        """

        result = Image.new(mode='RGB', size=(self.width, self.height))
        x_borders = self._determine_box_borders(self.width, nr_pixels_in_x)
        y_borders = self._determine_box_borders(self.height, nr_pixels_in_y)
        for x in x_borders:
            for y in y_borders:
                box = (x[0], y[0], x[1], y[1])
                sub_img = self.img.crop(box)
                avg_color = PhotoAnalyzer.determine_avg_color(sub_img)
                colored_box = Image.new(mode='RGB', size=sub_img.size, color=avg_color)
                result.paste(colored_box, box=box)
        return result

    @staticmethod
    def _determine_box_borders(total_nr_pixels: int, nr_boxes: int) -> List[Tuple[int, int]]:
        """
        Return the borders per box for the given number of boxes

        :param total_nr_pixels: Total number of pixels to distribute
        :param nr_boxes: Total number of boxes to distribute over
        :return: List of tuples containing the box borders, e.g.
                [(0, 77), (77, 155), (155, 232), (232, 310), (310, 387),
                 (387, 464), (464, 542), (542, 619), (619, 697), (697, 774)]
        """

        nr_pixels_per_box: float = total_nr_pixels / nr_boxes
        return [
            (int(round(nr_pixels_per_box * index)), int(round(nr_pixels_per_box * (index + 1))))
            for index in range(nr_boxes)
        ]


if __name__ == '__main__':
    mc = MosaicCreator(get_photo('wolf'))
    mc.pixelate(50, 35)
