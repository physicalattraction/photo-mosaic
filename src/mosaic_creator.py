import random
from typing import List, Tuple

from PIL import Image

from photo import Photo
from photo_analyzer import PhotoAnalyzer
from type_hinting import Box, Color
from utils import Path


class MosaicCreator:
    """
    Class responsible for creating a mosaic in the shape of a given photo
    """

    photo: Photo
    pixels: List[Color]
    width: int
    height: int

    def __init__(self, filepath: str):
        """
        :param filepath: Path to the file with the photo to recreate
        """

        self.photo = Photo.open(filepath)
        self.pixels = list(self.photo.getdata())
        self.width, self.height = self.photo.size

    def pixelate(self, nr_pixels_in_x: int, nr_pixels_in_y: int) -> Photo:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its average color
        """

        result = Photo.new(mode='RGB', size=(self.width, self.height))
        for box in self._determine_boxes(nr_pixels_in_x, nr_pixels_in_y):
            sub_img = Photo(self.photo.crop(box))
            colored_box = Image.new(mode='RGB', size=sub_img.size, color=sub_img.avg_color)
            result.paste(colored_box, box=box)
        return result

    def photo_pixelate(self, src_dir: str, nr_pixels_in_x: int, nr_pixels_in_y: int) -> Photo:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its most matching photo
        """

        result = Photo.new(mode='RGB', size=(self.width, self.height))
        boxes = self._determine_boxes(nr_pixels_in_x, nr_pixels_in_y)
        analyzer = PhotoAnalyzer(src_dir, nr_photo_pixels=nr_pixels_in_x * nr_pixels_in_y)
        for box in boxes:
            sub_img = Photo(self.photo.crop(box))
            best_photo = analyzer.select_best_photo(sub_img.avg_color).resize(sub_img.size)
            best_photo = best_photo.convert('RGBA')
            colored_box = Image.new(mode='RGB', size=sub_img.size, color=sub_img.avg_color)
            mask = Image.new(mode='RGBA', size=sub_img.size, color=(0, 0, 0, 100))
            best_photo.paste(colored_box, mask=mask)
            result.paste(best_photo, box=box)
        return result

    def _determine_boxes(self, nr_pixels_in_x: int, nr_pixels_in_y: int) -> List[Box]:
        """
        Return a list of boxes representing the pixels, in a random order
        """

        boxes = []
        x_borders = self._determine_box_borders(self.width, nr_pixels_in_x)
        y_borders = self._determine_box_borders(self.height, nr_pixels_in_y)
        for x in x_borders:
            for y in y_borders:
                box = (x[0], y[0], x[1], y[1])
                boxes.append(box)

        return random.sample(boxes, len(boxes))

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
    c = MosaicCreator(Path.to_photo('wolf_high_res'))
    img = c.photo_pixelate(Path.to_src_dir('cats'), nr_pixels_in_x=40, nr_pixels_in_y=40)
    img.show()
