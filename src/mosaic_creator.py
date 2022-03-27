import os.path
from typing import List, Tuple

from PIL import Image

from photo import Photo
from photo_analyzer import PhotoAnalyzer
from utils.type_hinting import Box, Color, Size, size_as_string
from utils.list_utils import permutation_multiple_lists
from utils.path import Path


class MosaicCreator:
    """
    Class responsible for creating a mosaic in the shape of a given photo
    """

    DEFAULT_MAX_OUTPUT_SIZE = 4000  # The maximum width or height of the output photo
    DEFAULT_CHEAT_PARAMETER = 150

    original_photo: Photo  # The photo to create a mosaic of
    original_size: Size  # The size of the original photo
    pixels: List[Color]  # The pixel data of the original photo
    output_size: Size  # The size of the output mosaic

    def __init__(self, filepath: str,
                 nr_pixels_in_x: int, nr_pixels_in_y: int,
                 max_output_size: int = DEFAULT_MAX_OUTPUT_SIZE,
                 cheat_parameter: int = DEFAULT_CHEAT_PARAMETER):
        """
        :param filepath: Path to the file with the photo to recreate
        :param max_output_size: Maximum width or height of the output image
        :param cheat_parameter: Value between 0 (no cheat) and 255 (full cheat)
                                to additionally color the photos in the original pixel's color
        """

        assert 0 <= cheat_parameter <= 255

        self.original_photo = Photo.open(filepath)
        self.original_size = self.original_photo.size
        self.pixels = list(self.original_photo.getdata())
        self.max_output_size = max_output_size
        self.cheat_parameter = cheat_parameter
        self.nr_pixels_in_x = nr_pixels_in_x
        self.nr_pixels_in_y = nr_pixels_in_y
        self.output_size = self._determine_output_size()

    def pixelate(self, nr_pixels_in_x: int, nr_pixels_in_y: int) -> Photo:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its average color
        """

        # TODO: Instead of calculating the average color of a box, resize the source image
        #       to the amount of pixels you need, then this resizing takes care of calculating
        #       the average color. The result is not identical, but you can't say with the
        #       human eye which one is better. We now do resize the original photo, but we
        #       didn't remove the calculation yet and just take the one pixel value.
        self.original_size = (nr_pixels_in_x, nr_pixels_in_y)
        self.original_photo = self.original_photo.resize(self.original_size)

        result = Photo.new(mode='RGB', size=self.output_size)
        for original_box, output_box in self._get_boxes(nr_pixels_in_x, nr_pixels_in_y):
            print(original_box)
            sub_img = Photo(self.original_photo.crop(original_box))
            output_img_size = (output_box[2] - output_box[0], output_box[3] - output_box[1])
            colored_box = Image.new(mode='RGB', size=output_img_size, color=sub_img.avg_color)
            result.paste(colored_box, box=output_box)
        return result

    def photo_pixelate(self, src_dir: str) -> Photo:
        """
        Pixelate the given photo by chopping it up in rectangles, and replace every square by its most matching photo
        """

        result = Photo.new(mode='RGB', size=self.output_size)
        subimg_size = (int(self.output_size[0] / self.nr_pixels_in_x), int(self.output_size[1] / self.nr_pixels_in_y))
        analyzer = PhotoAnalyzer(src_dir, nr_photo_pixels=self.nr_pixels_in_x * self.nr_pixels_in_y,
                                 tile_size=subimg_size)
        for original_box, output_box in self._get_boxes(self.nr_pixels_in_x, self.nr_pixels_in_y):
            sub_img = Photo(self.original_photo.crop(original_box))
            best_photo = analyzer.select_best_photo(sub_img.avg_color)
            best_photo = best_photo.convert('RGBA')
            colored_box = Image.new(mode='RGB', size=best_photo._size, color=sub_img.avg_color)
            mask = Image.new(mode='RGBA', size=best_photo._size, color=(0, 0, 0, self.cheat_parameter))
            best_photo.paste(colored_box, mask=mask)
            result.paste(best_photo, box=output_box)
        return result

    def _determine_output_size(self) -> Size:
        """
        Based on the size of the photo to recreate and the MAX_SIZE of the output,
        determine the size with the same aspect ratio as the target photo.

        Also make sure that the amount of pixels is a multiple of nr_pixels_in_x and in_y,
        such that each subimage is identical in size.
        """

        width, height = self.original_size
        factor = min(self.max_output_size / width, self.max_output_size / height)
        new_width = round(factor * width / self.nr_pixels_in_x) * self.nr_pixels_in_x
        new_height = round(factor * height / self.nr_pixels_in_y) * self.nr_pixels_in_y
        return new_width, new_height

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
    _max_output_size = 1000
    _cheat_parameter = 25
    _nr_pixels_in_x = 40
    _nr_pixels_in_y = 40

    c = MosaicCreator(Path.to_photo('wolf_high_res'), cheat_parameter=_cheat_parameter,
                      max_output_size=_max_output_size, nr_pixels_in_x=_nr_pixels_in_x, nr_pixels_in_y=_nr_pixels_in_y)
    img = c.photo_pixelate(Path.to_src_photos_dir('cats'))
    output_filename = f'wolf_photo_pixelated_{_max_output_size}px_c{_cheat_parameter}_{_nr_pixels_in_x}x{_nr_pixels_in_y}.jpg'
    output_fp = os.path.join(Path.to_src_photos_dir('cats'), output_filename)
    img.save(output_fp)

    # max_output_size = 12500
    # src_photo = 'papmam1'
    # c = MosaicCreator(Path.to_photo(src_photo), max_output_size=max_output_size, cheat_parameter=_cheat_parameter)
    # # img = c.pixelate(nr_pixels_in_x=18, nr_pixels_in_y=24)
    # src_photos_dir = os.path.join('pap', 'mosaic')
    # # TODO: Write a method that calculates this desired ratio automatically, instead of using Excel like I did now.
    # # TODO: Combine the Collector and the MosaicCreator to resize images and precalculate and reuse average colors.
    # img = c.photo_pixelate(Path.to_src_photos_dir(src_photos_dir), nr_pixels_in_x=50, nr_pixels_in_y=50)
    # img.show()
    # img.save(Path.to_photo(f'{src_photo}_photo_pixelated_{max_output_size}_{_cheat_parameter}'))
