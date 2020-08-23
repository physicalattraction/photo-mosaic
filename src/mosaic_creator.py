from typing import List, Tuple

from PIL import Image

from photo import Photo
from photo_analyzer import PhotoAnalyzer
from type_hinting import Box, Color, Size
from utils import Path, permutation_multiple_lists


class MosaicCreator:
    """
    Class responsible for creating a mosaic in the shape of a given photo
    """

    DEFAULT_MAX_OUTPUT_SIZE = 4000  # The maximum width or height of the output photo

    original_photo: Photo  # The photo to create a mosaic of
    original_size: Size  # The size of the original photo
    pixels: List[Color]  # The pixel data of the original photo
    output_size: Size  # The size of the output mosaic

    def __init__(self, filepath: str, max_output_size: int = DEFAULT_MAX_OUTPUT_SIZE):
        """
        :param filepath: Path to the file with the photo to recreate
        """

        self.original_photo = Photo.open(filepath)
        self.original_size = self.original_photo.size
        self.pixels = list(self.original_photo.getdata())
        self.max_output_size = max_output_size
        self.output_size = self._determine_output_size()

    def pixelate(self, nr_pixels_in_x: int, nr_pixels_in_y: int) -> Photo:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its average color
        """

        result = Photo.new(mode='RGB', size=self.output_size)
        for original_box, output_box in self._get_boxes(nr_pixels_in_x, nr_pixels_in_y):
            sub_img = Photo(self.original_photo.crop(original_box))
            output_img_size = (output_box[2] - output_box[0], output_box[3] - output_box[1])
            colored_box = Image.new(mode='RGB', size=output_img_size, color=sub_img.avg_color)
            result.paste(colored_box, box=output_box)
        return result

    def photo_pixelate(self, src_dir: str, nr_pixels_in_x: int, nr_pixels_in_y: int) -> Photo:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its most matching photo
        """

        result = Photo.new(mode='RGB', size=self.output_size)
        analyzer = PhotoAnalyzer(src_dir, nr_photo_pixels=nr_pixels_in_x * nr_pixels_in_y)
        for original_box, output_box in self._get_boxes(nr_pixels_in_x, nr_pixels_in_y):
            sub_img = Photo(self.original_photo.crop(original_box))
            output_img_size = (output_box[2]-output_box[0], output_box[3] - output_box[1])
            best_photo = analyzer.select_best_photo(sub_img.avg_color, desired_size=output_img_size)
            best_photo = best_photo.convert('RGBA')
            colored_box = Image.new(mode='RGB', size=best_photo.size, color=sub_img.avg_color)
            mask = Image.new(mode='RGBA', size=best_photo.size, color=(0, 0, 0, 100))
            best_photo.paste(colored_box, mask=mask)
            result.paste(best_photo, box=output_box)
        return result

    def _determine_output_size(self) -> Size:
        """
        Based on the size of the photo to recreate and the MAX_SIZE of the output,
        determine the size with the same aspect ratio as the target photo.
        """

        width, height = self.original_size
        factor = min(self.max_output_size / width, self.max_output_size / height)
        return round(factor * width), round(factor * height)

    def _get_boxes(self, nr_boxes_in_x: int, nr_boxes_in_y: int) -> List[Tuple[Box, Box]]:
        original_boxes = self._determine_boxes(*self.original_size, nr_boxes_in_x, nr_boxes_in_y)
        output_boxes = self._determine_boxes(*self.output_size, nr_boxes_in_x, nr_boxes_in_y)
        return permutation_multiple_lists(original_boxes, output_boxes)

    @staticmethod
    def _determine_boxes(width, height, nr_boxes_in_x: int, nr_boxes_in_y: int) -> List[Box]:
        """
        Return a list of boxes, splitting up a rectangle in the given number of boxes horizontally and vertically
        """

        boxes = []
        x_borders = MosaicCreator._determine_box_borders(width, nr_boxes_in_x)
        y_borders = MosaicCreator._determine_box_borders(height, nr_boxes_in_y)
        for x in x_borders:
            for y in y_borders:
                box = (x[0], y[0], x[1], y[1])
                boxes.append(box)
        return boxes

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
            (round(nr_pixels_per_box * index), round(nr_pixels_per_box * (index + 1)))
            for index in range(nr_boxes)
        ]


if __name__ == '__main__':
    c = MosaicCreator(Path.to_photo('wolf_high_res'), max_output_size=774)
    img = c.photo_pixelate(Path.to_src_dir('cats'), nr_pixels_in_x=40, nr_pixels_in_y=40)
    img.show()
    img.save('wolf_photo_pixelated.jpg')
